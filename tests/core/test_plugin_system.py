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
from core.tools.base import BaseTool
from core.tools.registry_access import get_registry, reset_registry


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
    
    def setUp(self):
        """Reset registry for each test."""
        reset_registry() # Reset the singleton instance before each test
        # Mock os.path.dirname to control plugin discovery path
        self.mock_dirname = patch("os.path.dirname").start()
        self.mock_dirname.return_value = "/fake/path"
        # Mock pkgutil.iter_modules to simulate finding modules
        self.mock_iter_modules = patch("pkgutil.iter_modules").start()
        # Mock importlib.import_module to simulate importing modules
        self.mock_import_module = patch("importlib.import_module").start()
        # Mock inspect.getmembers to simulate finding classes
        self.mock_getmembers = patch("inspect.getmembers").start()
        # Mock issubclass to control which classes are treated as plugins
        self.mock_issubclass = patch("builtins.issubclass").start()
        self.mock_logger = patch("core.tools.registry.logger").start()
        
    def tearDown(self):
        """Stop mocks after each test."""
        patch.stopall()

    def test_register_plugin_namespace(self):
        """Test registering a plugin namespace."""
        registry = get_registry() # Use singleton
        registry.register_plugin_namespace("test_plugins")
        self.assertIn("test_plugins", registry.plugin_namespaces)

    @patch("os.path.exists", return_value=True) # Assume namespace directory exists
    def test_load_plugins_single_namespace(self, mock_exists):
        """Test loading plugins from a specific namespace."""
        registry = get_registry() # Use singleton
        registry.register_plugin_namespace("test_plugins") # Register the namespace

        # Simulate finding a module and a plugin class within it
        self.mock_iter_modules.return_value = [(None, "mock_plugin_module", True)]
        mock_module = MagicMock()
        self.mock_import_module.return_value = mock_module
        # Simulate finding the TestPlugin class (must be defined elsewhere)
        self.mock_getmembers.return_value = [("TestPlugin", TestPlugin)] 
        self.mock_issubclass.side_effect = lambda cls, base: cls is TestPlugin and base is BaseTool

        registry.load_plugins(namespace="test_plugins")
        
        self.mock_iter_modules.assert_called_once()
        self.mock_import_module.assert_called_once_with(".mock_plugin_module", package="test_plugins")
        self.mock_getmembers.assert_called_once()
        # Check if tool is registered
        self.assertTrue(registry.tool_exists("test_tool")) 

    @patch("os.path.exists", return_value=True)
    def test_load_plugins_reload(self, mock_exists):
        """Test reloading plugins."""
        registry = get_registry() # Use singleton
        registry.register_plugin_namespace("test_plugins")
        # Simulate loading plugins first time
        self.mock_iter_modules.return_value = [(None, "mock_plugin_module", True)]
        mock_module = MagicMock()
        self.mock_import_module.return_value = mock_module
        self.mock_getmembers.return_value = [("TestPlugin", TestPlugin)]
        self.mock_issubclass.side_effect = lambda cls, base: cls is TestPlugin and base is BaseTool
        registry.load_plugins()
        self.assertTrue(registry.tool_exists("test_tool"))
        
        # Reset mocks for reload call
        self.mock_iter_modules.reset_mock()
        self.mock_import_module.reset_mock()
        self.mock_getmembers.reset_mock()
        self.mock_issubclass.reset_mock()
        # Set side effect again for the second call
        self.mock_issubclass.side_effect = lambda cls, base: cls is TestPlugin and base is BaseTool

        # Reload plugins
        registry.load_plugins(reload=True)
        # Check mocks were called again
        self.mock_iter_modules.assert_called_once()
        self.mock_import_module.assert_called_once_with(".mock_plugin_module", package="test_plugins")
        self.mock_getmembers.assert_called_once()
        # Tool should still exist
        self.assertTrue(registry.tool_exists("test_tool"))

    @patch("os.path.exists", return_value=True)
    def test_execute_plugin_tool(self, mock_exists):
        """Test executing a tool loaded from a plugin."""
        registry = get_registry() # Use singleton
        registry.register_plugin_namespace("test_plugins")
        # Simulate loading plugins
        self.mock_iter_modules.return_value = [(None, "mock_plugin_module", True)]
        mock_module = MagicMock()
        self.mock_import_module.return_value = mock_module
        self.mock_getmembers.return_value = [("TestPlugin", TestPlugin)]
        self.mock_issubclass.side_effect = lambda cls, base: cls is TestPlugin and base is BaseTool
        registry.load_plugins()
        
        # Execute the tool
        result = registry.execute_tool("test_tool", {"param1": "exec_test"})
        self.assertTrue(result["success"])
        self.assertIn("exec_test", result["result"])

    def test_error_on_invalid_namespace(self):
        """Test error when trying to load non-existent namespace."""
        registry = get_registry() # Use singleton
        # Don't register the namespace
        with self.assertRaisesRegex(ValueError, "Namespace 'invalid_namespace' not registered."):
            registry.load_plugins(namespace="invalid_namespace")

    @patch("os.path.exists", return_value=True) # Assume namespace directory exists
    def test_no_plugins_found_warning(self, mock_exists):
        """Test warning when no plugins are found in a namespace."""
        registry = get_registry() # Use singleton
        registry.register_plugin_namespace("empty_plugins") 
        # Simulate finding no modules
        self.mock_iter_modules.return_value = []
        
        registry.load_plugins(namespace="empty_plugins")
        # Check that logger.info was called with a relevant message
        self.mock_logger.info.assert_any_call("No plugins found in namespace 'empty_plugins'.")


if __name__ == "__main__":
    unittest.main() 