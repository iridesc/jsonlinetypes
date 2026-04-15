# JsonLineTypes 项目实现原理详解

## 项目概述

**JsonLineTypes** 是一个基于 JSONL (JSON Lines) 文件格式的键值对和列表数据结构，用于处理不适合放入内存的大数据集。

### 核心思想

将 Python 的 `dict` 和 `list` 的数据存储在磁盘上的 JSONL 文件中，而不是 RAM 中，从而支持任意大小的数据集（仅受磁盘空间限制）。

---

## 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      用户代码                              │
│                     (Python 脚本)                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              JLFDict / JLFList 接口层                     │
│        继承自 MutableMapping / MutableSequence             │
│                    (API 接口)                               │
├─────────────────────────────────────────────────────────────┤
│                   索引管理层                               │
│  • _key_to_offset (字典索引)                             │
│  • _index_to_offset (列表索引)                           │
│  • _deleted_keys / _deleted_indexes (删除标记)            │
│  • threading.RLock (线程锁)                              │
├─────────────────────────────────────────────────────────────┤
│                   文件存储层                               │
│  • data.jsonl (主数据文件，JSONL 格式)                   │
│  • data.jsonl.idx (索引文件，Pickle 格式)               │
│  • data.jsonl.idx.del (删除标记索引，可选)               │
├─────────────────────────────────────────────────────────────┤
│                   底层存储                                 │
│              磁盘文件系统                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. JSONL 格式

### 什么是 JSONL？

**JSONL (JSON Lines)** 是一种简单但强大的文本格式，每行都是一个独立的 JSON 对象。

```
{"id": 1, "name": "Alice", "age": 30}
{"id": 2, "name": "Bob", "age": 25}
{"id": 3, "name": "Charlie", "age": 35}
```

### 为什么选择 JSONL？

| 特性 | JSONL | 普通 JSON |
|------|-------|-----------|
| 流式处理 | ✅ 支持 | ❌ 需要完整解析 |
| 内存效率 | ✅ 逐行读取（O(1)） | ❌ 需要全部加载 |
| 可读性 | ✅ 人类可读 | ✅ 人类可读 |
| 追加写入 | ✅ 支持（追加行） | ❌ 需要重写 |
| 大文件 | ✅ 可以处理 GB 级 | ❌ 受限于 RAM |
| 部分更新 | ✅ 可以追加新记录 | ❌ 需要重写文件 |

---

## 2. JLFDict 实现原理

### 核心数据结构

```python
class JLFDict:
    def __init__(self, file_path, key_field):
        self.file_path = file_path      # JSONL 文件路径
        self.key_field = key_field        # 用作键的字段名
        self.index_path = file_path + ".idx"  # 索引文件

        # 核心索引（内存中）
        self._key_to_offset = {}        # key -> 文件偏移量（字节）
        self._deleted_keys = set()      # 已删除的 key 集合

        # 线程安全
        self._lock = threading.RLock()  # 可重入锁
```

### 2.1 索引机制

**索引是 JLF 性能的关键！**

```python
# 索引示例
_key_to_offset = {
    "user1": 0,      # user1 的数据在文件第 0 字节开始
    "user2": 89,     # user2 的数据在文件第 89 字节开始
    "user3": 178     # user3 的数据在文件第 178 字节开始
}
```

**工作流程：**

1. **启动时** - 加载或重建索引
   ```python
   # 方式 1: 从索引文件加载（快）
   if os.path.exists("data.jsonl.idx"):
       with open("data.jsonl.idx", "rb") as f:
           _key_to_offset = pickle.load(f)  # ~100 字节/key

   # 方式 2: 扫描 JSONL 文件重建（慢但可靠）
   else:
       for offset, line in enumerate(file):
           data = json.loads(line)
           key = data[key_field]
           _key_to_offset[key] = offset
   ```

2. **读取时** - O(1) 查找
   ```python
   def __getitem__(self, key):
       # 步骤 1: 查找偏移量（O(1)）
       offset = _key_to_offset[key]

       # 步骤 2: 跳转到文件位置
       f.seek(offset)

       # 步骤 3: 读取一行 JSON 并解析
       line = f.readline()
       return json.loads(line)
   ```

