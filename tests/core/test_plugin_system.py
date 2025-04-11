"""
Tests for the plugin system for tool execution.
"""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from core.tools.plugin import ToolPlugin
from core.tools.plugin_manager import PluginManager
from core.tools.registry import ToolRegistry


# Create a simple test plugin for testing
class TestPlugin(ToolPlugin):
    """A test plugin for unit testing."""  # noqa: D202
    
    @property
    def tool_name(self) -> str:
        return "test_tool"
    
    @property
    def description(self) -> str:
        return "A test tool for unit testing"
    
    @property
    def required_parameters(self) -> list:
        return ["param1"]
    
    @property
    def optional_parameters(self) -> dict:
        return {"param2": "default_value"}
    
    def execute(self, **kwargs) -> str:
        param1 = kwargs.get("param1")
        param2 = kwargs.get("param2", "default_value")
        return f"Executed with param1={param1}, param2={param2}"


class TestPluginBase(unittest.TestCase):
    """Test the base ToolPlugin class."""  # noqa: D202
    
    def test_plugin_base(self):
        """Test the base plugin functionality."""
        plugin = TestPlugin()
        
        # Test basic properties
        self.assertEqual(plugin.tool_name, "test_tool")
        self.assertEqual(plugin.description, "A test tool for unit testing")
        self.assertEqual(plugin.required_parameters, ["param1"])
        self.assertEqual(plugin.optional_parameters, {"param2": "default_value"})
        
        # Test parameter validation
        with self.assertRaises(ValueError):
            # Missing required parameter
            plugin.validate_parameters(param2="value2")
        
        # Test parameter validation with defaults
        params = plugin.validate_parameters(param1="value1")
        self.assertEqual(params["param1"], "value1")
        self.assertEqual(params["param2"], "default_value")
        
        # Test parameter validation with overrides
        params = plugin.validate_parameters(param1="value1", param2="custom")
        self.assertEqual(params["param1"], "value1")
        self.assertEqual(params["param2"], "custom")
        
        # Test execution
        result = plugin.execute(param1="value1")
        self.assertEqual(result, "Executed with param1=value1, param2=default_value")
        
        # Test metadata
        metadata = plugin.get_metadata()
        self.assertEqual(metadata["name"], "test_tool")
        self.assertEqual(metadata["description"], "A test tool for unit testing")
        self.assertEqual(metadata["required_parameters"], ["param1"])
        self.assertEqual(metadata["optional_parameters"], {"param2": "default_value"})


class TestPluginManager(unittest.TestCase):
    """Test the plugin manager functionality."""  # noqa: D202
    
    def setUp(self):
        """Set up a test environment."""
        self.plugin_manager = PluginManager()
    
    @patch("importlib.import_module")
    @patch("pkgutil.iter_modules")
    @patch("inspect.getmembers")
    def test_discover_plugins(self, mock_getmembers, mock_iter_modules, mock_import_module):
        """Test plugin discovery functionality."""
        # Set up mocks
        mock_module = MagicMock()
        mock_module.__path__ = ["/path/to/package"]
        mock_module.__name__ = "test_package"
        mock_import_module.return_value = mock_module
        
        mock_iter_modules.return_value = [
            (None, "test_package.module1", False),
            (None, "test_package.module2", True),  # This is a package, should be skipped
        ]
        
        # Mock the imported module
        mock_module1 = MagicMock()
        # When module1 is imported, return mock_module1
        mock_import_module.side_effect = [mock_module, mock_module1]
        
        # Set up the class discovery
        mock_getmembers.return_value = [
            ("SomeClass", TestPlugin),
            ("NotAPlugin", object)
        ]
        
        # Test the discovery
        discovered = self.plugin_manager.discover_plugins("test_package")
        
        # Verify the results
        self.assertEqual(len(discovered), 1)
        self.assertEqual(discovered[0], TestPlugin)
        
        # Verify the expected calls
        mock_import_module.assert_any_call("test_package")
        mock_import_module.assert_any_call("test_package.module1")
        mock_iter_modules.assert_called_once_with(["/path/to/package"], "test_package.")


class TestToolRegistry(unittest.TestCase):
    """Test the integration of plugins with the ToolRegistry."""  # noqa: D202
    
    def test_register_and_execute_plugin(self):
        """Test registering and executing a plugin through the registry."""
        registry = ToolRegistry()
        
        # Create a test plugin and use it to verify registration
        test_plugin = TestPlugin()
        
        # Directly register the plugin in the registry's plugin manager
        registry.plugin_manager.plugins[test_plugin.tool_name] = test_plugin
        
        # Load the plugins into the registry
        registry.load_plugins()
        
        # Verify the plugin is registered as a tool
        tool = registry.get_tool("test_tool")
        self.assertIsNotNone(tool)
        
        # Execute the tool
        result = registry.execute_tool("test_tool", {"param1": "test_value"})
        
        # Verify the result
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], "Executed with param1=test_value, param2=default_value")
        
        # Test error handling
        result = registry.execute_tool("test_tool", {"wrong_param": "value"})
        self.assertFalse(result["success"])
        self.assertIn("Missing required parameter", result["error"])


if __name__ == "__main__":
    unittest.main() 