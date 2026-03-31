# JsonLineTypes

**Dict/List backed by JSONL files for large datasets - memory efficient alternatives to dict/list**

**中文说明见 [README_CN.md](README_CN.md)**

## Overview

`JsonLineTypes` provides `JLFDict` and `JLFList` classes that mimic the behavior of Python's built-in `dict` and `list` types, but store data in JSON Lines (JSONL) files on disk instead of memory. This is particularly useful when working with large datasets that don't fit in RAM.

## Features

### JLFDict
- ✅ Drop-in replacement for dict
- ✅ O(1) lookup, insert, update, delete
- ✅ Supports: `keys()`, `values()`, `items()`, iteration
- ✅ Supports: `get()`, `pop()`, `clear()`, `update()`
- ✅ Index persistence for fast startup
- ✅ Compact operation to clean up deleted records

### JLFList
- ✅ Drop-in replacement for list
- ✅ O(1) append, extend, index access
- ✅ Supports: negative indices, iteration
- ✅ Supports: `pop()`, `reverse()`, `clear()`
- ✅ Index persistence for fast startup
- ✅ Compact operation to clean up deleted records

## Installation

```bash
pip install jsonlinetypes
```

Or install from source:

```bash
git clone https://github.com/yourusername/jsonlinetypes.git
cd jsonlinetypes
pip install .
```

## Quick Start

### JLFDict Usage

```python
from jsonlinetypes import JLFDict

# Create a dict-like object backed by a JSONL file
d = JLFDict("data.jsonl", "id")

# Add data (just like dict)
d[1] = {"id": 1, "name": "Alice"}
d[2] = {"id": 2, "name": "Bob"}

# Access data
print(d[1])  # Output: {'id': 1, 'name': 'Alice'}

# Iterate (just like dict)
for key, value in d.items():
    print(key, value)

# Update existing key
d[1] = {"id": 1, "name": "Alice2"}

# Delete a key
del d[2]

# Pop a key
value = d.pop(1, default)

# Batch update
d.update({3: {"id": 3, "name": "Charlie"}})

# Compact to remove deleted records
d.compact()
```

### JLFList Usage

```python
from jsonlinetypes import JLFList

# Create a list-like object backed by a JSONL file
lst = JLFList("items.jsonl")

# Add items (just like list)
lst.append({"name": "Alice"})

# Batch add
lst.extend([{"name": "Bob"}, {"name": "Charlie"}])

# Access by index
print(lst[0])    # Output: {'name': 'Alice'}
print(lst[-1])   # Output: {'name': 'Charlie'}

# Iterate (just like list)
for item in lst:
    print(item)

# Update by index
lst[0] = {"name": "Alice2"}

# Delete by index
del lst[1]

# Pop last item
item = lst.pop()

# Reverse in place
lst.reverse()

# Compact to remove deleted records
lst.compact()
```

## How It Works

### Storage Format
Data is stored in JSON Lines format (one JSON object per line, separated by newline):

```
{"id": 1, "name": "Alice"}
{"id": 2, "name": "Bob"}
{"id": 1, "name": "Alice2"}
```

### Indexing
An index file (`*.jsonl.idx`) is maintained using pickle for O(1) lookups:

- **JLFDict**: Maps keys to file offsets
- **JLFList**: Maps indices to file offsets

### Delete/Update Strategy
When you delete or update a record:
1. A deletion marker is appended to the file
2. For updates, a new record is also appended
3. Index is updated accordingly
4. Call `compact()` to clean up (optional, recommended periodically)

## Performance

### Memory Usage
- Only index is kept in memory
- ~100 bytes per record (regardless of data size)
- 10 million records ≈ 1GB RAM

### Benchmark Results
*(Tested on typical dataset of 1000 records)*

| Operation | Time |
|-----------|------|
| Insert 1000 items | < 1s |
| Read 1000 items | < 0.1s |
| Update 1000 items | < 1s |
| Delete 1000 items | < 1s |
| Compact | < 0.5s |

### Comparison with dict/list

| Feature | dict/list | JLFDict/JLFList |
|---------|-----------|-----------------|
| Memory | All in RAM | Index only |
| Max Size | Limited by RAM | Limited by disk |
| Read Speed | Faster | Fast (seek + read) |
| Write Speed | Faster | Fast (append + index) |
| Persistence | Manual | Automatic |
| Compact | N/A | Required periodically |

## API Reference

### JLFDict

#### Constructor
```python
JLFDict(file_path, key_field, auto_save_index=True)
```

- `file_path`: Path to JSONL file
- `key_field`: Field name to use as key
- `auto_save_index`: Automatically save index on changes

#### Methods
- `__getitem__(key)`: Get value by key
- `__setitem__(key, value)`: Set value by key
- `__delitem__(key)`: Delete key
- `get(key, default=None)`: Get with default
- `keys()`: Get keys view
- `values()`: Get values view  
- `items()`: Get items view
- `pop(key, default)`: Pop and return value
- `update(other)`: Update with dict/iterable
- `clear()`: Clear all data
- `compact()`: Clean up deleted records

### JLFList

#### Constructor
```python
JLFList(file_path, auto_save_index=True)
```

- `file_path`: Path to JSONL file
- `auto_save_index`: Automatically save index on changes

#### Methods
- `__getitem__(index)`: Get value by index
- `__setitem__(index, value)`: Set value by index
- `__delitem__(index)`: Delete by index
- `append(value)`: Append value
- `extend(values)`: Extend with iterable
- `pop(index)`: Pop and return value
- `reverse()`: Reverse in place
- `clear()`: Clear all data
- `compact()`: Clean up deleted records

## Best Practices

1. **Use `compact()` periodically** - Call after many delete/update operations
2. **Choose appropriate keys** - Use unique, stable keys for JLFDict
3. **Batch operations** - Use `update()`/`extend()` for better performance
4. **Monitor file size** - Large files still benefit from compaction
5. **Backup before compact** - Compact rewrites the file

## Limitations

- No `insert()` for JLFList (not supported in append-only format)
- Modify operations append to file (call `compact()` periodically)
- Not thread-safe (use locks in multi-threaded environments)
- Requires disk I/O (slower than in-memory dict/list)

## Requirements

- Python 3.8+
- No external dependencies!

## Testing

Run tests with pytest:

```bash
# Install dev dependencies
pip install pytest

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_jlf_dict.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Author

Your Name - your.email@example.com

## Acknowledgments

- Inspired by JSON Lines (jsonlines.org)
- Built with Python's collections.abc for duck typing

## See Also

- [COMPARISON.md](COMPARISON.md) - Compare with similar libraries (shelve, tinydb, pandas, etc.)
- [USABILITY.md](USABILITY.md) - Usability comparison and ease of use analysis
- [memory_demo.py](memory_demo.py) - Run memory usage demonstration
- [usability_demo.py](usability_demo.py) - Run usability comparison demonstration
- [jsonlines](https://jsonlines.org/) - JSON Lines specification
- [pandas](https://pandas.pydata.org/) - For data analysis (memory-efficient modes)

## Changelog

### v0.1.0 (2024)
- Initial release
- JLFDict with full dict-like interface
- JLFList with full list-like interface  
- Index persistence
- Compact operation
- Comprehensive test coverage
