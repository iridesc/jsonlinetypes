# 对比文档导航

本项目提供了详细的对比文档，帮助您了解 jsonlinetypes 与其他类似库的差异。

## 📊 对比文档

### 1. [COMPARISON.md](COMPARISON.md) - 功能和内存对比

对比以下库的功能特性、内存使用、性能等：

- jsonlinetypes
- shelve (Python 标准库)
- tinydb
- jsondb
- diskdict
- zodb
- pandas

**内容包括：**
- ✅ 各库使用方法和代码示例
- ✅ 内存消耗详细对比
- ✅ 性能对比表格
- ✅ 使用场景建议

### 2. [USABILITY.md](USABILITY.md) - 易用性对比

从 6 个维度评估各库的易用性：

- 安装难度
- API 简洁性
- 学习曲线
- 文档完善度
- 调试友好度
- 错误处理

**内容包括：**
- ✅ 易用性评分卡
- ✅ 代码行数对比
- ✅ 常见错误对比
- ✅ 学习时间估计
- ✅ 场景推荐

## 🎮 演示脚本

### 1. memory_demo.py - 内存使用演示

展示不同库的内存使用差异：

```bash
python memory_demo.py
```

**演示内容：**
- jsonlinetypes 如何只加载索引到内存
- 与普通 dict 的内存占用对比
- 内存使用估算表

### 2. usability_demo.py - 易用性演示

展示各库的易用性差异：

```bash
python usability_demo.py
```

**演示内容：**
- 易用性评分卡
- 代码行数对比
- 常见错误对比
- 安装方式对比
- 学习时间估计
- 完整代码示例

### 3. examples.py - 基础使用示例

jsonlinetypes 的基础使用示例：

```bash
python examples.py
```

## 📈 快速对比

### 综合评分（满分 5 星）

| 库 | 综合评分 | 最擅长 |
|---|---------|--------|
| **jsonlinetypes** | **4.7** | 易用性 + 内存友好 |
| **tinydb** | **4.0** | 查询功能 |
| **shelve** | **3.7** | 内置简单存储 |
| **diskdict** | **3.0** | 简单磁盘存储 |
| **pandas** | **3.0** | 数据分析 |
| **zodb** | **2.7** | 复杂应用 |

### 内存友好度对比（100 万条记录）

| 库 | 内存占用 | 数据位置 |
|---|---------|---------|
| jsonlinetypes | ~100MB | 索引在内存，数据在磁盘 |
| shelve | ~200-500MB | 按需缓存 |
| tinydb | ~500MB | 全部在内存 |
| pandas | 1-2GB | 全部在内存（默认） |

### 易用性对比

| 库 | 学习时间 | 代码行数（等效功能） |
|---|---------|-------------------|
| jsonlinetypes | 5 分钟 | 3-4 行 |
| shelve | 10 分钟 | 4 行 |
| tinydb | 30 分钟 | 5-6 行 |
| pandas | 4 小时+ | 5 行 |
| zodb | 2 小时+ | 10+ 行 |

### 特性对比

| 特性 | jsonlinetypes | shelve | tinydb | zodb | pandas |
|------|---------------|--------|--------|------|--------|
| 人类可读格式 | ✅ JSONL | ❌ Pickle | ✅ JSON | ❌ Binary | ❌ HDF5 |
| 安装 | pip install | 内置 | pip install | pip install | pip install |
| 推荐使用场景 | 大数据存储 | 简单存储 | 小型查询 | 复杂应用 | 数据分析 |
| 内存友好 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐ |
| 易用性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |

## 🎯 选择建议

### 根据 **易用性** 选择

**最易用：jsonlinetypes** (4.7/5)
- ✅ 零学习成本
- ✅ 完全模拟 dict/list 接口
- ✅ 代码最简洁

### 根据 **内存效率** 选择

**最内存友好：jsonlinetypes**
- ✅ 只加载索引到内存
- ✅ 数据保持在磁盘
- ✅ 适合大数据集

### 根据 **功能需求** 选择

- **简单存储** → jsonlinetypes 或 shelve
- **需要查询** → tinydb
- **数据分析** → pandas
- **复杂应用** → zodb

### 根据 **学习成本** 选择

- **零成本** → jsonlinetypes (5 分钟)
- **低耗时** → shelve, diskdict (10 分钟)
- **可接受** → tinydb (30 分钟)
- **投入较大** → zodb, pandas (2-4 小时+)

## 📝 使用示例

### jsonlinetypes - 最简洁

```python
from jsonlinetypes import JLFDict

# 3 行代码，和原生 dict 一样
d = JLFDict("data.jsonl", "id")
d["key"] = {"data": "value"}
print(d["key"])
```

### shelve - Python 内置

```python
import shelve

# 4 行代码，key 必须是字符串
with shelve.open("data.db") as db:
    db["key"] = {"data": "value"}
    print(db["key"])
```

### tinydb - 支持查询

```python
from tinydb import TinyDB, Query

# 6 行代码，需要学习 Query 语法
db = TinyDB("data.json")
User = Query()
db.insert({"name": "Alice", "age": 30})
db.close()
```

## 🔗 链接

- [README.md](README.md) - 项目主文档
- [README_CN.md](README_CN.md) - 中文文档
- [COMPARISON.md](COMPARISON.md) - 详细对比
- [USABILITY.md](USABILITY.md) - 易用性分析
- [memory_demo.py](memory_demo.py) - 内存演示
- [usability_demo.py](usability_demo.py) - 易用性演示
- [examples.py](examples.py) - 示例代码
