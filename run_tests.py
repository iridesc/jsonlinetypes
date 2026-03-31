#!/usr/bin/env python3
import os
import sys
import tempfile
import json

sys.path.insert(0, '.')

from jsonlinetypes import JLFDict, JLFList

def run_tests():
    passed = 0
    failed = 0
    
    def test(name, fn):
        nonlocal passed, failed
        try:
            fn()
            print(f"✓ {name}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {name}: {type(e).__name__}: {e}")
            failed += 1
    
    # JLFDict Tests
    print("\n=== Testing JLFDict ===")
    
    def test_dict_basic():
        fd, path = tempfile.mkstemp(suffix='.jsonl')
        os.close(fd)
        try:
            d = JLFDict(path, "id")
            d[1] = {"id": 1, "name": "Alice"}
            assert d[1] == {"id": 1, "name": "Alice"}
            assert len(d) == 1
        finally:
            for f in [path, path + ".idx", path + ".idx.del"]:
                if os.path.exists(f):
                    os.remove(f)
    
    test("JLFDict basic get/set", test_dict_basic)
    
    def test_dict_get_default():
        fd, path = tempfile.mkstemp(suffix='.jsonl')
        os.close(fd)
        try:
            d = JLFDict(path, "id")
            assert d.get(999, "default") == "default"
            assert d.get(999) is None
        finally:
            for f in [path, path + ".idx", path + ".idx.del"]:
                if os.path.exists(f):
                    os.remove(f)
    
    test("JLFDict get with default", test_dict_get_default)
    
    def test_dict_contains():
        fd, path = tempfile.mkstemp(suffix='.jsonl')
        os.close(fd)
        try:
            d = JLFDict(path, "id")
            d[1] = {"id": 1, "name": "Alice"}
            assert 1 in d
            assert 2 not in d
        finally:
            for f in [path, path + ".idx", path + ".idx.del"]:
                if os.path.exists(f):
                    os.remove(f)
    
    test("JLFDict contains", test_dict_contains)
    
    def test_dict_keys():
        fd, path = tempfile.mkstemp(suffix='.jsonl')
        os.close(fd)
        try:
            d = JLFDict(path, "id")
            d[1] = {"id": 1, "name": "Alice"}
            d[2] = {"id": 2, "name": "Bob"}
            keys = list(d.keys())
            assert sorted(keys) == [1, 2]
        finally:
            for f in [path, path + ".idx", path + ".idx.del"]:
                if os.path.exists(f):
                    os.remove(f)
    
    test("JLFDict keys", test_dict_keys)
    
    def test_dict_values():
        fd, path = tempfile.mkstemp(suffix='.jsonl')
        os.close(fd)
        try:
            d = JLFDict(path, "id")
            d[1] = {"id": 1, "name": "Alice"}
            d[2] = {"id": 2, "name": "Bob"}
            values = list(d.values())
            assert len(values) == 2
            assert any(v["name"] == "Alice" for v in values)
        finally:
            for f in [path, path + ".idx", path + ".idx.del"]:
                if os.path.exists(f):
                    os.remove(f)
    
    test("JLFDict values", test_dict_values)
    
    def test_dict_items():
        fd, path = tempfile.mkstemp(suffix='.jsonl')
        os.close(fd)
        try:
            d = JLFDict(path, "id")
            d[1] = {"id": 1, "name": "Alice"}
            d[2] = {"id": 2, "name": "Bob"}
            items = list(d.items())
            assert len(items) == 2
            assert set(k for k, v in items) == {1, 2}
        finally:
            for f in [path, path + ".idx", path + ".idx.del"]:
                if os.path.exists(f):
                    os.remove(f)
    
    test("JLFDict items", test_dict_items)
    
    def test_dict_iter():
        fd, path = tempfile.mkstemp(suffix='.jsonl')
        os.close(fd)
        try:
            d = JLFDict(path, "id")
            d[1] = {"id": 1, "name": "Alice"}
            d[2] = {"id": 2, "name": "Bob"}
            keys = list(d)
            assert sorted(keys) == [1, 2]
        finally:
            for f in [path, path + ".idx", path + ".idx.del"]:
                if os.path.exists(f):
                    os.remove(f)
    
    test("JLFDict iter", test_dict_iter)
    
    def test_dict_delete():
        fd, path = tempfile.mkstemp(suffix='.jsonl')
        os.close(fd)
        try:
            d = JLFDict(path, "id")
            d[1] = {"id": 1, "name": "Alice"}
            del d[1]
            assert 1 not in d
            assert len(d) == 0
        finally:
            for f in [path, path + ".idx", path + ".idx.del"]:
                if os.path.exists(f):
                    os.remove(f)
    
    test("JLFDict delete", test_dict_delete)
    
    def test_dict_pop():
        fd, path = tempfile.mkstemp(suffix='.jsonl')
        os.close(fd)
        try:
            d = JLFDict(path, "id")
            d[1] = {"id": 1, "name": "Alice"}
            result = d.pop(1)
            assert result == {"id": 1, "name": "Alice"}
            assert 1 not in d
        finally:
            for f in [path, path + ".idx", path + ".idx.del"]:
                if os.path.exists(f):
                    os.remove(f)
    
    test("JLFDict pop", test_dict_pop)
    
    def test_dict_update():
        fd, path = tempfile.mkstemp(suffix='.jsonl')
        os.close(fd)
        try:
            d = JLFDict(path, "id")
            d.update({1: {"id": 1, "name": "Alice"}, 2: {"id": 2, "name": "Bob"}})
            assert d[1]["name"] == "Alice"
            assert d[2]["name"] == "Bob"
        finally:
            for f in [path, path + ".idx", path + ".idx.del"]:
                if os.path.exists(f):
                    os.remove(f)
    
    test("JLFDict update", test_dict_update)
    
    def test_dict_clear():
        fd, path = tempfile.mkstemp(suffix='.jsonl')
        os.close(fd)
        try:
            d = JLFDict(path, "id")
            d[1] = {"id": 1, "name": "Alice"}
            d[2] = {"id": 2, "name": "Bob"}
            d.clear()
            assert len(d) == 0
        finally:
            for f in [path, path + ".idx", path + ".idx.del"]:
                if os.path.exists(f):
                    os.remove(f)
    
    test("JLFDict clear", test_dict_clear)
    
    def test_dict_modify():
        fd, path = tempfile.mkstemp(suffix='.jsonl')
        os.close(fd)
        try:
            d = JLFDict(path, "id")
            d[1] = {"id": 1, "name": "Alice"}
            d[1] = {"id": 1, "name": "Alice2"}
            assert d[1]["name"] == "Alice2"
            assert len(d) == 1
        finally:
            for f in [path, path + ".idx", path + ".idx.del"]:
                if os.path.exists(f):
                    os.remove(f)
    
    test("JLFDict modify existing key", test_dict_modify)
    
    def test_dict_persistence():
        fd, path = tempfile.mkstemp(suffix='.jsonl')
        os.close(fd)
        try:
            d1 = JLFDict(path, "id", auto_save_index=True)
            d1[1] = {"id": 1, "name": "Alice"}
            d1[2] = {"id": 2, "name": "Bob"}
            
            d2 = JLFDict(path, "id", auto_save_index=True)
            assert len(d2) == 2
            assert d2[1]["name"] == "Alice"
        finally:
            for f in [path, path + ".idx", path + ".idx.del"]:
                if os.path.exists(f):
                    os.remove(f)
    
    test("JLFDict persistence", test_dict_persistence)
    
    # JLFList Tests
    print("\n=== Testing JLFList ===")
    
    def test_list_basic():
        fd, path = tempfile.mkstemp(suffix='.jsonl')
        os.close(fd)
        try:
            lst = JLFList(path)
            lst.append({"name": "Alice"})
            assert lst[0] == {"name": "Alice"}
        finally:
            for f in [path, path + ".idx"]:
                if os.path.exists(f):
                    os.remove(f)
    
    test("JLFList basic append/get", test_list_basic)
    
    def test_list_extend():
        fd, path = tempfile.mkstemp(suffix='.jsonl')
        os.close(fd)
        try:
            lst = JLFList(path)
            lst.extend([{"name": "Alice"}, {"name": "Bob"}])
            assert len(lst) == 2
            assert lst[0] == {"name": "Alice"}
        finally:
            for f in [path, path + ".idx"]:
                if os.path.exists(f):
                    os.remove(f)
    
    test("JLFList extend", test_list_extend)
    
    def test_list_negative_index():
        fd, path = tempfile.mkstemp(suffix='.jsonl')
        os.close(fd)
        try:
            lst = JLFList(path)
            lst.append({"name": "Alice"})
            lst.append({"name": "Bob"})
            assert lst[-1] == {"name": "Bob"}
        finally:
            for f in [path, path + ".idx"]:
                if os.path.exists(f):
                    os.remove(f)
    
    test("JLFList negative index", test_list_negative_index)
    
    def test_list_setitem():
        fd, path = tempfile.mkstemp(suffix='.jsonl')
        os.close(fd)
        try:
            lst = JLFList(path)
            lst.append({"name": "Alice"})
            lst.append({"name": "Bob"})
            lst[0] = {"name": "Alice2"}
            assert lst[0] == {"name": "Alice2"}
        finally:
            for f in [path, path + ".idx"]:
                if os.path.exists(f):
                    os.remove(f)
    
    test("JLFList setitem", test_list_setitem)
    
    def test_list_delete():
        fd, path = tempfile.mkstemp(suffix='.jsonl')
        os.close(fd)
        try:
            lst = JLFList(path)
            lst.append({"name": "Alice"})
            lst.append({"name": "Bob"})
            del lst[0]
            assert len(lst) == 1
            assert lst[0] == {"name": "Bob"}
        finally:
            for f in [path, path + ".idx"]:
                if os.path.exists(f):
                    os.remove(f)
    
    test("JLFList delete", test_list_delete)
    
    def test_list_pop():
        fd, path = tempfile.mkstemp(suffix='.jsonl')
        os.close(fd)
        try:
            lst = JLFList(path)
            lst.append({"name": "Alice"})
            lst.append({"name": "Bob"})
            result = lst.pop(0)
            assert result == {"name": "Alice"}
            assert len(lst) == 1
        finally:
            for f in [path, path + ".idx"]:
                if os.path.exists(f):
                    os.remove(f)
    
    test("JLFList pop", test_list_pop)
    
    def test_list_iter():
        fd, path = tempfile.mkstemp(suffix='.jsonl')
        os.close(fd)
        try:
            lst = JLFList(path)
            lst.append({"name": "Alice"})
            lst.append({"name": "Bob"})
            items = list(lst)
            assert len(items) == 2
        finally:
            for f in [path, path + ".idx"]:
                if os.path.exists(f):
                    os.remove(f)
    
    test("JLFList iter", test_list_iter)
    
    def test_list_clear():
        fd, path = tempfile.mkstemp(suffix='.jsonl')
        os.close(fd)
        try:
            lst = JLFList(path)
            lst.append({"name": "Alice"})
            lst.clear()
            assert len(lst) == 0
        finally:
            for f in [path, path + ".idx"]:
                if os.path.exists(f):
                    os.remove(f)
    
    test("JLFList clear", test_list_clear)
    
    def test_list_persistence():
        fd, path = tempfile.mkstemp(suffix='.jsonl')
        os.close(fd)
        try:
            lst1 = JLFList(path, auto_save_index=True)
            lst1.append({"name": "Alice"})
            
            lst2 = JLFList(path, auto_save_index=True)
            assert len(lst2) == 1
            assert lst2[0] == {"name": "Alice"}
        finally:
            for f in [path, path + ".idx"]:
                if os.path.exists(f):
                    os.remove(f)
    
    test("JLFList persistence", test_list_persistence)
    
    # Summary
    print(f"\n{'='*40}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*40}")
    
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
