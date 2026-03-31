# JsonLineTypes

**基于 JSONL 文件的字典/列表 - 大数据集的高效内存替代方案**

## 概述

`JsonLineTypes` 提供了 `JLFDict` 和 `JLFList` 类，模拟 Python 内置 `dict` 和 `list` 类型的行为，但将数据存储在磁盘上的 JSON Lines (JSONL) 文件中而不是内存中。这对于处理无法装入 RAM 的大型数据集特别有用。

## 特性

### JLFDict
- ✅ 可直接替代 dict
- ✅ O(1) 查找、插入、更新、删除
- ✅ 支持：`keys()`, `values()`, `items()`, 迭代
- ✅ 支持：`get()`, `pop()`, `clear()`, `update()`
- ✅ 索引持久化，快速启动
- ✅ 紧凑操作以清理已删除的记录

### JLFList
- ✅ 可直接替代 list
- ✅ O(1) 追加、扩展、索引访问
- ✅ 支持：负索引、迭代
- ✅ 支持：`pop()`, `reverse()`, `clear()`
- ✅ 索引持久化，快速启动
- ✅ 紧凑操作以清理已删除的记录

## 安装

```bash
pip install jsonlinetypes
```

或从源码安装：

```bash
git clone https://github.com/yourusername/jsonlinetypes.git
cd jsonlinetypes
pip install .
```

## 快速开始

### JLFDict 使用

```python
from jsonlinetypes import JLFDict

# 创建由 JSONL 文件支持的字典类对象
d = JLFDict("data.jsonl", "id")

# 添加数据（就像 dict 一样）
d[1] = {"id": 1, "name": "Alice"}
d[2] = {"id": 2, "name": "Bob"}

# 访问数据
print(d[1])  # 输出: {'id': 1, 'name': 'Alice'}

# 迭代（就像 dict 一样）
for key, value in d.items():
    print(key, value)

# 更新现有键
d[1] = {"id": 1, "name": "Alice2"}

# 删除键
del d[2]

# 弹出键
value = d.pop(1, default)

# 批量更新
d.update({3: {"id": 3, "name": "Charlie"}})

# 压缩以删除已删除的记录
d.compact()
```

### JLFList 使用

```python
from jsonlinetypes import JLFList

# 创建由 JSONL 文件支持的列表类对象
lst = JLFList("items.jsonl")

# 添加项目（就像 list 一样）
lst.append({"name": "Alice"})

# 批量添加
lst.extend([{"name": "Bob"}, {"name": "Charlie"}])

# 按索引访问
print(lst[0])    # 输出: {'name': 'Alice'}
print(lst[-1])   # 输出: {'name': 'Charlie'}

# 迭代（就像 list 一样）
for item in lst:
    print(item)

# 按索引更新
lst[0] = {"name": "Alice2"}

# 按索引删除
del lst[1]

# 弹出最后一项
item = lst.pop()

# 原地反转
lst.reverse()

# 压缩以删除已删除的记录
lst.compact()
```

## 工作原理

### 存储格式
数据以 JSON Lines 格式存储（每行一个 JSON 对象，用换行符分隔）：

```
{"id": 1, "name": "Alice"}
{"id": 2, "name": "Bob"}
{"id": 1, "name": "Alice2"}
```

### 索引
使用 pickle 维护一个索引文件（`*.jsonl.idx`）以实现 O(1) 查找：

- **JLFDict**：将键映射到文件偏移量
- **JLFList**：将索引映射到文件偏移量

### 删除/更新策略
删除或更新记录时：
1. 将删除标记追加到文件中
2. 对于更新，也会追加新记录
3. 相应地更新索引
4. 调用 `compact()` 以清理（可选，建议定期执行）

## 性能

### 内存使用
- 仅索引保存在内存中
- 每条记录约 100 字节（无论数据大小如何）
- 1000 万条记录 ≈ 1GB RAM

### 基准测试结果
*(在 1000 条记录的典型数据集上测试)*

| 操作 | 时间 |
|-----------|------|
| 插入 1000 项 | < 1s |
| 读取 1000 项 | < 0.1s |
| 更新 1000 项 | < 1s |
| 删除 1000 项 | < 1s |
| 压缩 | < 0.5s |

### 与 dict/list 的对比

| 特性 | dict/list | JLFDict/JLFList |
|---------|-----------|-----------------|
| 内存 | 全部在 RAM 中 | 仅索引 |
| 最大大小 | 受限于 RAM | 受限于磁盘 |
| 读取速度 | 更快 | 快（定位 + 读取） |
| 写入速度 | 更快 | 快（追加 + 索引）|
| 持久化 | 手动 | 自动 |
| 压缩 | N/A | 需要定期执行 |

## API 参考

### JLFDict

#### 构造函数
```python
JLFDict(file_path, key_field, auto_save_index=True)
```

- `file_path`：JSONL 文件路径
- `key_field`：用作键的字段名
- `auto_save_index`：更改时自动保存索引

#### 方法
- `__getitem__(key)`：按键获取值
- `__setitem__(key, value)`：按键设置值
- `__delitem__(key)`：删除键
- `get(key, default=None)`：获取默认值
- `keys()`：获取键视图
- `values()`：获取值视图  
- `items()`：获取项视图
- `pop(key, default)`：弹出并返回值
- `update(other)`：用字典/可迭代对象更新
- `clear()`：清除所有数据
- `compact()`：清理已删除的记录