**索引优势：**
- 🚀 只在内存中保存索引，不保存数据
- 📊 100万条记录仅需 ~100MB RAM
- 💾 500MB 数据只需 ~100MB 索引

### 2.2 追加写入策略

**核心创新：只追加，不修改已有数据**

```python
def __setitem__(self, key, value):
    # 首次写入
    if key not in _key_to_offset:
        # 直接追加到文件末尾
        append_to_file(key, value)
        # 更新索引
        _key_to_offset[key] = current_file_offset

    # 更新已有 key
    else:
        # 步骤 1: 追加删除标记
        append_to_file({key_field: key, "_deleted": True})

        # 步骤 2: 追加新值
        append_to_file(value)

        # 步骤 3: 更新索引指向新值
        _key_to_offset[key] = new_offset
```

**追加写入的文件变化：**

```
初始状态（写入 3 条）:
{"id": 1, "name": "Alice"}
{"id": 2, "name": "Bob"}
{"id": 3, "name": "Charlie"}

更新 user2 的情况:
{"id": 1, "name": "Alice"}
{"id": 2, "name": "Bob"}  ← 旧数据，被标记删除
{"id": 3, "name": "Charlie"}
{"id": 2, "_deleted": true}  ← 删除标记
{"id": 2, "name": "Bob Smith"}  ← 新数据

索引更新:
_key_to_offset = {
    "user1": 0,      # 不变
    "user2": 210,    # 指向新数据（文件末尾）
    "user3": 178     # 不变
}
```

**为什么这样做？**
- ✅ 文件追加速度快（不需要查找插入位置）
- ✅ 不需要移动已有数据
- ✅ 操作原子性更好
- ⚠️ 缺点：文件会变大（需要 compact）

### 2.3 删除策略

**软删除 + 删除标记**

```python
def __delitem__(self, key):
    # 步骤 1: 追加删除标记
    append_to_file({key_field: key, "_deleted": True})

    # 步骤 2: 更新内存索引
    _deleted_keys.add(key)      # 标记为已删除
    del _key_to_offset[key]     # 从索引中移除
```

**删除后的文件：**

```
{"id": 1, "name": "Alice"}
{"id": 2, "name": "Bob"}  ← 要删除
{"id": 3, "name": "Charlie"}
{"id": 2, "_deleted": true}  ← 追加的删除标记
```

**读取时的检查：**
```python
def __getitem__(self, key):
    if key in _deleted_keys:      # 快速检查（O(1)）
        raise KeyError(key)
    # ... 继续读取
```

### 2.4 Compact 压缩

**清理"垃圾"数据，恢复磁盘空间**

```python
def compact(self):
    # 创建临时文件
    temp_path = file_path + ".tmp"

    # 只复制未被删除的记录
    with open(file_path, "rb") as src:
        with open(temp_path, "wb") as dst:
            for line in src:
                data = json.loads(line)
                if not data.get('_deleted'):  # 跳过已删除
                    dst.write(line)  # 复制有效数据

    # 原子性替换
    os.replace(temp_path, file_path)

    # 重建索引（所有记录重新编号）
    _build_index()
```

**Compact 效果：**

```
Compact 前（10 行，包含删除标记）:
{"id": 1, "name": "Alice"}
{"id": 2, "name": "Bob"}
{"id": 3, "name": "Charlie"}
{"id": 1, "_deleted": true}
{"id": 1, "name": "Alice2"}
{"id": 2, "_deleted": true"}
{"id": 3, "_deleted": true"}
{"id": 3, "name": "Charlie2"}
{"id": 1, "_deleted": true}
{"id": 1, "name": "Alice3"}

Compact 后（3 行，仅保留最新有效数据）:
{"id": 1, "name": "Alice3"}
{"id": 2, "name": "Bob"}
{"id": 3, "name": "Charlie2"}
```

**何时调用 compact？**
- 大量删除/更新操作后
- 文件变得很大时
- 定期维护（如每天/每周）

---

## 3. JLFList 实现原理

### 核心数据结构

```python
class JLFList:
    def __init__(self, file_path):
        self._index_to_offset = {}     # 原始索引 -> 文件偏移
        self._active_indices = []       # 逻辑索引列表
        self._deleted_indexes = set()   # 已删除索引集合
        self._next_index = 0            # 下一个可用索引
```

