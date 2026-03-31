#!/usr/bin/env python3
"""
演示线程安全问题
"""

import threading
import time
from jsonlinetypes import JLFDict
import tempfile
import os

print("=" * 80)
print("线程安全问题演示")
print("=" * 80)

temp_file = tempfile.mktemp(suffix=".jsonl")

def worker(d, worker_id, num_operations):
    """工作线程函数"""
    for i in range(num_operations):
        key = f"key_{worker_id}_{i % 10}"  # 每个线程只写10个不同的key

        # 模拟混合读写操作
        if i % 3 == 0:
            # 读操作
            try:
                value = d.get(key)
                # print(f"Thread {worker_id}: Read {key}")
            except Exception as e:
                print(f"Thread {worker_id}: Read error: {e}")
        else:
            # 写操作
            try:
                d[key] = {"id": key, "value": f"from_thread_{worker_id}", "count": i}
                # print(f"Thread {worker_id}: Write {key}")
            except Exception as e:
                print(f"Thread {worker_id}: Write error: {e}")

        # 小延迟
        time.sleep(0.001)

    print(f"Thread {worker_id} completed")

def test_unsafe_concurrent_access():
    """测试不安全的并发访问"""
    print("\n【测试 1】不安全的并发访问（无锁）")
    print("-" * 80)

    d = JLFDict(temp_file, "id", auto_save_index=False)

    # 创建多个线程
    num_threads = 5
    num_operations = 50
    threads = []

    print(f"启动 {num_threads} 个线程，每个执行 {num_operations} 次操作...")

    start_time = time.time()

    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(d, i, num_operations))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    end_time = time.time()

    print(f"所有线程完成，耗时: {end_time - start_time:.2f}s")
    print(f"最终记录数: {len(d)}")

    # 检查数据完整性
    print("\n检查数据完整性:")
    print(f"  索引中的 keys: {len(d._key_to_offset)}")
    print(f"  已删除的 keys: {len(d._deleted_keys)}")

    # 尝试检查 JSONL 文件
    jsonl_lines = 0
    with open(temp_file, "r") as f:
        for line in f:
            if line.strip():
                jsonl_lines += 1

    print(f"  JSONL 文件行数: {jsonl_lines}")

    print("\n【潜在问题】")
    print("  ⚠️  索引可能不同步（读写竞争条件）")
    print("  ⚠️  JSONL 文件写入可能交错（乱序）")
    print("  ⚠️  索引文件保存可能不完整（同时调用 save_index）")
    print("  ⚠️  可能出现 KeyError 或其他异常")

    d.clear()

def test_concurrent_saves():
    """测试并发保存索引"""
    print("\n【测试 2】并发保存索引")
    print("-" * 80)

    d = JLFDict(temp_file, "id", auto_save_index=False)

    # 先写入一些数据
    for i in range(10):
        d[f"key{i}"] = {"id": f"key{i}", "value": f"value{i}"}

    print(f"写入 {len(d)} 条记录")

    # 多个线程同时尝试保存索引
    def save_worker(worker_id):
        try:
            d.save_index()
            print(f"Thread {worker_id}: save_index() 完成")
        except Exception as e:
            print(f"Thread {worker_id}: save_index() 错误: {e}")

    threads = []
    for i in range(10):
        t = threading.Thread(target=save_worker, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("\n【潜在问题】")
    print("  ⚠️  多个线程同时写入索引文件可能导致文件损坏")
    print("  ⚠️  Pickle 数据可能不完整")
    print("  ⚠️  下次加载可能失败")

    # 尝试加载索引
    try:
        del d
        d2 = JLFDict(temp_file, "id", auto_save_index=True)
        print(f"\n✅ 索引加载成功，记录数: {len(d2)}")
        d2.clear()
    except Exception as e:
        print(f"\n❌ 索引加载失败: {e}")
        print("💡 尝试删除索引文件重建...")
        if os.path.exists(temp_file + ".idx"):
            os.remove(temp_file + ".idx")
        if os.path.exists(temp_file + ".idx.del"):
            os.remove(temp_file + ".idx.del")
        d2 = JLFDict(temp_file, "id", auto_save_index=True)
        print(f"✅ 重建索引成功，记录数: {len(d2)}")
        d2.clear()

def test_racy_condition():
    """测试竞态条件"""
    print("\n【测试 3】竞态条件演示")
    print("-" * 80)

    d = JLFDict(temp_file, "id", auto_save_index=False)

    errors = []
    lock = threading.Lock()

    def read_worker(worker_id):
        """只读线程"""
        for i in range(100):
            try:
                _ = d.get(f"key{i}")
            except (KeyError, OSError, Exception) as e:
                with lock:
                    errors.append(f"Read-{worker_id}: {type(e).__name__}")

    def write_worker(worker_id):
        """只写线程"""
        for i in range(100):
            try:
                key = f"key{i}"
                d[key] = {"id": key, "value": f"writer_{worker_id}", "count": i}
            except Exception as e:
                with lock:
                    errors.append(f"Write-{worker_id}: {type(e).__name__}")

    print("启动 1 个读线程和 1 个写线程...")

    t1 = threading.Thread(target=read_worker, args=(1,))
    t2 = threading.Thread(target=write_worker, args=(1,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    if errors:
        print(f"\n⚠️  发现 {len(errors)} 个错误:")
        for error in errors[:10]:  # 只显示前10个
            print(f"    {error}")
        if len(errors) > 10:
            print(f"    ... 还有 {len(errors) - 10} 个错误")
    else:
        print("\n✅ 未发现错误（但可能仍有潜在问题）")

    d.clear()

# 清理函数
def cleanup():
    for ext in ["", ".idx", ".idx.del"]:
        path = temp_file + ext
        if os.path.exists(path):
            os.remove(path)

try:
    test_unsafe_concurrent_access()
    test_concurrent_saves()
    test_racy_condition()

finally:
    cleanup()

print("\n" + "=" * 80)
print("演示结论")
print("=" * 80)

print("""
【什么是线程安全？】

线程安全是指多个线程同时访问同一个数据结构或资源时，
能够保证数据的完整性和一致性，不会出现不可预测的结果。

【当前版本的线程安全问题】

1. 无锁保护的共享数据
   ❌ _key_to_offset（字典）- 多线程同时修改可能导致数据损坏
   ❌ _deleted_keys（集合）- 多线程同时修改可能导致数据不一致

2. 非原子操作
   ❌ __setitem__ - 读索引、写文件、更新索引不是原子的
   ❌ __getitem__ - 读索引、读文件不是原子的
   ❌ save_index() - 写入索引文件不是原子的

3. 文件并发写入
   ❌ 多个线程同时写入 JSONL 文件可能导致数据交错
   ❌ 多个线程同时保存索引文件可能导致文件损坏

【建议】

✅ 单线程使用: 完全安全
❌ 多线程使用: **不安全**，容易出问题

【解决方案】

1. 使用外部锁（简单方案）
   - 在应用层使用 threading.Lock 保护所有操作

2. 修改 JLFDict 支持内部锁（推荐）
   - 添加可选的线程安全模式
   - 所有操作自动加锁

详细文档: THREAD_SAFETY.md
""")

print("=" * 80)
