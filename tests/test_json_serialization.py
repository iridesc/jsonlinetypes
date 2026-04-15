#!/usr/bin/env python3
"""
测试 JSON 序列化修复方案
"""

import sys
sys.path.insert(0, '.')
import tempfile
import json
import os
from jsonlinetypes import JLFDict, JLFList, JLFEncoder

print("=" * 80)
print("测试 JSON 序列化修复")
print("=" * 80)

# 测试 1: 使用 JLFEncoder 序列化 JLFList
print("\n【测试1】使用 JLFEncoder 序列化 JLFList")
print("-" * 80)

fd, path = tempfile.mkstemp(suffix='.jsonl')
os.close(fd)

try:
    lst = JLFList(path)
    lst.append({"name": "Alice"})
    lst.append({"name": "Bob"})

    # 使用自定义 encoder
    data = {"assets": lst, "count": len(lst)}
    json_str = json.dumps(data, cls=JLFEncoder, indent=2)

    print("✅ 序列化成功:")
    print(json_str)

    # 验证
    parsed = json.loads(json_str)
    assert parsed["count"] == 2
    assert parsed["assets"][0]["name"] == "Alice"
    print("✅ 反序列化验证通过")

finally:
    for f in [path, path + ".idx"]:
        if os.path.exists(f):
            os.remove(f)

# 测试 2: 使用 JLFEncoder 序列化 JLFDict
print("\n【测试2】使用 JLFEncoder 序列化 JLFDict")
print("-" * 80)

fd, path = tempfile.mkstemp(suffix='.jsonl')
os.close(fd)

try:
    d = JLFDict(path, "id")
    d[1] = {"id": 1, "name": "Alice"}
    d[2] = {"id": 2, "name": "Bob"}

    # 使用自定义 encoder
    data = {"users": d, "total": len(d)}
    json_str = json.dumps(data, cls=JLFEncoder, indent=2)

    print("✅ 序列化成功:")
    print(json_str)

    # 验证
    parsed = json.loads(json_str)
    assert parsed["total"] == 2
    assert parsed["users"]["1"]["name"] == "Alice"  # JSON 键必须是字符串
    print("✅ 反序列化验证通过")

finally:
    for f in [path, path + ".idx", path + ".idx.del"]:
        if os.path.exists(f):
            os.remove(f)

# 测试 3: 混合使用
print("\n【测试3】混合使用 JLFDict 和 JLFList")
print("-" * 80)

fd, list_path = tempfile.mkstemp(suffix='_list.jsonl')
os.close(fd)
fd, dict_path = tempfile.mkstemp(suffix='_dict.jsonl')
os.close(fd)

try:
    lst = JLFList(list_path)
    lst.append({"name": "Alice"})

    d = JLFDict(dict_path, "id")
    d[1] = {"id": 1, "value": "test"}

    data = {
        "list_data": lst,
        "dict_data": d,
        "metadata": {"version": "1.0"}
    }

    json_str = json.dumps(data, cls=JLFEncoder, indent=2)

    print("✅ 混合序列化成功:")
    print(json_str)

    parsed = json.loads(json_str)
    assert len(parsed["list_data"]) == 1
    assert len(parsed["dict_data"]) == 1
    print("✅ 反序列化验证通过")

finally:
    for f in [list_path, list_path + ".idx", dict_path, dict_path + ".idx", dict_path + ".idx.del"]:
        if os.path.exists(f):
            os.remove(f)

print("\n" + "=" * 80)
print("所有测试通过！JLFEncoder 解决了 JSON 序列化问题")
print("=" * 80)

print("""
【如何使用】

方法1: 在 json.dumps 时指定 cls 参数
```python
from jsonlinetypes import JLFEncoder

data = {"assets": jlf_list}
json_str = json.dumps(data, cls=JLFEncoder)
```

方法2: 使用 with 关键字和 custom encoder
```python
import json
from jsonlinetypes import JLFEncoder

with open('output.json', 'w') as f:
    json.dump({"data": jlf_list}, f, cls=JLFEncoder)
```

方法3: 如果你需要兼容其他 JSON 库，可以手动转换
```python
data = {"assets": jlf_list.to_list()}
json_str = json.dumps(data)
```
""")
