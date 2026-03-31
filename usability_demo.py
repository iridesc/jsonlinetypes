#!/usr/bin/env python3
"""
易用性对比演示 - 展示各个库的代码简洁性和易用性
"""

import os
import tempfile
import shutil

print("=" * 80)
print("易用性对比演示")
print("=" * 80)

# ============================================================================
# 评分卡
# ============================================================================
print("\n" + "=" * 80)
print("易用性评分卡（满分5星）")
print("=" * 80)

score_card = """
┌─────────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│ Library     │ 安装难度 │ API简洁  │ 学习曲线 │ 文档完善 │ 调试友好 │ 错误处理 │ 综合评分 │
├─────────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│jsonlinetypes│ ⭐⭐⭐⭐⭐ │ ⭐⭐⭐⭐⭐ │ ⭐⭐⭐⭐⭐ │ ⭐⭐⭐⭐   │ ⭐⭐⭐⭐   │ ⭐⭐⭐⭐   │  4.7    │
│shelve      │ ⭐⭐⭐⭐⭐ │ ⭐⭐⭐   │ ⭐⭐⭐   │ ⭐⭐⭐⭐   │ ⭐⭐⭐   │ ⭐⭐⭐   │  3.7    │
│tinydb      │ ⭐⭐⭐⭐   │ ⭐⭐⭐   │ ⭐⭐⭐   │ ⭐⭐⭐⭐⭐ │ ⭐⭐⭐⭐   │ ⭐⭐⭐⭐   │  4.0    │
│diskdict    │ ⭐⭐⭐   │ ⭐⭐⭐⭐   │ ⭐⭐⭐⭐   │ ⭐⭐     │ ⭐⭐     │ ⭐⭐⭐   │  3.0    │
│zodb        │ ⭐⭐⭐   │ ⭐⭐     │ ⭐⭐     │ ⭐⭐⭐   │ ⭐⭐⭐   │ ⭐⭐⭐   │  2.7    │
│pandas      │ ⭐⭐     │ ⭐⭐⭐   │ ⭐⭐     │ ⭐⭐⭐⭐⭐ │ ⭐⭐⭐⭐   │ ⭐⭐⭐   │  3.0    │
└─────────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
"""
print(score_card)

# ============================================================================
# 代码行数对比
# ============================================================================
print("\n" + "=" * 80)
print("代码行数对比 - 实现相同功能")
print("=" * 80)

print("(功能: 创建、保存1条数据、读取)")
print()

examples = [
    ("jsonlinetypes", """
from jsonlinetypes import JLFDict
d = JLFDict("data.jsonl", "id")
d["key"] = {"data": "value"}
print(d["key"])
""", 4, "最简洁"),

    ("shelve", """
import shelve
with shelve.open("data.db") as db:
    db["key"] = {"data": "value"}
    print(db["key"])
""", 4, "简洁，但key必须是字符串"),

    ("tinydb", """
from tinydb import TinyDB
db = TinyDB("data.json")
db.insert({"_key": "key", "data": "value"})
print(db.all())
db.close()
""", 6, "需要Query语法"),

    ("diskdict", """
import diskdict
d = diskdict.DiskDict("data.bin")
d["key"] = {"data": "value"}
print(d["key"])
""", 4, "简洁，但文档少"),

    ("zodb", """
from ZODB import FileStorage, DB
import transaction
storage = FileStorage.FileStorage("data.fs")
db = DB(storage)
conn = db.open()
root = conn.root()
root["key"] = {"data": "value"}
transaction.commit()
conn.close()
print(root["key"])
""", 11, "最复杂"),

    ("pandas", """
import pandas as pd
df = pd.DataFrame([{"key": "key", "data": "value"}])
df.to_hdf("data.h5", "table", mode="w")
df = pd.read_hdf("data.h5", "table")
print(df.to_dict())
""", 5, "功能强大，但概念多")
]

for lib, code, lines, comment in examples:
    print(f"\n【{lib}】{lines} 行  - {comment}")
    print("-" * 80)
    print(code.strip())

# ============================================================================
# 常见错误对比
# ============================================================================
print("\n" + "=" * 80)
print("常见错误对比 - 新手容易踩的坑")
print("=" * 80)

errors = [
    ("jsonlinetypes", [
        ("✅ 无特殊限制", "和原生 dict/list 一致"),
        ("✅ 错误信息清晰", "KeyError, IndexError 等标准异常")
    ]),

    ("shelve", [
        ("❌ Key 必须是字符串", 'db[1] = "value"  ❌ 错误\ndb["1"] = "value" ✅ 正确'),
        ("⚠️ 忘记 close()", "需要用 with 语句或手动 close()")
    ]),

    ("tinydb", [
        ("⚠️ 查询无结果不报错", 'db.search(User.wrong == "x")  # 返回 [] 不报错'),
        ("⚠️ 拼写错误难以发现", "查询返回空列表时可能是拼写错误")
    ]),

    ("zodb", [
        ("❌ 忘记 commit()", "修改后必须 transaction.commit()"),
        ("❌ 对象引用复杂", "持久化对象需要理解脏检查机制")
    ]),

    ("pandas", [
        ("⚠️ SettingWithCopyWarning", 'df["age"][0] = 25  ⚠️ 警告\ndf.loc[0, "age"] = 25  ✅ 推荐'),
        ("⚠️ 索引方式多", "loc, iloc, ix 等容易混淆")
    ])
]

