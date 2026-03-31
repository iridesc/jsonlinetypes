import json
import os
import pickle
import tempfile
from collections.abc import MutableMapping

class JLFDict(MutableMapping):
    def __init__(self, file_path, key_field, auto_save_index=True):
        self.file_path = file_path
        self.key_field = key_field
        self.index_path = file_path + ".idx"
        self._key_to_offset = {}
        self._deleted_keys = set()
        self._auto_save_index = auto_save_index
        
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                pass

        if auto_save_index and os.path.exists(self.index_path):
            with open(self.index_path, "rb") as f:
                self._key_to_offset = pickle.load(f)
            self._load_deleted_keys()
        else:
            self._build_index()
            if auto_save_index:
                self.save_index()

    def _load_deleted_keys(self):
        if os.path.exists(self.index_path + ".del"):
            with open(self.index_path + ".del", "rb") as f:
                self._deleted_keys = pickle.load(f)

    def _save_deleted_keys(self):
        with open(self.index_path + ".del", "wb") as f:
            pickle.dump(self._deleted_keys, f)

    def _build_index(self):
        # First pass: collect all records with their offsets
        records = []
        with open(self.file_path, "rb") as f:
            offset = f.tell()
            line = f.readline()
            while line:
                if line.strip():
                    data = json.loads(line.decode('utf-8'))
                    key = data.get(self.key_field)
                    if key is not None:
                        records.append((key, offset, data))
                offset = f.tell()
                line = f.readline()

        # Second pass: determine which keys are active
        # Only keep the latest version (highest offset) for each key
        last_offsets = {}
        for key, offset, data in records:
            if offset > last_offsets.get(key, -1):
                last_offsets[key] = (offset, data)

        # Now check if the latest record is deleted
        for key, offset in last_offsets.items():
            should_delete = False
            for _, _, data in records:
                if data.get('_deleted') and data.get(self.key_field) == key:
                    # Check if this delete record is the last one for this key
                    last_key_offset = last_offsets[key][0] if isinstance(last_offsets[key], tuple) else last_offsets[key]
                    # Actually, we need to be more careful here
                    # Let's rebuild the logic
                    pass

        # Simpler approach: process in order, keeping track of current state
        self._deleted_keys = set()
        current_offsets = {}
        for key, offset, data in records:
            if data.get('_deleted'):
                self._deleted_keys.add(key)
                if key in current_offsets:
                    del current_offsets[key]
            else:
                self._deleted_keys.discard(key)
                current_offsets[key] = offset

        self._key_to_offset = current_offsets

    def save_index(self):
        with open(self.index_path, "wb") as f:
            pickle.dump(self._key_to_offset, f)
        self._save_deleted_keys()

    def __getitem__(self, key):
        if key in self._deleted_keys:
            raise KeyError(key)
        offset = self._key_to_offset.get(key)
        if offset is None:
            raise KeyError(key)
        with open(self.file_path, "rb") as f:
            f.seek(offset)
            return json.loads(f.readline().decode('utf-8'))

    def __setitem__(self, key, value):
        value[self.key_field] = key
        if key in self._key_to_offset and key not in self._deleted_keys:
            with open(self.file_path, "ab") as f:
                deletion_record = {self.key_field: key, "_deleted": True}
                f.seek(0, os.SEEK_END)
                f.write((json.dumps(deletion_record, ensure_ascii=False) + "\n").encode('utf-8'))
        
        with open(self.file_path, "ab") as f:
            f.seek(0, os.SEEK_END)
            new_offset = f.tell()
            f.write((json.dumps(value, ensure_ascii=False) + "\n").encode('utf-8'))
            self._key_to_offset[key] = new_offset
            if key in self._deleted_keys:
                self._deleted_keys.remove(key)
        if self._auto_save_index:
            self.save_index()

    def __delitem__(self, key):
        if key in self._deleted_keys:
            raise KeyError(key)
        if key not in self._key_to_offset:
            raise KeyError(key)
        
        with open(self.file_path, "ab") as f:
            deletion_record = {self.key_field: key, "_deleted": True}
            f.seek(0, os.SEEK_END)
            f.write((json.dumps(deletion_record, ensure_ascii=False) + "\n").encode('utf-8'))
        
        self._deleted_keys.add(key)
        del self._key_to_offset[key]
        if self._auto_save_index:
            self.save_index()

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key):
        return key in self._key_to_offset and key not in self._deleted_keys

    def __len__(self):
        return len(self._key_to_offset)

    def __iter__(self):
        for key in self._key_to_offset:
            if key not in self._deleted_keys:
                yield key

    def keys(self):
        from collections.abc import KeysView
        keys_list = [k for k in self._key_to_offset if k not in self._deleted_keys]
        return KeysView({k: self[k] for k in keys_list})

    def values(self):
        from collections.abc import ValuesView
        values_list = [self[k] for k in self]
        return ValuesView({k: self[k] for k in self})

    def items(self):
        from collections.abc import ItemsView
        items_dict = {k: self[k] for k in self}
        return ItemsView(items_dict)

    def pop(self, key, *args):
        if len(args) > 1:
            raise TypeError(f"pop expected at most 2 arguments, got {len(args) + 1}")
        try:
            value = self[key]
            del self[key]
            return value
        except KeyError:
            if args:
                return args[0]
            raise

    def update(self, other=None, **kwargs):
        if other is not None:
            if hasattr(other, 'items'):
                for key, value in other.items():
                    self[key] = value
            else:
                for key, value in other:
                    self[key] = value
        for key, value in kwargs.items():
            self[key] = value
        if self._auto_save_index:
            self.save_index()

    def clear(self):
        self._key_to_offset.clear()
        self._deleted_keys.clear()
        with open(self.file_path, "w", encoding="utf-8") as f:
            pass
        self.save_index()

    def compact(self):
        if not self._deleted_keys and len(self._key_to_offset) == 0:
            return
        
        temp_path = self.file_path + ".tmp"
        new_offset = 0
        
        with open(self.file_path, "rb") as src:
            with open(temp_path, "wb") as dst:
                line = src.readline()
                while line:
                    if line.strip():
                        data = json.loads(line.decode('utf-8'))
                        if not data.get('_deleted'):
                            key = data.get(self.key_field)
                            dst.write(line)
                            self._key_to_offset[key] = new_offset
                        new_offset = dst.tell()
                    else:
                        new_offset += len(line)
                    line = src.readline()
        
        os.replace(temp_path, self.file_path)
        self._deleted_keys.clear()
        self.save_index()

    def __str__(self):
        return f"JLFDict({dict(self.items())})"

    def __repr__(self):
        return f"JLFDict({self.file_path!r}, {self.key_field!r})"