### 3.1 索引映射

**逻辑索引 vs 原始索引：**

```python
# 文件中的数据（可能包含删除标记）
[
    {"_index": 0, "value": "A"},     # 逻辑索引 0
    {"_index": 1, "value": "B", "_deleted": true},  # 已删除
    {"_index": 2, "value": "C"},     # 逻辑索引 1
    {"_index": 3, "value": "D", "_deleted": true},  # 已删除
    {"_index": 4, "value": "E"}      # 逻辑索引 2
]

# 内存中的映射
_active_indices = [0, 2, 4]  # 有效的原始索引列表
_deleted_indexes = {1, 3}  # 已删除的原始索引

# 逻辑索引操作
lst[0]  → _active_indices[0] = 0  → 读取原始索引 0
lst[1]  → _active_indices[1] = 2  → 读取原始索引 2
lst[2]  → _active_indices[2] = 4  → 读取原始索引 4
```

### 3.2 追加操作

```python
def append(self, value):
    # 分配新的原始索引
    index = _next_index
    _next_index += 1

    # 追加到文件
    append_to_file({"_index": index, "value": value})

    # 更新索引
    _index_to_offset[index] = new_offset
    _active_indices.append(index)  # 添加到有效列表
```

### 3.3 删除操作

```python
def __delitem__(self, logical_index):
    # 步骤 1: 转换逻辑索引为原始索引
    original_index = _active_indices[logical_index]

    # 步骤 2: 追加删除标记
    append_to_file({"_index": original_index, "_deleted": True})

    # 步骤 3: 更新索引
    _active_indices.remove(original_index)  # 从有效列表移除
    _deleted_indexes.add(original_index)    # 添加到删除集合
```

### 3.4 修改操作

```python
def __setitem__(self, logical_index, value):
    # 步骤 1: 转换逻辑索引为原始索引
    original_index = _active_indices[logical_index]

    # 步骤 2: 追加删除标记
    append_to_file({"_index": original_index, "_deleted": true})

    # 步骤 3: 追加新值（使用相同原始索引）
    append_to_file({"_index": original_index, "value": value})

    # 步骤 4: 更新索引（指向新数据）
    _index_to_offset[original_index] = new_offset
```

---

## 4. 线程安全实现

### 核心机制：RLock

```python
class JLFDict:
    def __init__(self, ...):
        self._lock = threading.RLock()  # 可重入锁

    def __getitem__(self, key):
        with self._lock:  # 自动获取和释放锁
            offset = _key_to_offset[key]

        with open(file_path, "rb") as f:
            f.seek(offset)
            return json.loads(f.readline())

    def __setitem__(self, key, value):
        with self._lock:
            # 更新内存索引（需要锁）
            _key_to_offset[key] = new_offset

        # 文件写入（部分不加锁以减少竞争）
        with open(file_path, "ab") as f:
            f.write(data)
```

### 批量操作优化

```python
# 方式 1: 每个操作都加锁（慢）
for i in range(1000):
    d[f"key_{i}"] = value  # 1000 次锁操作

# 方式 2: 批量操作只加锁一次（快）
with d:  # 只获取一次锁
    for i in range(1000):
        d[f"key_{i}"] = value  # 在锁的保护下操作
# 离开 with 时自动释放锁
```

### RLock 的优势

```python
# RLock (可重入锁)
d = JLFDict("data.jsonl", "id")

def function_a():
    with d:  # 获取锁
        function_b()  # 可以嵌套调用

def function_b():
    with d:  # ✅ RLock 允许同一线程重复获取锁
        d["key"] = value
```

---

## 5. 索引持久化

为什么需要持久化索引？

### 重建索引 vs 加载索引

| 方式 | 启动时间 | 说明 |
|------|---------|------|
| **加载索引** | 几毫秒 | 直接从 .idx 文件加载 |
| **重建索引** | 几到几十秒 | 扫描整个 JSONL 文件 |

### 索引文件格式

