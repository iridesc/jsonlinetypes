#!/usr/bin/env python3
"""
JsonLineTypes - Usage Examples
"""

from jsonlinetypes import JLFDict, JLFList
import tempfile
import os

print("=" * 60)
print("JsonLineTypes - Memory Efficient Dict and List for JSONL")
print("=" * 60)

# Example 1: JLFDict
print("\n--- Example 1: JLFDict ---")
temp_file = tempfile.mkstemp(suffix='.jsonl')[1]

try:
    # Create a dictionary backed by JSONL
    d = JLFDict(temp_file, "user_id")
    
    # Add data
    d["a"] = {"user_id": "a", "name": "Alice", "age": 30}
    d["b"] = {"user_id": "b", "name": "Bob", "age": 25}
    d["c"] = {"user_id": "c", "name": "Charlie", "age": 35}
    
    print(f"Added 3 users, total: {len(d)}")
    
    # Access data
    print(f"User a: {d.get('a')}")
    
    # Update data
    d["a"] = {"user_id": "a", "name": "Alice Smith", "age": 31}
    print(f"Updated user a: {d['a']}")
    
    # Delete data
    del d["b"]
    print(f"After deleting user b, total: {len(d)}")
    
    # Iterate
    print("\nAll users:")
    for user_id, user in d.items():
        print(f"  {user_id}: {user['name']} (age {user['age']})")
    
    # Batch update
    d.update({"d": {"user_id": "d", "name": "David", "age": 28}})
    print(f"\nAfter batch update, total: {len(d)}")
    
    # Cleanup
    d.clear()
    print(f"After clear, total: {len(d)}")

finally:
    # Cleanup temp files
    for ext in ['', '.idx', '.idx.del']:
        if os.path.exists(temp_file + ext):
            os.remove(temp_file + ext)

# Example 2: JLFList
print("\n--- Example 2: JLFList ---")
temp_file = tempfile.mktemp(suffix='.jsonl')

try:
    # Create a list backed by JSONL
    lst = JLFList(temp_file)
    
    # Add items
    lst.append({"name": "Alice", "score": 95})
    lst.append({"name": "Bob", "score": 88})
    lst.append({"name": "Charlie", "score": 92})
    
    print(f"Added 3 students, total: {len(lst)} {lst=}")
    print(lst)
    
    # Batch add
    lst.extend([
        {"name": "David", "score": 85},
        {"name": "Eve", "score": 90}
    ])
    print(f"After extend, total: {len(lst)}")
    print(lst)
    
    # Access by index
    print(f"\nFirst student: {lst[0]}")
    print(f"Last student: {lst[-1]}")
    
    # Update
    lst[0] = {"name": "Alice Smith", "score": 96}
    print(f"Updated first student: {lst[0]}")
    
    # Delete
    del lst[1]
    print(f"After deleting index 1, total: {len(lst)}")
    print(f"Now at index 1: {lst[1]}")
    print(lst)
    
    # Pop
    removed = lst.pop()
    print(f"Removed last student: {removed}")
    print(f"Total after pop: {len(lst)}")
    
    # Iterate
    print("\nAll students:")
    for i, student in enumerate(lst):
        print(f"  {i}: {student['name']} (score {student['score']})")
    
    # Reverse
    lst.reverse()
    print(f"\nAfter reverse, first student: {lst[0]['name']}")
    print(lst)
    # Cleanup
    lst.clear()
    print(f"After clear, total: {len(lst)}")

finally:
    # Cleanup temp files
    for ext in ['', '.idx']:
        if os.path.exists(temp_file + ext):
            os.remove(temp_file + ext)

print("\n" + "=" * 60)
print("Examples completed successfully!")
print("=" * 60)


