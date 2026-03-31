import json
import os
import pickle
from collections.abc import MutableSequence

class JLFList(MutableSequence):
    def __init__(self, file_path, auto_save_index=True):
        self.file_path = file_path
        self.index_path = file_path + ".idx"
        self._index_to_offset = {}
        self._active_indices = []
        self._deleted_indexes = set()
        self._auto_save_index = auto_save_index
        
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                pass

        if auto_save_index and os.path.exists(self.index_path):
            with open(self.index_path, "rb") as f:
                data = pickle.load(f)
                self._index_to_offset = data.get('offsets', {})
                self._active_indices = data.get('active', [])
                self._deleted_indexes = data.get('deleted', set())
        else:
            self._build_index()
            if auto_save_index:
                self.save_index()

    def _build_index(self):
        index = 0
        with open(self.file_path, "rb") as f:
            offset = f.tell()
            line = f.readline()
            while line:
                if line.strip():
                    data = json.loads(line.decode('utf-8'))
                    if not data.get('_deleted') and '_index' in data:
                        original_index = data.get('_index')
                        self._index_to_offset[original_index] = offset
                        self._active_indices.append(original_index)
                        index += 1
                offset = f.tell()
                line = f.readline()
        self._next_index = max(self._active_indices) + 1 if self._active_indices else 0

    def save_index(self):
        data = {'offsets': self._index_to_offset, 'active': self._active_indices, 'deleted': self._deleted_indexes, 'next_index': self._next_index}
        with open(self.index_path, "wb") as f:
            pickle.dump(data, f)

    def _get_next_index(self):
        if not hasattr(self, '_next_index'):
            self._next_index = max(self._index_to_offset.keys()) + 1 if self._index_to_offset else 0
        return self._next_index

    def _normalize_index(self, index):
        length = len(self)
        if index < 0:
            index += length
        if index < 0 or index >= length:
            raise IndexError("list index out of range")
        return index
    
    def _get_original_index(self, logical_index):
        logical_index = self._normalize_index(logical_index)
        if 0 <= logical_index < len(self._active_indices):
            return self._active_indices[logical_index]
        raise IndexError("list index out of range")

    def __getitem__(self, index):
        original_index = self._get_original_index(index)
        offset = self._index_to_offset.get(original_index)
        if offset is None:
            raise IndexError("list index out of range")
        with open(self.file_path, "rb") as f:
            f.seek(offset)
            data = json.loads(f.readline().decode('utf-8'))
            return data.get('value')

    def __setitem__(self, index, value):
        original_index = self._get_original_index(index)
        
        with open(self.file_path, "ab") as f:
            deletion_record = {"_index": original_index, "_deleted": True}
            f.seek(0, os.SEEK_END)
            f.write((json.dumps(deletion_record, ensure_ascii=False) + "\n").encode('utf-8'))
        
        with open(self.file_path, "ab") as f:
            f.seek(0, os.SEEK_END)
            new_offset = f.tell()
            data = {"_index": original_index, "value": value}
            f.write((json.dumps(data, ensure_ascii=False) + "\n").encode('utf-8'))
            self._index_to_offset[original_index] = new_offset
        if self._auto_save_index:
            self.save_index()

    def __delitem__(self, index):
        original_index = self._get_original_index(index)
        
        with open(self.file_path, "ab") as f:
            deletion_record = {"_index": original_index, "_deleted": True}
            f.seek(0, os.SEEK_END)
            f.write((json.dumps(deletion_record, ensure_ascii=False) + "\n").encode('utf-8'))
        
        del self._index_to_offset[original_index]
        self._active_indices.remove(original_index)
        self._deleted_indexes.add(original_index)
        if self._auto_save_index:
            self.save_index()

    def __len__(self):
        return len(self._index_to_offset)

    def __iter__(self):
        for logical_index in range(len(self)):
            yield self[logical_index]

    def insert(self, index, value):
        raise NotImplementedError("Insert is not supported in append-only JSONL format")

    def append(self, value):
        index = self._get_next_index()
        with open(self.file_path, "ab") as f:
            f.seek(0, os.SEEK_END)
            new_offset = f.tell()
            data = {"_index": index, "value": value}
            f.write((json.dumps(data, ensure_ascii=False) + "\n").encode('utf-8'))
            self._index_to_offset[index] = new_offset
            self._active_indices.append(index)
            self._next_index = index + 1
        if self._auto_save_index:
            self.save_index()

    def extend(self, values):
        for value in values:
            self.append(value)
        self.save_index()

    def pop(self, index=-1):
        index = self._normalize_index(index)
        value = self[index]
        del self[index]
        return value

    def clear(self):
        self._index_to_offset.clear()
        self._active_indices.clear()
        self._deleted_indexes.clear()
        self._next_index = 0
        with open(self.file_path, "w", encoding="utf-8") as f:
            pass
        self.save_index()

    def compact(self):
        if not self._index_to_offset:
            return
        
        temp_path = self.file_path + ".tmp"
        new_offsets = {}
        new_active_indices = []
        new_index = 0
        new_offset = 0
        
        with open(temp_path, "wb") as dst:
            for original_index in self._active_indices:
                value = self[self._active_indices.index(original_index)]
                new_data = {"_index": new_index, "value": value}
                new_line = (json.dumps(new_data, ensure_ascii=False) + "\n").encode('utf-8')
                dst.write(new_line)
                new_offsets[new_index] = new_offset
                new_active_indices.append(new_index)
                new_offset = dst.tell()
                new_index += 1
        
        os.replace(temp_path, self.file_path)
        self._index_to_offset = new_offsets
        self._active_indices = new_active_indices
        self._next_index = new_index
        self._deleted_indexes.clear()
        self.save_index()

    def reverse(self):
        self._active_indices.reverse()
        if self._auto_save_index:
            self.save_index()

    def __str__(self):
        return f"JLFList({list(self)})"

    def __repr__(self):
        return f"JLFList({self.file_path!r})"