```python
# JLFDict 索引文件（.idx）
_key_to_offset = {
    "user1": 0,
    "user2": 89,
    "user3": 178
}

# 删除标记索引（.idx.del）
_deleted_keys = {"user2", "user5"}

# JLFList 索引文件（.idx）
{
    "offsets": {0: 0, 2: 178, 4: 356},
    "active": [0, 2, 4],
    "deleted": {1, 3},
    "next_index": 5
}
```

### 自动保存

```python
def __init__(self, ..., auto_save_index=True):
    self._auto_save_index = auto_save_index

    if auto_save_index:
        save_index()  # 启动后保存
```

---

## 6. 数据恢复机制

### 索引损坏怎么办？

**答案：从 JSONL 文件重建索引！**

```python
def _build_index(self):
    # 步骤 1: 扫描整个文件
    records = []
    with open(file_path, "rb") as f:
        offset = f.tell()
        line = f.readline()
        while line:
            data = json.loads(line)
            key = data[key_field]
            records.append((offset, data, key))
            offset = f.tell()
            line = f.readline()

    # 步骤 2: 只保留每个 key 的最后一个记录
    latest_records = {}
    for offset, data, key in records:
        if key not in latest_records or offset > latest_records[key][0]:
            latest_records[key] = (offset, data)

    # 步骤 3: 检查删除标记
    for key, (offset, data) in latest_records.items():
        if data.get('_deleted'):
            _deleted_keys.add(key)
        else:
            _key_to_offset[key] = offset
```

**重建过程示例：**

```
JSONL 文件内容:
{"id": 1, "name": "Alice"}           ← 原始
{"id": 1, "name": "Alice2"}          ← 更新
{"id": 1, "_deleted": true}         ← 删除
{"id": 1, "name": "Alice3"}          ← 恢复
{"id": 2, "name": "Bob"}

重建后索引:
_key_to_offset = {
    1: 指向 "Alice3" (最后一个非删除记录),
    2: 指向 "Bob"
}

_deleted_keys = {
    # 空，因为 key=1 的最后一个记录是有效的
}
```

---

## 7. 性能优化技术

### 7.1 文件偏移量索引

**问题：** 如何快速找到文件中的特定记录？

**解决：** 使用文件偏移量（字节位置）

```python
# 不直接搜索文本
with open("data.jsonl", "r") as f:
    for line in f:
        if line.find('"id": 2') != -1:  # 慢！
            return json.loads(line)

# 使用偏移量快速跳转
offset = _key_to_offset[2]  # 例如: 89 字节
with open("data.jsonl", "rb") as f:
    f.seek(offset)          # 直接跳到第 89 字节
    return json.loads(f.readline())  # 快！
```

**性能对比：**
- 搜索方式：O(n) 需要扫描文件
- 索引方式：O(1) 直接跳转

### 7.2 延迟读取

**核心思想：** 只读取需要的数据

```python
# 只有一个 key 时
value = d["user1"]  # 只读取这一条记录

# 而不是加载所有数据
all_data = json.load(file)  # ❌ 慢，占用大量 RAM
```

### 7.3 批量操作

减少锁的获取次数

```python
# ❌ 每个操作都加锁
for i in range(1000):
    d[f"key_{i}"] = value  # 1000 次锁操作

# ✅ 批量操作只加锁一次
with d:
    for i in range(1000):
        d[f"key_{i}"] = value  # 1 次锁操作
```

---

## 8. 关键设计决策

### 8.1 为什么用 JSONL 而不是普通 JSON？

| 特性 | JSONL | JSON |
|------|-------|------|
| 大文件处理 | ✅ 逐行处理 | ❌ 需要全部加载 |
| 内存占用 | ✅ O(1) 每条记录 | ❌ O(n) 全部数据 |
| 追加写入 | ✅ 可以 | ❌ 需要重写 |
| 可读性 | ✅ 人类可读 | ✅ 人类可读 |
| 流式处理 | ✅ 支持 | ❌ 不支持 |

### 8.2 为什么用追加写入？

**传统方式的问题：**
```
在中间插入数据需要移动所有后续数据：
[A, B, C, D]  插入 X 到位置 1
[A, X, B, C, D]  需要移动 B, C, D
```

**追加写入的优势：**
```
[A, B, C, D]  更新 B
[A, B, C, D, B(del), X]  只需追加，不移动数据
快速、简单、原子性
```

