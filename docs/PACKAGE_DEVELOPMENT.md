# Dawn Framework: Development Guide

This guide provides instructions for developers working on the Dawn framework before its official release.

## Current Development Setup

While working on the framework before the official release, we've implemented several approaches to handle Python module imports and testing:

### 1. Development Installation

The most reliable way to develop the framework is using a development installation:

```bash
# From the project root
pip install -e .
```

This allows you to import the package modules normally in your code and tests, and any changes you make to the code will be immediately available without reinstallation.

### 2. Using Run Scripts

If you don't want to install the package, you can use the provided run scripts:

* For examples:
  ```bash
  ./run_example.sh examples/your_example.py
  ```

* For tests:
  ```bash
  ./run_tests.sh
  ```

These scripts set up the Python environment correctly before running your code.

### 3. Manual PYTHONPATH Setup

You can also manually set the PYTHONPATH when running code:

```bash
PYTHONPATH=/path/to/dawn python your_script.py
```

## Directory Structure

Current project structure:

```
dawn/
├── setup.py                 # Basic package setup
├── conftest.py              # Pytest configuration
├── pytest.ini               # Pytest settings
├── run_tests.sh             # Test runner script
├── run_example.sh           # Example runner script
├── core/                    # Core functionality
│   └── tools/               # Tool infrastructure
│       └── registry.py      # Tool registry
├── tools/                   # Tool implementations
│   ├── openai_vs/           # OpenAI Vector Store tools
│   │   ├── utils/           # Utilities for vector stores
│   │   │   └── vs_id_validator.py # Vector store ID validation
│   │   ├── create_vector_store.py # Create vector store tool
│   │   └── ...              # Other vector store tools
│   ├── vector_store_tool.py # Legacy vector store tool
│   └── write_markdown_tool.py # Markdown writing tool
├── tests/                   # Test suite
│   ├── openai_vs/           # Tests for vector store tools
│   │   └── ...
│   └── ...                  # Other tests
├── examples/                # Example scripts
│   └── ...
└── fixes/                   # Documentation for common issues and fixes
    ├── vector_store_id_validation.md
    ├── pytest_fixes.md
    └── python_module_import_fix.md
```

## Testing

### Running Tests

To run the test suite:

```bash
# Run all tests
./run_tests.sh

# Run a specific test file
python -m pytest tests/test_file.py -v

# Run a specific test class or method
python -m pytest tests/test_file.py::TestClass::test_method -v
```

### Writing Tests

When writing new tests:

1. Use pytest fixtures where appropriate
2. Mock external services (like OpenAI API)
3. Use temporary directories for file operations
4. Properly test both success and error cases

Example:

```python
import pytest
from dawn.tools.some_tool import SomeTool

@pytest.fixture
def tool():
    return SomeTool()

def test_some_functionality(tool):
    result = tool.do_something()
    assert result is not None
    # More assertions...
```

## Code Style and Quality

### Consistent Error Handling

- Raise exceptions instead of returning error messages
- Use specific exception types when possible
- Document exceptions in function docstrings

### Type Hints

- Use type hints for all function parameters and return values
- Use Optional[] for parameters that can be None
- Use Union[] for parameters that can be different types

### Docstrings

- Use consistent docstring format (Google or Numpy style)
- Document all parameters, return values, and exceptions
- Include examples for complex functions

## Configuration Management

Currently, configuration is loaded from environment variables or `.env` files. In the future, a more robust configuration system will be implemented as described in the release packaging guide.

## Debugging Tips

- Use `print()` statements or logging for debugging
- For API issues, enable logging for HTTP requests:
  ```python
  import logging
  logging.basicConfig(level=logging.DEBUG)
  ```
  
- Test tools with simplified inputs first before integrating them

## Common Issues and Solutions

See the `fixes/` directory for detailed solutions to common issues:

- `fixes/pytest_fixes.md` - How to fix pytest-related issues
- `fixes/python_module_import_fix.md` - How to fix import issues
- `fixes/vector_store_id_validation.md` - Issues with vector store ID validation 