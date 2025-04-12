"""
Simple script to verify the plugin manager error handling.
"""

import sys
import os
import unittest
from unittest.mock import patch

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.tools.plugin_manager import PluginManager


def test_plugin_manager_error():
    """Test that load_plugins_from_namespace raises ValueError for invalid namespaces."""
    # Create a plugin manager
    plugin_manager = PluginManager()
    
    print("Testing PluginManager.load_plugins_from_namespace with invalid namespace...")
    
    # Mock importlib.import_module to raise ImportError
    with patch('importlib.import_module', side_effect=ImportError("No module named 'invalid_namespace'")):
        try:
            # This should raise ValueError
            plugin_manager.load_plugins_from_namespace("invalid_namespace", {})
            print("FAIL: Expected ValueError was not raised!")
            return False
        except ValueError as e:
            print(f"SUCCESS: ValueError raised as expected: {e}")
            return True
        except Exception as e:
            print(f"FAIL: Unexpected exception raised: {type(e).__name__}: {e}")
            return False


if __name__ == "__main__":
    success = test_plugin_manager_error()
    sys.exit(0 if success else 1) 