### 8.3 为什么需要 Compact？

**问题：** 追加写入会产生"垃圾"数据

```
文件增长：
第 1 次写入: 1 KB (10 条记录)
第 100 次更新: 100 KB (100 条新记录 + 100 条删除标记)
第 1000 次更新: 1 MB (大量删除标记)

最终有效数据: 10 KB (但文件是 1 MB)
```

**Compact 解决方案：**
```
Compact 前:
[数据, 数据, 删除标记, 数据, 删除标记, ...]  1 MB
└─ 有效数据: 10 KB

Compact 后:
[数据, 数据, 数据]  10 KB
```

---

## 9. 完整工作流程示例

### 场景：用户管理系统

```python
from jsonlinetypes import JLFDict

# 1. 初始化（创建索引）
users = JLFDict("users.jsonl", "user_id")

# 文件结构
# users.jsonl: (空)
# users.jsonl.idx: {}

# 2. 写入用户数据
users[1] = {"user_id": 1, "name": "Alice", "age": 30}
users[2] = {"user_id": 2, "name": "Bob", "age": 25}
users[3] = {"user_id": 3, "name": "Charlie", "age": 35}

# 文件内容
# users.jsonl:
# {"user_id": 1, "name": "Alice", "age": 30}
# {"user_id": 2, "name": "Bob", "age": 25}
# {"user_id": 3, "name": "Charlie", "age": 35}

# users.jsonl.idx:
# {1: 0, 2: 89, 3: 178}

# 3. 更新用户
users[1] = {"user_id": 1, "name": "Alice Smith", "age": 31}

# 文件内容（追加）
# users.jsonl:
# {"user_id": 1, "name": "Alice", "age": 30}
# {"user_id": 2, "name": "Bob", "age": 25}
# {"user_id": 3, "name": "Charlie", "age": 35}
# {"user_id": 1, "_deleted": True}  ← 删除标记
# {"user_id": 1, "name": "Alice Smith", "age": 31}  ← 新数据

# users.jsonl.idx:
# {1: 268, 2: 89, 3: 178}  ← 索引更新，指向新数据

# 4. 删除用户
del users[2]

# 文件内容（追加）
# users.jsonl:
# ...
# {"user_id": 1, "name": "Alice Smith", "age": 31}
# {"user_id": 2, "_deleted": true}  ← 删除标记

# users.jsonl.idx:
# {1: 268, 3: 178}  ← 索引移除
# users.jsonl.idx.del:
# {2}  ← 删除标记集合

# 5. 读取用户（使用索引）
alice = users[1]
# 步骤 1: 查找偏移量 _key_to_offset[1] = 268
# 步骤 2: f.seek(268) 跳转到文件位置
# 步骤 3: f.readline() 读取一行
# 步骤 4: json.loads() 解析
# 结果: {"user_id": 1, "name": "Alice Smith", "age": 31}

# 6. 迭代用户
for user_id, user in users.items():
    # 使用索引快速遍历
    # 从 _key_to_offset 中排除 _deleted_keys 中的 key
    pass

# 7. Compact（清理垃圾数据）
users.compact()

# Compact 后文件内容
# users.jsonl:
# {"user_id": 1, "name": "Alice Smith", "age": 31}
# {"user_id": 3, "name": "Charlie", "age": 35}

# 重建索引
# users.jsonl.idx:
# {1: 0, 3: 89}  ← 偏移量重新计算
```

---

## 10. 性能分析

### 时间复杂度

| 操作 | 时间复杂度 | 说明 |
|------|-----------|------|
| **读取** | O(1) | 使用索引直接跳转 |
| **写入** | O(1) | 追加到文件末尾 |
| **更新** | O(1) | 追加删除标记 + 新数据 |
| **删除** | O(1) | 追加删除标记 |
| **迭代** | O(n) | 遍历所有键 |
| **Compact** | O(n) | 重写整个文件 |

### 空间复杂度

| 数据类型 | 空间复杂度 | 说明 |
|---------|-----------|------|
| **内存占用** | O(n) | 只保存索引，~100 字节/记录 |
| **磁盘占用** | O(n) | 实际数据大小 + 删除标记 |
| **索引大小** | O(n) | ~100 字节 × 记录数 |

