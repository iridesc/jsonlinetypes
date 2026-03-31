# 索引文件损坏与数据恢复

## 问题

**索引文件损坏会影响 jsonlinetypes 数据的重新加载吗？**

## 短答案

✅ **不会影响数据丢失**。数据存储在 JSONL 文件中，索引只是加速访问的缓存。

**处理方式：**
1. 如果索引文件不存在 → 自动重建
2. 如果索引文件损坏 → 删除后自动重建
3. 重建后会从 JSONL 文件恢复所有数据

---

## 详细说明

### 1. 数据存储结构

```
data.jsonl       - 主数据文件（人类可读的 JSONL 格式）
data.jsonl.idx   - 索引文件（Pickle 格式，加速访问）
data.jsonl.idx.del - 删除标记索引（仅 JLFDict）
```

**关键点：**
- ✅ **所有数据存储在 JSONL 文件中**
- ✅ **索引文件只是缓存，不存储数据**
- ✅ **删除索引不影响 JSONL 数据**

### 2. 索引重建机制

**JLFDict 和 JLFList 在初始化时会：**

```python
# 伪代码
if auto_save_index and 索引文件存在:
    try:
        加载索引文件
    except:
        # 这里会抛出异常（如果索引损坏）
else:
    # 索引不存在或加载失败（手动删除后）
    重建索引()  # 扫描整个 JSONL 文件
    保存新索引()
```

**重建索引的步骤：**

1. 逐行读取 JSONL 文件
2. 解析每行数据
3. 对于每个 key/index，只保留**最后一个**记录
4. 检查最后一个记录的 `_deleted` 标记
5. 如果有 `_deleted: true`，则标记为已删除
6. 否则，记录其文件偏移量到索引中

### 3. 测试验证

运行测试脚本验证索引重建功能：

```bash
python test_index_recovery.py        # JLFDict 索引恢复测试
python test_list_index_recovery.py   # JLFList 索引恢复测试
```

**测试结果：**

```
✅ 索引文件删除后自动重建
✅ 重建后数据完全一致
✅ 正确处理已删除记录
✅ 正确处理更新后的记录
✅ 索引损坏后删除即可恢复
```

---

## 实际场景处理

### 场景 1: 索引文件不存在

```python
from jsonlinetypes import JLFDict

# 索引文件不存在（首次运行或被删除）
d = JLFDict("data.jsonl", "id")

# ✅ 自动重建索引
# ✅ 数据完全可用
print(len(d))  # 正常显示记录数
```

**流程：**
1. 检测到索引文件不存在
2. 扫描整个 JSONL 文件（可能需要几秒）
3. 重建索引并保存
4. 数据可正常使用

### 场景 2: 索引文件损坏

```python
from jsonlinetypes import JLFDict

d = JLFDict("data.jsonl", "id", auto_save_index=True)

# ❌ 如果索引文件损坏，会抛出异常
# UnpicklingError: pickle data was truncated

# ✅ 解决方法：删除损坏的索引文件
import os
os.remove("data.jsonl.idx")
if os.path.exists("data.jsonl.idx.del"):
    os.remove("data.jsonl.idx.del")

# ✅ 重新创建，会自动重建索引
d = JLFDict("data.jsonl", "id")
print(len(d))  # 数据完全恢复
```

### 场景 3: 正常使用中的索引更新

```python
from jsonlinetypes import JLFDict

d = JLFDict("data.jsonl", "id", auto_save_index=True)  # 默认

# 每次修改会自动更新索引
d["key1"] = {"id": "key1", "value": "data"}

# 或手动保存
d.save_index()

# ✅ 索引保持最新状态
```

---

## 性能影响

### 索引重建时间

| 记录数 | 文件大小 | 重建时间（估算） |
|--------|---------|----------------|
| 10,000 | ~5MB | < 1 秒 |
| 100,000 | ~50MB | 1-3 秒 |
| 1,000,000 | ~500MB | 5-15 秒 |
| 10,000,000 | ~5GB | 1-3 分钟 |

**影响因素：**
- 📁 磁盘 I/O 速度（SSD vs HDD）
- 💾 CPU 性能（JSON 解析）
- 📊 单条记录大小

### 重建后性能

重建完成后，性能恢复正常：
- ✅ O(1) 查找
- ✅ O(1) 插入
- ✅ 正常读写速度

---

## 最佳实践

### 1. 定期备份

```python
import shutil
import os

# 备份 JSONL 文件（最重要的）
shutil.copy("data.jsonl", "data.jsonl.backup")

# 索引文件可以不备份（损坏可重建）
```

### 2. 安全关闭

```python
d = JLFDict("data.jsonl", "id")
try:
    # ... 使用数据 ...
    pass
finally:
    d.save_index()  # 确保索引保存
```

### 3. 错误处理

```python
from jsonlinetypes import JLFDict
import os

def safe_open_jlf(file_path, key_field):
    """安全打开 JLFDict，自动处理索引损坏"""
    try:
        return JLFDict(file_path, key_field)
    except Exception as e:
        print(f"索引加载失败: {e}")
        print("正在重建索引...")

        # 删除可能的损坏索引
        if os.path.exists(file_path + ".idx"):
            os.remove(file_path + ".idx")
        if os.path.exists(file_path + ".idx.del"):
            os.remove(file_path + ".idx.del")

        # 重新打开（会自动重建）
        return JLFDict(file_path, key_field)

# 使用
d = safe_open_jlf("data.jsonl", "id")
```

