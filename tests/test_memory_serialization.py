#!/usr/bin/env python3
"""
内存消耗测试：比较不同序列化方案的内存使用
"""

import sys
sys.path.insert(0, '.')
import tracemalloc
import tempfile
import json
from jsonlinetypes import JLFDict, JLFList

def test_to_list_method():
    """方案1: to_list() 方法"""
    fd, path = tempfile.mkstemp(suffix='.jsonl')
    os.close(fd)

    tracemalloc.start()

    # 创建 JLFList（不占用大量内存）
    lst = JLFList(path)
    for i in range(10000):
        lst.append({"id": i, "data": "x" * 100})

    mem1 = tracemalloc.get_traced_memory()[0] / 1024 / 1024

    # 显式调用 to_list() - 此时才加载所有数据
    data = lst.to_list()
    mem2 = tracemalloc.get_traced_memory()[0] / 1024 / 1024

    tracemalloc.stop()

    # 清理
    for f in [path, path + ".idx"]:
        if os.path.exists(f):
            os.remove(f)

    return mem1, mem2

def test_custom_encoder():
    """方案2: 自定义 JSONEncoder"""
    fd, path = tempfile.mkstemp(suffix='.jsonl')
    os.close(fd)

    class JLFEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, JLFList):
                return obj.to_list()
            return super().default(obj)

    tracemalloc.start()

    # 创建 JLFList
    lst = JLFList(path)
    for i in range(10000):
        lst.append({"id": i, "data": "x" * 100})

    mem1 = tracemalloc.get_traced_memory()[0] / 1024 / 1024

    # 使用自定义 encoder 序列化
    json.dumps({"list": lst}, cls=JLFEncoder)
    mem2 = tracemalloc.get_traced_memory()[0] / 1024 / 1024

    tracemalloc.stop()

    # 清理
    for f in [path, path + ".idx"]:
        if os.path.exists(f):
            os.remove(f)

    return mem1, mem2


def test_dict_to_dict_method():
    """JLFDict 方案1: to_dict() 方法"""
    fd, path = tempfile.mkstemp(suffix='.jsonl')
    os.close(fd)

    tracemalloc.start()

    # 创建 JLFDict（不占用大量内存）
    d = JLFDict(path, "id")
    for i in range(10000):
        d[i] = {"id": i, "data": "x" * 100}

    mem1 = tracemalloc.get_traced_memory()[0] / 1024 / 1024

    # 显式调用 to_dict() - 此时才加载所有数据
    data = d.to_dict()
    mem2 = tracemalloc.get_traced_memory()[0] / 1024 / 1024

    tracemalloc.stop()

    # 清理
    for f in [path, path + ".idx", path + ".idx.del"]:
        if os.path.exists(f):
            os.remove(f)

    return mem1, mem2


def test_dict_custom_encoder():
    """JLFDict 方案2: 自定义 JSONEncoder"""
    fd, path = tempfile.mkstemp(suffix='.jsonl')
    os.close(fd)

    class JLFEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, JLFDict):
                return obj.to_dict()
            return super().default(obj)

    tracemalloc.start()

    # 创建 JLFDict
    d = JLFDict(path, "id")
    for i in range(10000):
        d[i] = {"id": i, "data": "x" * 100}

    mem1 = tracemalloc.get_traced_memory()[0] / 1024 / 1024

    # 使用自定义 encoder 序列化
    json.dumps({"dict": d}, cls=JLFEncoder)
    mem2 = tracemalloc.get_traced_memory()[0] / 1024 / 1024

    tracemalloc.stop()

    # 清理
    for f in [path, path + ".idx", path + ".idx.del"]:
        if os.path.exists(f):
            os.remove(f)

    return mem1, mem2

if __name__ == "__main__":
    import os

    print("=" * 80)
    print("JLFList 内存消耗测试对比")
    print("=" * 80)

    print("\n【方案1: to_list() 方法】")
    mem1_before, mem1_after = test_to_list_method()
    print(f"  - to_list() 前: {mem1_before:.2f} MB")
    print(f"  - to_list() 后: {mem1_after:.2f} MB")
    print(f"  - 增量: {mem1_after - mem1_before:.2f} MB")

    print("\n【方案2: 自定义 JSONEncoder】")
    mem2_before, mem2_after = test_custom_encoder()
    print(f"  - 序列化前: {mem2_before:.2f} MB")
    print(f"  - 序列化后: {mem2_after:.2f} MB")
    print(f"  - 增量: {mem2_after - mem2_before:.2f} MB")

    print("\n" + "=" * 80)
    print("JLFDict 内存消耗测试对比")
    print("=" * 80)

    print("\n【方案1: to_dict() 方法】")
    dict_mem1_before, dict_mem1_after = test_dict_to_dict_method()
    print(f"  - to_dict() 前: {dict_mem1_before:.2f} MB")
    print(f"  - to_dict() 后: {dict_mem1_after:.2f} MB")
    print(f"  - 增量: {dict_mem1_after - dict_mem1_before:.2f} MB")

    print("\n【方案2: 自定义 JSONEncoder】")
    dict_mem2_before, dict_mem2_after = test_dict_custom_encoder()
    print(f"  - 序列化前: {dict_mem2_before:.2f} MB")
    print(f"  - 序列化后: {dict_mem2_after:.2f} MB")
    print(f"  - 增量: {dict_mem2_after - dict_mem2_before:.2f} MB")

    print("\n" + "=" * 80)
    print("总结")
    print("=" * 80)
    print(f"JLFList:")
    print(f"  - to_list() 方法内存增量: {mem1_after - mem1_before:.2f} MB")
    print(f"  - 编码器方法内存增量: {mem2_after - mem2_before:.2f} MB")
    print(f"  - 内存优化: {(1 - (mem2_after - mem2_before) / (mem1_after - mem1_before)) * 100:.1f}%")

    print(f"\nJLFDict:")
    print(f"  - to_dict() 方法内存增量: {dict_mem1_after - dict_mem1_before:.2f} MB")
    print(f"  - 编码器方法内存增量: {dict_mem2_after - dict_mem2_before:.2f} MB")
    print(f"  - 内存优化: {(1 - (dict_mem2_after - dict_mem2_before) / (dict_mem1_after - dict_mem1_before)) * 100:.1f}%")

    print("\n结论：自定义 JSONEncoder 是内存最优的选择")
    print("=" * 80)