### 实际数据示例

```
数据集: 100 万条记录
单条记录: 500 字节

总数据大小: 500 MB
索引内存占用: 100 MB

对比全加载到内存:
  全加载方式: 需要 500 MB RAM
  JsonLineTypes: 只需 100 MB RAM
  节省: 80% 内存
```

---

## 11. 与其他数据结构的对比

### 对比列表

| 特性 | Python list | JLFList |
|------|-------------|----------|
| 内存 | 全部在 RAM | 索引在 RAM，数据在磁盘 |
| 最大大小 | 受限 RAM | 受限磁盘 |
| 插入 | O(n) 移动数据 | ❌ 不支持 |
| 追加 | O(1) 扩容 | O(1) 写入磁盘 |
| 删除 | O(n) 移动数据 | O(1) 追加标记 |
| 持久化 | 手动 | 自动 |

### 对比字典

| 特性 | Python dict | JLFDict |
|------|-------------|----------|
| 内存 | 全部在 RAM | 索引在 RAM，数据在磁盘 |
| 最大大小 | 受限 RAM | 受限磁盘 |
| 插入 | O(1) | O(1) 写入磁盘 |
| 更新 | O(1) | O(1) 追加标记 |
| 删除 | O(1) | O(1) 追加标记 |
| 持久化 | 手动 | 自动 |

---

## 12. 关键创新点

### 1. 文件偏移量索引

**传统方式：** 存储键值对应关系
```python
# ❌ 传统方式
{"user1": {"name": "Alice", "age": 30}, ...}  # 全部在内存
```

**JsonLineTypes 方式：** 存储键到文件偏移量的映射
```python
# ✅ JsonLineTypes
_key_to_offset = {"user1": 0, "user2": 89, ...}  # 只保存位置
```

### 2. 追加写入 + 软删除

**传统方式：** 修改原位数据
```python
# ❌ 传统方式（需要移动数据）
data = load(file)
data["user1"] = new_value
save(data)  # 重写整个文件
```

**JsonLineTypes 方式：** 追加新数据
```python
# ✅ JsonLineTypes
append({"user_id": 1, "_deleted": true})  # 标记旧数据
append({"user_id": 1, "name": "New Alice"})   # 追加新数据
```

### 3. 延迟读取 + 索引持久化

**传统方式：** 加载全部数据
```python
# ❌ 传统方式
data = json.load(file)  # 全部加载到 RAM
print(data["user1"])
```

**JsonLineTypes 方式：** 只读取需要的数据
```python
# ✅ JsonLineTypes
offset = _key_to_offset["user1"]  # 只加载索引
f.seek(offset)  # 只读取这一条
data = json.loads(f.readline())
```

---

## 13. 关键技术细节

### 13.1 锁的粒度控制

```python
def __setitem__(self, key, value):
    # 锁保护索引更新
    with self._lock:
        value[self.key_field] = key
        if key in self._key_to_offset:
            # 追加删除标记
            with open(self.file_path, "ab") as f:
                f.write(deletion_record)

    # 文件写入（不锁，减少竞争）
    with open(self.file_path, "ab") as f:
        f.write(data)

    # 再次锁保护索引更新
    with self._lock:
        self._key_to_offset[key] = new_offset
```

### 13.2 索引重建算法

**关键：只保留最后一条有效记录**

```python
# 第一遍：收集所有记录
records = []
for offset, line in file:
    data = json.loads(line)
    records.append((offset, data, key))

# 第二遍：保留每个 key 的最后一条记录
latest_records = {}
for offset, data, key in records:
    if key not in latest_records or offset > latest_records[key][0]:
        latest_records[key] = (offset, data)

# 第三遍：检查删除标记
for key, (offset, data) in latest_records.items():
    if data.get('_deleted'):
        _deleted_keys.add(key)
    else:
        _key_to_offset[key] = offset
```

### 13.3 文件操作的原子性

```python
def compact(self):
    # 使用临时文件 + 原子替换
    temp_path = file_path + ".tmp"

    # 写入临时文件
    with open(temp_path, "wb") as dst:
        write_data(dst)

    # 原子性替换（POSIX 保证）
    os.replace(temp_path, file_path)
```

