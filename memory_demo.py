#!/usr/bin/env python3
"""
Simple memory demo - shows memory usage concept
"""

import os
import tempfile
import sys

print("=" * 80)
print("内存使用对比演示")
print("=" * 80)

# 演示 1: jsonlinetypes - 仅索引在内存
print("\n【演示 1】jsonlinetypes - 内存友好，只加载索引")
print("-" * 80)

from jsonlinetypes import JLFDict

temp_file = tempfile.mktemp(suffix=".jsonl")

try:
    # 创建并写入
    d = JLFDict(temp_file, "id")

    # 写入 10 条记录（概念上可以 millions）
    for i in range(10):
        d[str(i)] = {"id": i, "data": "user_record_data_here"}

    # 获取索引大小（内存中保存的）
    num_keys = len(d)
    print(f"✓ 索引记录数: {num_keys}")
    print(f"✓ 索引内存占用: ~{num_keys * 100} 字节（估算）")
    print(f"✓ 数据存储: 在磁盘上，不占用 RAM")

    # 只有当你访问某条数据时，才从磁盘读取
    data_0 = d['0']
    print(f"✓ 访问 key=0: {data_0} (这条从磁盘读取)")

finally:
    for ext in ["", ".idx", ".idx.del"]:
        path = temp_file + ext
        if os.path.exists(path):
            os.remove(path)

# 演示 2: 普通 dict - 所有数据在内存
print("\n【演示 2】Python dict - 所有数据在内存")
print("-" * 80)

data = {}
for i in range(10):
    data[str(i)] = {"id": i, "data": "user_record_data_here"}

print(f"✓ 记录数: {len(data)}")
print(f"✓ 内存占用: 全部数据在 RAM 中（包括 value 数据）")
print(f"✓ 访问速度快: 因为全部在内存")

# 数据量对比示例
print("\n" + "=" * 80)
print("内存使用对比（估算）")
print("=" * 80)

print("\n场景: 1,000,000 条记录，每条约 500 字节（总数据 500MB）")
print()

# jsonlinetypes
jsonl_index_size = 100_000_000  # 约 100 字节/索引
jsonl_data_memory = 0  # 数据在磁盘

# shelve
shelve_memory = 200_000_000  # 假设缓存部分

# tinydb
tinydb_memory = 500_000_000  # 全部加载

# pandas
pandas_memory = 1_000_000_000  # DataFrame 开销

print(f"{'库':<20} {'索引在内存':<15} {'数据在内存':<15} {'估算总内存':<15}")
print("-" * 80)
print(f"{'jsonlinetypes':<20} {'100MB':<15} {'0MB (磁盘)':<15} {'~100MB':<15}")
print(f"{'shelve':<20} {'50MB':<15} {'部分缓存':<15} {'~200-500MB':<15}")
print(f"{'tinydb':<20} {'N/A':<15} {'500MB':<15} {'~500MB':<15}")
print(f"{'pandas':<20} {'N/A':<15} {'1-2GB':<15} {'~1-2GB':<15}")

print("\n" + "=" * 80)
print("结论")
print("=" * 80)

print("""
jsonlinetypes 内存优势:
  ▸ 适合数据量 >> RAM 的场景
  ▸ 启动快（只加载索引）
  ▸ 内存占用与数据大小无关
  ▸ 适合: 日志存储、大数据集、内存受限环境

牺牲:
  ▸ 读取速度稍慢（需要磁盘 I/O）
  ▸ 不支持复杂查询
  ▸ 需要磁盘空间

适用场景:
  ✓ RAM: 1GB，数据: 100GB   → jsonlinetypes ✅
  ✓ RAM: 16GB，数据: 10GB    → pandas 也行
  ✓ RAM: 4GB，数据: 50GB     → jsonlinetypes ✅
""")

print("=" * 80)