for lib, error_list in errors:
    print(f"\n【{lib}】")
    print("-" * 80)
    for issue, desc in error_list:
        print(f"{issue:10s} {desc}")

# ============================================================================
# 安装方式对比
# ============================================================================
print("\n" + "=" * 80)
print("安装方式对比")
print("=" * 80)

install_methods = [
    ("jsonlinetypes", "pip install jsonlinetypes", "✅ 简单，无依赖"),
    ("shelve", "无需安装，Python 内置", "✅ 零安装"),
    ("tinydb", "pip install tinydb", "✅ 简单"),
    ("diskdict", "pip install diskdict", "⚠️ 来源不确定"),
    ("zodb", "pip install ZODB", "⚠️ 包较大"),
    ("pandas", "pip install pandas", "⚠️ 包很大，依赖多")
]

for lib, install, note in install_methods:
    print(f"\n{lib:15s}")
    print(f"  安装: {install}")
    print(f"  备注: {note}")

# ============================================================================
# 学习时间估计
# ============================================================================
print("\n" + "=" * 80)
print("学习时间估计（达到基本使用水平）")
print("=" * 80)

learning_times = [
    ("jsonlinetypes", "5分钟", "零学习成本，会 dict 就会用"),
    ("shelve", "10分钟", "需了解 key 限制"),
    ("tinydb", "30分钟", "学习 Query 语法"),
    ("diskdict", "10分钟", "类似 dict，但文档少"),
    ("zodb", "2小时+", "需理解事务、持久化等概念"),
    ("pandas", "4小时+", "需学习 DataFrame 概念和 API")
]

for lib, time_estimate, description in learning_times:
    bar = "█" * min(20, int(time_estimate.replace("分钟", "").replace("小时+", "").split("+")[0]) // 2)
    print(f"\n{lib:15s} {time_estimate:10s} {bar}")
    print(f"              {description}")

# ============================================================================
# 实际代码示例 - jsonlinetypes
# ============================================================================
print("\n" + "=" * 80)
print("实际代码示例 - jsonlinetypes 最易用")
print("=" * 80)

from jsonlinetypes import JLFDict, JLFList

temp_file = tempfile.mktemp(suffix=".jsonl")

try:
    print("\n【完整示例】就像使用原生 dict/list 一样")
    print("-" * 80)

    # 创建
    d = JLFDict(temp_file, "id")
    print("✅ 创建: d = JLFDict('data.jsonl', 'id')")

    # 写入
    d["user1"] = {"id": "user1", "name": "Alice", "age": 30}
    d["user2"] = {"id": "user2", "name": "Bob", "age": 25}
    print("✅ 写入: d['user1'] = {...}")

    # 读取
    user = d["user1"]
    print(f"✅ 读取: d['user1'] = {user}")

    # 更新
    d["user1"]["age"] = 31
    print("✅ 更新: d['user1']['age'] = 31")

    # 删除
    del d["user2"]
    print("✅ 删除: del d['user2']")

    # 检查存在
    print(f"✅ 存在检查: 'user1' in d = {'user1' in d}")

    # 迭代
    print("✅ 迭代:")
    for key, value in d.items():
        print(f"      {key}: {value}")

    # 获取视图
    print(f"✅ keys: {list(d.keys())}")
    print(f"✅ 长度: {len(d)}")

    # 人类可读的文件
    print("\n✅ 文件内容（人类可读）:")
    with open(temp_file, "r") as f:
        print(f.read())

finally:
    for ext in ["", ".idx", ".idx.del"]:
        path = temp_file + ext
        if os.path.exists(path):
            os.remove(path)

# ============================================================================
# 总结
# ============================================================================
print("\n" + "=" * 80)
print("总结")
print("=" * 80)

summary = """
【易用性排名】
  🥇 jsonlinetypes (4.7/5) - 最易用，零学习成本
  🥈 tinydb      (4.0/5) - 功能强大，有学习成本
  🥉 shelve      (3.7/5) - 内置，key限制
  4. diskdict    (3.0/5) - 简单但文档少
  5. pandas      (3.0/5) - 功能强大但学习曲线陡
  6. zodb        (2.7/5) - 复杂但适合高级用法

【选择建议】
  • 新手入门          → jsonlinetypes
  • 简单数据存储      → jsonlinetypes 或 shelve
  • 需要查询功能      → tinydb
  • 数据分析          → pandas
  • 复杂应用          → zodb
  • 使用Python内置    → shelve

【代码简洁性】
  最简洁: jsonlinetypes, shelve, diskdict (3-4行)
  中等: tinydb, pandas (5-6行)
  最复杂: zodb (10+行)

【学习成本】
  零成本: jsonlinetypes (5分钟)
  低成本: shelve, diskdict (10分钟)
  中等: tinydb (30分钟)
  高成本: zodb, pandas (2-4小时+)

详细对比请查看: USABILITY.md
"""
print(summary)

print("=" * 80)
