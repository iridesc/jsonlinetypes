# Project Structure

## Directory Layout

```
jsonlinetypes/
├── jsonlinetypes/          # Main package code
│   ├── __init__.py
│   ├── jlf_dict.py
│   └── jlf_list.py
├── docs/                   # Documentation
│   ├── README_CN.md
│   ├── PERFORMANCE.md
│   ├── COMPARISON.md
│   ├── USABILITY.md
│   ├── INDEX_RECOVERY.md
│   ├── THREAD_SAFETY.md
│   ├── ARCHITECTURE.md
│   ├── QUICK_START.md
│   ├── CHANGELOG.md
│   ├── TEST_COVERAGE_ANALYSIS.md
│   └── README_COMPARISON.md
├── tests/                  # Test scripts
│   ├── __init__.py
│   ├── test_jlf_dict.py
│   ├── test_jlf_list.py
│   ├── run_tests.py
│   ├── test_index_recovery.py
│   ├── test_list_index_recovery.py
│   └── test_thread_safety.py
├── demos/                  # Example scripts and demos
│   ├── examples.py
│   ├── memory_demo.py
│   ├── usability_demo.py
│   ├── benchmark_safety.py
│   └── demo_thread_safety.py
├── README.md               # Main README (root)
├── LICENSE
├── pyproject.toml
└── ...
```

## Running Tests

Run all tests from the project root:

```bash
# Using run_tests.py
python tests/run_tests.py

# Or with pytest (if installed)
pytest tests/
```

## Running Demos

Run example scripts from the project root:

```bash
# Basic examples
PYTHONPATH=. python demos/examples.py

# Memory usage demo
PYTHONPATH=. python demos/memory_demo.py

# Thread safety demo
PYTHONPATH=. python demos/demo_thread_safety.py

# Performance benchmarks
PYTHONPATH=. python demos/benchmark_safety.py
```

## Documentation

- **README.md** - Main project overview
- **docs/README_CN.md** - Chinese documentation
- **docs/QUICK_START.md** - Quick start guide
- **docs/PERFORMANCE.md** - Performance analysis
- **docs/THREAD_SAFETY.md** - Thread safety guide
- **docs/ARCHITECTURE.md** - Architecture details