---

## 14. 线程安全细节

### 锁的获取时机

```python
# 所有对索引的访问都需要锁
def __getitem__(self, key):
    with self._lock:
        offset = _key_to_offset[key]  # 需要锁
    
    # 文件读取不需要锁（减少竞争）
    with open(file_path, "rb") as f:
        f.seek(offset)
        return json.loads(f.readline())
```

### 死锁避免

**使用 RLock 而不是 Lock**

```python
# 标准锁（Lock）- 会导致死锁
d = JLFDict("data.jsonl", "id")
with d:  # 获取锁
    nested_function()  # ❌ 尝试再次获取锁 -> 死锁！

def nested_function():
    with d:  # Lock 不能重入
        pass

# 可重入锁（RLock）- 不会死锁
d = JLFDict("data.jsonl", "id")
with d:  # 获取锁
    nested_function()  # ✅ RLock 允许重入

def nested_function():
    with d:  # RLock 可以重入
        pass
```

---

## 15. 总结

### 核心原理

1. **JSONL 格式** - 每行一个 JSON 对象，流式处理友好
2. **文件偏移量索引** - 存储 key → 文件位置映射，O(1) 查找
3. **追加写入 + 软删除** - 快速写入，原地修改通过标记实现
4. **延迟读取** - 只加载索引，按需读取数据
5. **索引持久化** - 快速启动，索引可随时重建
6. **线程安全** - RLock 保护所有关键操作
7. **数据恢复** - 从 JSONL 文件可重建所有索引

### 关键优势

- ✅ **内存高效** - 只保存索引，数据在磁盘
- ✅ **大规模** - 处理任意大小数据集（仅受磁盘限制）
- ✅ **持久化** - 自动保存，无需手动处理
- ✅ **易用** - 完全模仿 dict/list 接口
- ✅ **线程安全** - 多线程环境安全使用
- ✅ **可读** - JSONL 格式人类可读

### 适用场景

- ✅ 大数据集（> RAM）
- ✅ 日志存储
- ✅ 缓存系统
- ✅ 嵌入式系统（资源有限）
- ✅ 数据管道（需要持久化）

### 不适用场景

- ❌ 需要复杂查询（用数据库）
- ❌ 需要插入操作（用其他数据结构）
- ❌ 内存很小且需要全部数据（也许用分布式数据库）
- ❌ 需要实时性要求极高的场景（用内存数据库）

---

## 16. 技术架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户层                              │
│                   (dict/list 接口)                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                      JLFDict / JLFList                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  索引层（内存）                                    │  │
│  │  • _key_to_offset: key → offset                   │  │
│  │  • _index_to_offset: index → offset                │  │
│  │  • _deleted_keys: 已删除的键                        │  │
│  │  • _active_indices: 有效索引列表                    │  │
│  │  • threading.RLock: 线程锁                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    文件存储层（磁盘）                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ data.jsonl   │  │ data.jsonl   │  │ data.jsonl   │    │
│  │ (JSONL 格式) │  │ .idx         │  │ .idx.del     │    │
│  │              │  │ (Pickle 索引)│  │ (删除标记)   │    │
│  │ • 数据行     │  │              │  │              │    │
│  │ • 删除标记   │  │ 映射表      │  │ 集合         │    │
│  │ • 更新记录   │  │              │  │              │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   操作流程示例（读取）                         │
│                                                              │
│  1. 用户调用: users["user1"]                             │
│  ↓                                                           │
│  2. 查找偏移量: offset = _key_to_offset["user1"] = 89      │
│  3. 跳转文件: f.seek(89)                                  │
│  4. 读取数据: line = f.readline()                         │
│  5. 解析 JSON: data = json.loads(line)                    │
│  6. 返回数据: return data                                  │
│                                                              │
│  总耗时: 几毫秒（主要是磁盘 I/O）                            │
└─────────────────────────────────────────────────────────────┘
```

---

**JsonLineTypes 是一个巧妙的设计，通过 JSONL 格式、文件偏移量索引、追加写入策略等技术，实现了类 dict/list 接口的大规模数据存储方案，在保持简单易用的同时，提供了出色的内存效率和持久化能力。**
