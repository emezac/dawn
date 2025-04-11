# Python Module Import Fix

## Issue

The project has modules organized in a package structure (`core`, `tools`, etc.), but when running scripts directly or using pytest, Python can't find these modules. This results in errors like:

```
ModuleNotFoundError: No module named 'core'
```

This happens because:
1. Python's module search path doesn't include the project root by default
2. The project isn't installed as a package
3. The import statements assume the module is in the Python path

## Solutions

### Solution 1: Install the Package in Development Mode

The most robust solution is to install the package in development mode:

```bash
cd /path/to/project
pip install -e .
```

This adds the package to your Python environment while allowing you to continue editing the code.

### Solution 2: Use the Run Scripts

Use the provided scripts that set up the correct PYTHONPATH:

For running tests:
```bash
./run_tests.sh
```

For running examples:
```bash
./run_example.sh examples/context_aware_legal_review_workflow.py
```

### Solution 3: Set PYTHONPATH Manually

Set the PYTHONPATH environment variable before running your script:

```bash
PYTHONPATH=/path/to/project python examples/context_aware_legal_review_workflow.py
```

Or in your script, add the project root to sys.path:

```python
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
```

## What We've Added

1. **setup.py**: Properly configured to make the project installable
2. **run_tests.sh**: Sets up the environment for running tests
3. **run_example.sh**: Sets up the environment for running example scripts
4. **conftest.py**: Helps pytest find the modules

## Best Practice

Going forward, we recommend:

1. Always use one of the run scripts to execute examples or tests
2. Install the package in development mode for a more permanent solution
3. When adding new examples, follow the pattern in existing examples, which add the project root to sys.path 