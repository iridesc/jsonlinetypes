#!/usr/bin/env python3
"""
测试 JLFList 索引重建
"""

import os
import tempfile
from jsonlinetypes import JLFList

print("=" * 80)
print("测试：JLFList 索引重建")
print("=" * 80)

temp_file = tempfile.mktemp(suffix=".jsonl")

try:
    # 步骤 1: 创建并写入数据
    print("\n【步骤 1】创建 JLFList 并写入数据")
    print("-" * 80)

    lst = JLFList(temp_file)

    # 添加数据
    lst.append({"name": "Alice"})
    lst.append({"name": "Bob"})
    lst.append({"name": "Charlie"})

    print(f"✅ 添加 3 条数据，总长度: {len(lst)}")
    print(f"✅ items: {list(lst)}")

    # 更新数据
    lst[1] = {"name": "Bob Updated"}
    print(f"✅ 更新索引 1: {lst[1]}")

    # 删除数据
    del lst[0]
    print(f"✅ 删除索引 0，剩余: {len(lst)} 条")
    print(f"✅ items: {list(lst)}")

    lst.save_index()

    # 步骤 2: 正常加载
    print("\n【步骤 2】正常加载")
    print("-" * 80)

    del lst
    lst = JLFList(temp_file)
    print(f"✅ 从索引加载: {len(lst)} 条")
    print(f"✅ items: {list(lst)}")

    # 步骤 3: 删除索引，重建
    print("\n【步骤 3】删除索引，自动重建")
    print("-" * 80)

    del lst

    if os.path.exists(temp_file + ".idx"):
        os.remove(temp_file + ".idx")

    lst = JLFList(temp_file)
    print(f"✅ 重建索引: {len(lst)} 条")
    print(f"✅ items: {list(lst)}")

    # 验证数据
    assert len(lst) == 2
    assert lst[0]["name"] == "Bob Updated"
    assert lst[1]["name"] == "Charlie"

    print("✅ 数据验证通过")

    # 步骤 4: 更多操作
    print("\n【步骤 4】执行更多操作")
    print("-" * 80)

    lst.append({"name": "David"})
    lst[0] = {"name": "Bob Final"}
    del lst[1]

    print(f"✅ 更多操作后: {len(lst)} 条")
    print(f"✅ items: {list(lst)}")

    lst.save_index()

    # 步骤 5: 完整重建
    print("\n【步骤 5】删除索引，完整重建")
    print("-" * 80)

    del lst

    if os.path.exists(temp_file + ".idx"):
        os.remove(temp_file + ".idx")

    lst = JLFList(temp_file)
    print(f"✅ 完整重建: {len(lst)} 条")
    print(f"✅ items: {list(lst)}")

    assert len(lst) == 2
    assert lst[0]["name"] == "Bob Final"
    assert lst[1]["name"] == "David"

    print("✅ 数据完全恢复")

finally:
    # 清理
    for ext in ["", ".idx"]:
        path = temp_file + ext
        if os.path.exists(path):
            os.remove(path)

print("\n" + "=" * 80)
print("测试结论")
print("=" * 80)

print("""
✅ JLFList 索引重建功能正常
✅ 正确处理更新操作（保留最新值）
✅ 正确处理删除操作
✅ 正确维护索引顺序
""")

print("=" * 80)
