import os
import tempfile
import pytest
import json
from jsonlinetypes import JLFList

@pytest.fixture
def temp_file():
    fd, path = tempfile.mkstemp(suffix='.jsonl')
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)
    if os.path.exists(path + '.idx'):
        os.remove(path + '.idx')

class TestJLFList:
    def test_init_creates_file(self, temp_file):
        lst = JLFList(temp_file)
        assert os.path.exists(temp_file)
    
    def test_basic_append_get(self, temp_file):
        lst = JLFList(temp_file)
        lst.append({"name": "Alice"})
        assert lst[0] == {"name": "Alice"}
    
    def test_len(self, temp_file):
        lst = JLFList(temp_file)
        assert len(lst) == 0
        lst.append({"name": "Alice"})
        assert len(lst) == 1
        lst.append({"name": "Bob"})
        assert len(lst) == 2
    
    def test_extend(self, temp_file):
        lst = JLFList(temp_file)
        lst.extend([{"name": "Alice"}, {"name": "Bob"}])
        assert len(lst) == 2
        assert lst[0] == {"name": "Alice"}
        assert lst[1] == {"name": "Bob"}
    
    def test_iter(self, temp_file):
        lst = JLFList(temp_file)
        lst.append({"name": "Alice"})
        lst.append({"name": "Bob"})
        items = list(lst)
        assert len(items) == 2
        assert items[0] == {"name": "Alice"}
        assert items[1] == {"name": "Bob"}
    
    def test_negative_index(self, temp_file):
        lst = JLFList(temp_file)
        lst.append({"name": "Alice"})
        lst.append({"name": "Bob"})
        assert lst[-1] == {"name": "Bob"}
        assert lst[-2] == {"name": "Alice"}
    
    def test_setitem(self, temp_file):
        lst = JLFList(temp_file)
        lst.append({"name": "Alice"})
        lst.append({"name": "Bob"})
        lst[0] = {"name": "Alice2"}
        assert lst[0] == {"name": "Alice2"}
        assert lst[1] == {"name": "Bob"}
    
    def test_setitem_negative_index(self, temp_file):
        lst = JLFList(temp_file)
        lst.append({"name": "Alice"})
        lst.append({"name": "Bob"})
        lst[-1] = {"name": "Bob2"}
        assert lst[1] == {"name": "Bob2"}
    
    def test_delitem(self, temp_file):
        lst = JLFList(temp_file)
        lst.append({"name": "Alice"})
        lst.append({"name": "Bob"})
        del lst[0]
        assert len(lst) == 1
        assert lst[0] == {"name": "Bob"}
    
    def test_delitem_negative_index(self, temp_file):
        lst = JLFList(temp_file)
        lst.append({"name": "Alice"})
        lst.append({"name": "Bob"})
        del lst[-1]
        assert len(lst) == 1
        assert lst[0] == {"name": "Alice"}
    
    def test_pop(self, temp_file):
        lst = JLFList(temp_file)
        lst.append({"name": "Alice"})
        lst.append({"name": "Bob"})
        result = lst.pop(0)
        assert result == {"name": "Alice"}
        assert len(lst) == 1
        assert lst[0] == {"name": "Bob"}
    
    def test_pop_negative(self, temp_file):
        lst = JLFList(temp_file)
        lst.append({"name": "Alice"})
        lst.append({"name": "Bob"})
        result = lst.pop(-1)
        assert result == {"name": "Bob"}
        assert len(lst) == 1
        assert lst[0] == {"name": "Alice"}
    
    def test_pop_default(self, temp_file):
        lst = JLFList(temp_file)
        result = lst.pop()
        assert len(lst) == 0
    
    def test_out_of_range(self, temp_file):
        lst = JLFList(temp_file)
        lst.append({"name": "Alice"})
        
        with pytest.raises(IndexError):
            _ = lst[5]
        
        with pytest.raises(IndexError):
            _ = lst[-5]
        
        with pytest.raises(IndexError):
            lst[5] = {"name": "Bob"}
        
        with pytest.raises(IndexError):
            del lst[5]
    
    def test_clear(self, temp_file):
        lst = JLFList(temp_file)
        lst.append({"name": "Alice"})
        lst.append({"name": "Bob"})
        lst.clear()
        assert len(lst) == 0
    
    def test_compact(self, temp_file):
        lst = JLFList(temp_file)
        lst.append({"name": "Alice"})
        lst.append({"name": "Bob"})
        lst[0] = {"name": "Alice2"}
        del lst[1]
        lst.compact()
        
        assert len(lst) == 1
        assert lst[0] == {"name": "Alice2"}
    
    def test_reverse(self, temp_file):
        lst = JLFList(temp_file)
        lst.append({"name": "Alice"})
        lst.append({"name": "Bob"})
        lst.append({"name": "Charlie"})
        lst.reverse()
        
        assert lst[0] == {"name": "Charlie"}
        assert lst[1] == {"name": "Bob"}
        assert lst[2] == {"name": "Alice"}
    
    def test_persistence_index(self, temp_file):
        lst1 = JLFList(temp_file, auto_save_index=True)
        lst1.append({"name": "Alice"})
        lst1.append({"name": "Bob"})
        
        lst2 = JLFList(temp_file, auto_save_index=True)
        assert len(lst2) == 2
        assert lst2[0] == {"name": "Alice"}
        assert lst2[1] == {"name": "Bob"}
    
    def test_str_repr(self, temp_file):
        lst = JLFList(temp_file)
        lst.append({"name": "Alice"})
        assert "JLFList" in str(lst)
        assert "JLFList" in repr(lst)
        assert temp_file in repr(lst)
    
    def test_insert_not_supported(self, temp_file):
        lst = JLFList(temp_file)
        lst.append({"name": "Alice"})
        with pytest.raises(NotImplementedError):
            lst.insert(0, {"name": "Bob"})
    
    def test_file_integrity(self, temp_file):
        lst = JLFList(temp_file)
        lst.append({"name": "Alice"})
        lst.append({"name": "Bob"})
        
        with open(temp_file, 'r', encoding='utf-8') as f:
            lines = [json.loads(line) for line in f.readlines() if line.strip()]
        
        assert len([l for l in lines if not l.get('_deleted') and '_index' in l]) == 2
    
    def test_mixed_data_types(self, temp_file):
        lst = JLFList(temp_file)
        lst.append("string")
        lst.append(123)
        lst.append({"key": "value"})
        lst.append(["a", "b", "c"])
        
        assert lst[0] == "string"
        assert lst[1] == 123
        assert lst[2] == {"key": "value"}
        assert lst[3] == ["a", "b", "c"]
        assert len(lst) == 4
    
    def test_large_performance(self, temp_file):
        import time
        lst = JLFList(temp_file)
        start = time.time()
        for i in range(1000):
            lst.append({"id": i, "name": f"User{i}"})
        write_time = time.time() - start
        
        start = time.time()
        for i in range(1000):
            _ = lst[i]
        read_time = time.time() - start
        
        assert write_time < 5.0
        assert read_time < 1.0
        assert len(lst) == 1000
    
    def test_iteration_order(self, temp_file):
        lst = JLFList(temp_file)
        items = [{"id": i} for i in range(10)]
        for item in items:
            lst.append(item)
        
        for i, item in enumerate(lst):
            assert item == items[i]
