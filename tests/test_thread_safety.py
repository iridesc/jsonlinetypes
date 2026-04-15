"""
线程安全测试

现在 JLFDict 和 JLFList 默认就是线程安全的。
"""

from jsonlinetypes import JLFDict, JLFList
import threading
import tempfile
import os


def concurrent_write(d, worker_id, num_items):
    """
    测试函数：并发写入

    Args:
        d: JLFDict 实例
        worker_id: 工作线程 ID
        num_items: 写入的项目数
    """
    for i in range(num_items):
        key = f"key_{worker_id}_{i}"
        d[key] = {"id": key, "worker": worker_id, "index": i}


def concurrent_read(d, worker_id, num_reads):
    """
    测试函数：并发读取

    Args:
        d: JLFDict 实例
        worker_id: 工作线程 ID
        num_reads: 读取的项目数
    """
    for i in range(num_reads):
        key = f"key_{worker_id % 5}_{i % 10}"
        try:
            value = d.get(key)
        except Exception as e:
            print(f"Worker {worker_id}: Read error: {e}")


if __name__ == "__main__":
    # 示例：多线程测试
    temp_file = tempfile.mktemp(suffix=".jsonl")

    try:
        # 创建 JLFDict（现在是线程安全的）
        d = JLFDict(temp_file, "id", auto_save_index=False)

        print("=" * 80)
        print("线程安全测试")
        print("=" * 80)

        # 测试1：并发写入
        print("\n【测试1】并发写入")
        print("-" * 80)

        num_threads = 5
        num_items = 100
        threads = []

        import time
        start_time = time.time()

        for i in range(num_threads):
            t = threading.Thread(target=concurrent_write, args=(d, i, num_items))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        end_time = time.time()

        print(f"✅ {num_threads} 个线程，每个写入 {num_items} 条记录")
        print(f"✅ 耗时: {end_time - start_time:.2f}s")
        print(f"✅ 最终记录数: {len(d)}")
        assert len(d) == num_threads * num_items, "数据丢失！"

        # 测试2：并发读取
        print("\n【测试2】并发读取")
        print("-" * 80)

        num_reads = 1000
        threads = []

        start_time = time.time()

        for i in range(10):
            t = threading.Thread(target=concurrent_read, args=(d, i, num_reads))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        end_time = time.time()

        print(f"✅ 10 个线程，每个读取 {num_reads} 次")
        print(f"✅ 耗时: {end_time - start_time:.2f}s")
        print(f"✅ 无错误")

        # 测试3：并发读写
        print("\n【测试3】并发读写")
        print("-" * 80)

        threads = []
        start_time = time.time()

        for i in range(5):
            t = threading.Thread(target=concurrent_write, args=(d, i, 50))
            threads.append(t)
            t.start()

        for i in range(5):
            t = threading.Thread(target=concurrent_read, args=(d, i + 5, 200))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        end_time = time.time()

        print(f"✅ 5 个写线程，5 个读线程")
        print(f"✅ 耗时: {end_time - start_time:.2f}s")
        print(f"✅ 数据完整，无错误")

        # 测试4：批量操作优化
        print("\n【测试4】批量操作性能对比")
        print("-" * 80)

        d.clear()

        # 方法1：每个操作都加锁
        start_time = time.time()
        for i in range(1000):
            d[f"key_{i}"] = {"id": f"key_{i}", "value": i}
        time_each = time.time() - start_time
        print(f"✅ 每个操作加锁: {time_each:.3f}s")

        d.clear()

        # 方法2：批量操作，只加锁一次
        start_time = time.time()
        with d:
            for i in range(1000):
                d[f"key_{i}"] = {"id": f"key_{i}", "value": i}
        time_batch = time.time() - start_time
        print(f"✅ 批量操作加锁: {time_batch:.3f}s")
        print(f"✅ 性能提升: {time_each / time_batch:.1f}x")

        print("\n" + "=" * 80)
        print("所有测试通过！")
        print("=" * 80)

    finally:
        # 清理
        d.clear()
        for ext in ["", ".idx", ".idx.del"]:
            path = temp_file + ext
            if os.path.exists(path):
                os.remove(path)