### 4. 监控文件完整性

```python
import os

def check_index_integrity(file_path):
    """检查索引文件是否可用"""
    index_path = file_path + ".idx"

    if not os.path.exists(index_path):
        print("⚠️  索引文件不存在，需要重建")
        return False

    try:
        # 尝试加载索引（验证完整性）
        import pickle
        with open(index_path, "rb") as f:
            pickle.load(f)
        print("✅ 索引文件正常")
        return True
    except Exception as e:
        print(f"❌ 索引文件损坏: {e}")
        return False

# 使用
check_index_integrity("data.jsonl")
```

---

## 常见问题

### Q1: 索引损坏会丢失数据吗？

❌ **不会**。数据在 JSONL 文件中，索引只是缓存。

### Q2: 如何避免索引损坏？

- ✅ 正确关闭程序（确保 save_index）
- ✅ 不要手动编辑索引文件
- ✅ 定期备份 JSONL 文件
- ✅ 使用 UPS 防止突然断电

### Q3: 重建索引会丢失更新后的数据吗？

❌ **不会**。重建时会扫描整个 JSONL 文件，保留每个 key/index 的最后一个记录。

例如：
```
JSONL 文件：
{"id": 1, "name": "Alice"}
{"id": 1, "name": "Alice2"}  # 更新后

✅ 重建后保留: {"id": 1, "name": "Alice2"}
```

### Q4: 可以禁用索引吗？

```python
# 可以禁用自动保存索引
d = JLFDict("data.jsonl", "id", auto_save_index=False)

# 但性能会下降（每次都要扫描文件）
```

### Q5: 恢复数据只需要 JSONL 文件吗？

✅ **是的**。只要有 JSONL 文件，就可以恢复所有数据（通过重建索引）。

---

## 对比其他库

| 库 | 数据存储 | 索引可重建 | 数据恢复容易度 |
|---|---------|-----------|--------------|
| **jsonlinetypes** | JSONL 文件 | ✅ 完全自动 | ⭐⭐⭐⭐⭐ 极简单 |
| shelve | 二进制文件 | ❌ 需手动处理 | ⭐⭐ 中等 |
| tinydb | JSON 文件 | ✅ 可以重建 | ⭐⭐⭐⭐ 容易 |
| zodb | 专用格式 | ⚠️ 复杂 | ⭐⭐ 中等 |

**jsonlinetypes 优势：**
- 人类可读格式（JSONL）
- 索引损坏不影响数据
- 自动重建索引
- 任何时候都可以恢复数据

---

## 总结

| 问题 | 答案 |
|------|------|
| 索引损坏会丢失数据吗？ | ❌ 不会 |
| 如何恢复？ | 删除索引文件，重新创建 |
| 需要多长时间？ | 取决于数据量（1MB-5GB: 几秒到几分钟） |
| 会影响性能吗？ | 只影响启动时间，重建后性能正常 |
| 预防措施？ | 定期备份 JSONL 文件，正确关闭程序 |

**核心原则：**
> 📌 **索引是缓存，数据在 JSONL 中。索引损坏只会影响启动速度，不会丢失数据。**

---

## 相关文件

- [test_index_recovery.py](test_index_recovery.py) - JLFDict 索引恢复测试
- [test_list_index_recovery.py](test_list_index_recovery.py) - JLFList 索引恢复测试
- [如何测试索引损坏？](#测试验证) -> 运行测试脚本

---

## 故障排除指南

### 情况 1: 启动失败，提示索引加载错误

```bash
# 解决步骤
1. 删除损坏的索引文件
   rm data.jsonl.idx
   rm data.jsonl.idx.del  # 仅 JLFDict

2. 重新运行程序
   python your_app.py

3. 自动重建索引（可能需要几秒到几分钟）
```

### 情况 2: 数据不一致（感觉某些记录丢失）

```python
# 验证 JSONL 文件是否损坏
import json

with open("data.jsonl", "r") as f:
    for i, line in enumerate(f, 1):
        try:
            json.loads(line)
        except json.JSONDecodeError as e:
            print(f"❌ Line {i} 损坏: {e}")

# 如果 JSONL 文件损坏，需要恢复备份
# 如果 JSONL 文件正常，重建索引即可
```

### 情况 3: 重建索引后记录数不对

```python
# 检查 JSONL 文件记录数
with open("data.jsonl", "r") as f:
    total_lines = sum(1 for _ in f) if f.read().strip() else 0

print(f"JSONL 总行数: {total_lines}")

# 检查有多少删除标记
import json
deleted_count = 0
with open("data.jsonl", "r") as f:
    for line in f:
        if line.strip():
            data = json.loads(line)
            if data.get('_deleted'):
                deleted_count += 1

print(f"删除标记数: {deleted_count}")
```

---

需要更多帮助？查看：
- [README.md](README.md) - 基本使用
- [COMPARISON.md](COMPARISON.md) - 与其他库对比
- [USABILITY.md](USABILITY.md) - 易用性分析
