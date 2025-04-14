#!/usr/bin/env python3
"""
Simple test script to verify variable_resolver imports.
"""  # noqa: D202

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from core.utils.variable_resolver import resolve_path
    print("Import successful! resolve_path function is available.")
    
    # Test with a simple example
    test_data = {"task1": {"output_data": {"result": "Hello, world!"}}}
    result = resolve_path(test_data, "task1.output_data.result")
    print(f"Test successful! Result: {result}")
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Error during testing: {e}") 