### JLFList

#### 构造函数
```python
JLFList(file_path, auto_save_index=True)
```

- `file_path`：JSONL 文件路径
- `auto_save_index`：更改时自动保存索引

#### 方法
- `__getitem__(index)`：按索引获取值
- `__setitem__(index, value)`：按索引设置值
- `__delitem__(index)`：按索引删除
- `append(value)`：追加值
- `extend(values)`：用可迭代对象扩展
- `pop(index)`：弹出并返回值
- `reverse()`：原地反转
- `clear()`：清除所有数据
- `compact()`：清理已删除的记录

## 最佳实践

1. **定期使用 `compact()`** - 在大量删除/更新操作后调用
2. **选择合适的键** - 为 JLFDict 使用唯一、稳定的键
3. **批量操作** - 使用 `update()`/`extend()` 以获得更好的性能
4. **监控文件大小** - 大文件仍然受益于压缩
5. **压缩前备份** - 压缩会重写文件

## 限制

- JLFList 不支持 `insert()`（仅追加格式不支持）
- 修改操作会追加到文件中（定期调用 `compact()`）
- 需要磁盘 I/O（比内存中的 dict/list 慢）

## 要求

- Python 3.8+
- 无外部依赖！

## 测试

使用 pytest 运行测试：

```bash
# 安装开发依赖
pip install pytest

# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/test_jlf_dict.py
```

## 线程安全

**JLFDict 和 JLFList 现在默认就是线程安全的。**

所有操作都自动受可重入锁（RLock）保护，使其在多线程环境中使用安全，无需额外加锁。

### 基本使用

```python
from jsonlinetypes import JLFDict, JLFList

# 线程安全的字典
d = JLFDict("data.jsonl", "id")

# 所有操作自动线程安全
d["key1"] = {"id": "key1", "value": "v1"}
value = d["key1"]

# 线程安全的列表
lst = JLFList("items.jsonl")
lst.append({"name": "Alice"})
```

### 批量操作（优化性能）

对于多个连续操作，使用上下文管理器只需锁定一次以获得更好的性能：

```python
# 内部所有操作只锁一次
with d:
    d["key1"] = value1
    d["key2"] = value2
    for i in range(100):
        d[f"key{i}"] = value

with lst:
    for i in range(100):
        lst.append({"name": f"Person{i}"})
```

### 多线程示例

```python
import threading
from jsonlinetypes import JLFDict

d = JLFDict("data.jsonl", "id")

def worker(worker_id, num_items):
    for i in range(num_items):
        d[f"key_{worker_id}_{i}"] = {"id": f"key_{worker_id}_{i}", "value": i}

# 多个线程可以安全地访问同一个 JLFDict
threads = []
for i in range(5):
    t = threading.Thread(target=worker, args=(i, 100))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print(f"总项目数: {len(d)}")  # 500 个项目，无数据丢失
```

### 性能

JLFDict 和 JLFList 的线程安全性能开销很小：

- **单次操作**：约 3-8% 开销（磁盘 I/O 是主要瓶颈）
- **批量操作**：使用上下文管理器时约 0-3% 开销
- **单线程使用**：仍然安全，开销极小

详细性能分析，请查看 [PERFORMANCE.md](PERFORMANCE.md)。

运行测试：`python test_thread_safety.py`

## 性能

### 线程安全性能开销

| 版本 | 性能下降 | 使用场景 |
|---------|---------------------|----------|
| JLFDict（不安全） | 0% | 单线程应用 |
| ThreadSafeJLFDict（单次操作） | 3-8% | 多线程少量操作 |
| ThreadSafeJLFDict（批量操作） | 0-3% | 多线程批量操作 |

**关键发现**：由于磁盘 I/O 是主要瓶颈，线程安全版本的性能开销极小（平均 2.8%）。

详细性能分析，请查看 [PERFORMANCE.md](PERFORMANCE.md)。

## 贡献

欢迎贡献！请随时提交 Pull Request。

## 许可证

MIT 许可证 - 详见 LICENSE 文件。

## 作者

Your Name - your.email@example.com

## 致谢

- 灵感来自 JSON Lines (jsonlines.org)
- 使用 Python 的 collections.abc 构建以实现鸭子类型

## 另请参阅

- [COMPARISON.md](COMPARISON.md) - 与类似库对比（shelve, tinydb, pandas 等）
- [USABILITY.md](USABILITY.md) - 易用性对比分析
- [INDEX_RECOVERY.md](INDEX_RECOVERY.md) - 索引损坏恢复与数据恢复
- [THREAD_SAFETY.md](THREAD_SAFETY.md) - 线程安全指南
- [PERFORMANCE.md](PERFORMANCE.md) - 性能对比分析
- [memory_demo.py](memory_demo.py) - 运行内存使用演示
- [usability_demo.py](usability_demo.py) - 运行易用性对比演示
- [benchmark_safety.py](benchmark_safety.py) - 运行性能对比测试
- [jsonlines](https://jsonlines.org/) - JSON Lines 规范
- [pandas](https://pandas.pydata.org/) - 用于数据分析（内存高效模式）

## 更新日志

### v0.1.0 (2024)
- 初始版本
- 具有完整类 dict 接口的 JLFDict
- 具有完整类 list 接口的 JLFList
- 索引持久化
- 紧凑操作
- 全面的测试覆盖
