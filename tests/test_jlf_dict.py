import os
import tempfile
import pytest
import json
from jsonlinetypes import JLFDict

@pytest.fixture
def temp_file():
    fd, path = tempfile.mkstemp(suffix='.jsonl')
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)
    if os.path.exists(path + '.idx'):
        os.remove(path + '.idx')
    if os.path.exists(path + '.idx.del'):
        os.remove(path + '.idx.del')

class TestJLFDict:
    def test_init_creates_file(self, temp_file):
        d = JLFDict(temp_file, "id")
        assert os.path.exists(temp_file)
    
    def test_basic_get_set(self, temp_file):
        d = JLFDict(temp_file, "id")
        d[1] = {"id": 1, "name": "Alice"}
        assert d[1] == {"id": 1, "name": "Alice"}
    
    def test_get_with_default(self, temp_file):
        d = JLFDict(temp_file, "id")
        assert d.get(999, "default") == "default"
        assert d.get(999) is None
    
    def test_contains(self, temp_file):
        d = JLFDict(temp_file, "id")
        d[1] = {"id": 1, "name": "Alice"}
        assert 1 in d
        assert 2 not in d
    
    def test_len(self, temp_file):
        d = JLFDict(temp_file, "id")
        assert len(d) == 0
        d[1] = {"id": 1, "name": "Alice"}
        assert len(d) == 1
        d[2] = {"id": 2, "name": "Bob"}
        assert len(d) == 2
    
    def test_keys(self, temp_file):
        d = JLFDict(temp_file, "id")
        d[1] = {"id": 1, "name": "Alice"}
        d[2] = {"id": 2, "name": "Bob"}
        keys = list(d.keys())
        assert sorted(keys) == [1, 2]
    
    def test_values(self, temp_file):
        d = JLFDict(temp_file, "id")
        d[1] = {"id": 1, "name": "Alice"}
        d[2] = {"id": 2, "name": "Bob"}
        values = list(d.values())
        assert len(values) == 2
        assert any(v["name"] == "Alice" for v in values)
        assert any(v["name"] == "Bob" for v in values)
    
    def test_items(self, temp_file):
        d = JLFDict(temp_file, "id")
        d[1] = {"id": 1, "name": "Alice"}
        d[2] = {"id": 2, "name": "Bob"}
        items = list(d.items())
        assert len(items) == 2
        assert set(k for k, v in items) == {1, 2}
    
    def test_iter(self, temp_file):
        d = JLFDict(temp_file, "id")
        d[1] = {"id": 1, "name": "Alice"}
        d[2] = {"id": 2, "name": "Bob"}
        keys = list(d)
        assert sorted(keys) == [1, 2]
    
    def test_delitem(self, temp_file):
        d = JLFDict(temp_file, "id")
        d[1] = {"id": 1, "name": "Alice"}
        del d[1]
        assert 1 not in d
        assert len(d) == 0
    
    def test_delitem_nonexistent(self, temp_file):
        d = JLFDict(temp_file, "id")
        with pytest.raises(KeyError):
            del d[999]
    
    def test_pop(self, temp_file):
        d = JLFDict(temp_file, "id")
        d[1] = {"id": 1, "name": "Alice"}
        result = d.pop(1)
        assert result == {"id": 1, "name": "Alice"}
        assert 1 not in d
    
    def test_pop_with_default(self, temp_file):
        d = JLFDict(temp_file, "id")
        result = d.pop(999, "default")
        assert result == "default"
    
    def test_pop_nonexistent(self, temp_file):
        d = JLFDict(temp_file, "id")
        with pytest.raises(KeyError):
            d.pop(999)
    
    def test_update(self, temp_file):
        d = JLFDict(temp_file, "id")
        d.update({1: {"id": 1, "name": "Alice"}, 2: {"id": 2, "name": "Bob"}})
        assert d[1]["name"] == "Alice"
        assert d[2]["name"] == "Bob"
        assert len(d) == 2
    
    def test_update_with_kwargs(self, temp_file):
        d = JLFDict(temp_file, "id")
        d.update({1: {"id": 1, "name": "Alice"}}, name="updated")
        assert d[1]["name"] == "Alice"
        assert d.get("name") is None
    
    def test_update_from_list(self, temp_file):
        d = JLFDict(temp_file, "id")
        d.update([(1, {"id": 1, "name": "Alice"}), (2, {"id": 2, "name": "Bob"})])
        assert d[1]["name"] == "Alice"
        assert d[2]["name"] == "Bob"
    
    def test_clear(self, temp_file):
        d = JLFDict(temp_file, "id")
        d[1] = {"id": 1, "name": "Alice"}
        d[2] = {"id": 2, "name": "Bob"}
        d.clear()
        assert len(d) == 0
        assert 1 not in d
    
    def test_compact(self, temp_file):
        d = JLFDict(temp_file, "id")
        d[1] = {"id": 1, "name": "Alice"}
        d[2] = {"id": 2, "name": "Bob"}
        d[1] = {"id": 1, "name": "Alice2"}
        del d[2]
        d.compact()
        
        assert len(d) == 1
        assert d[1]["name"] == "Alice2"
        assert 2 not in d
    
    def test_persistence_index(self, temp_file):
        d1 = JLFDict(temp_file, "id", auto_save_index=True)
        d1[1] = {"id": 1, "name": "Alice"}
        d1[2] = {"id": 2, "name": "Bob"}
        
        d2 = JLFDict(temp_file, "id", auto_save_index=True)
        assert len(d2) == 2
        assert d2[1]["name"] == "Alice"
        assert d2[2]["name"] == "Bob"
    
    def test_modify_existing_key(self, temp_file):
        d = JLFDict(temp_file, "id")
        d[1] = {"id": 1, "name": "Alice"}
        d[1] = {"id": 1, "name": "Alice2"}
        assert d[1]["name"] == "Alice2"
        assert len(d) == 1
    
    def test_str_repr(self, temp_file):
        d = JLFDict(temp_file, "id")
        d[1] = {"id": 1, "name": "Alice"}
        assert "JLFDict" in str(d)
        assert "JLFDict" in repr(d)
        assert temp_file in repr(d)
    
    def test_file_integrity(self, temp_file):
        d = JLFDict(temp_file, "id")
        d[1] = {"id": 1, "name": "Alice"}
        d[2] = {"id": 2, "name": "Bob"}
        
        with open(temp_file, 'r', encoding='utf-8') as f:
            lines = [json.loads(line) for line in f.readlines() if line.strip()]
        
        assert len([l for l in lines if not l.get('_deleted')]) == 2
        assert not any(l.get('_deleted') for l in lines)
    
    def test_key_autocomplete(self, temp_file):
        d = JLFDict(temp_file, "id")
        d[1] = {"name": "Alice"}
        assert d[1]["id"] == 1
    
    def test_large_performance(self, temp_file):
        import time
        d = JLFDict(temp_file, "id")
        start = time.time()
        for i in range(1000):
            d[i] = {"id": i, "name": f"User{i}"}
        write_time = time.time() - start
        
        start = time.time()
        for i in range(1000):
            _ = d[i]
        read_time = time.time() - start
        
        assert write_time < 5.0
        assert read_time < 1.0
        assert len(d) == 1000
