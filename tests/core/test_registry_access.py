#!/usr/bin/env python
"""
Tests for the standardized ToolRegistry access module.
"""  # noqa: D202

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from core.tools.registry_access import (
    get_registry,
    reset_registry,
    register_tool,
    execute_tool,
    get_available_tools,
    tool_exists,
    load_plugins,
    register_plugin_namespace
)
from core.tools.registry import ToolRegistry


class TestRegistryAccess(unittest.TestCase):
    """Tests for the registry_access module."""  # noqa: D202

    def setUp(self):
        """Set up for each test."""
        # Reset the registry before each test
        reset_registry()

    def test_singleton_pattern(self):
        """Test that get_registry returns the same instance each time."""
        # Get the registry twice
        registry1 = get_registry()
        registry2 = get_registry()
        
        # Check that they're the same instance
        self.assertIs(registry1, registry2)
        
        # Reset and check that we get a new instance
        reset_registry()
        registry3 = get_registry()
        self.assertIsNot(registry1, registry3)

    def test_register_tool(self):
        """Test registering a tool with the registry."""
        # Create a simple handler function
        def dummy_handler(input_data):
            return {"success": True, "result": input_data}
        
        # Register the tool
        result = register_tool("test_tool", dummy_handler)
        self.assertTrue(result)
        
        # Check that the tool was registered
        self.assertTrue(tool_exists("test_tool"))
        
        # Try to register the same tool again (should fail)
        result = register_tool("test_tool", dummy_handler)
        self.assertFalse(result)
        
        # Try to register the same tool again with replace=True (should succeed)
        result = register_tool("test_tool", dummy_handler, replace=True)
        self.assertTrue(result)

    def test_execute_tool(self):
        """Test executing a tool through the registry."""
        # Create a simple handler function
        def dummy_handler(input_data):
            return {"success": True, "result": input_data.get("value", "default")}
        
        # Register the tool
        register_tool("test_tool", dummy_handler)
        
        # Execute the tool
        result = execute_tool("test_tool", {"value": "test_value"})
        
        # Check the result
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], "test_value")
        
        # Try to execute a non-existent tool
        result = execute_tool("non_existent_tool", {})
        self.assertFalse(result["success"])
        self.assertEqual(result["error_type"], "ToolNotFound")

    def test_get_available_tools(self):
        """Test getting a list of available tools."""
        # Initially, there should be no tools
        tools = get_available_tools()
        self.assertEqual(len(tools), 0)
        
        # Register a tool
        def dummy_handler(input_data):
            return {"success": True}
        
        register_tool("test_tool", dummy_handler)
        
        # Now there should be one tool
        tools = get_available_tools()
        self.assertEqual(len(tools), 1)
        self.assertIn("test_tool", tools)

    def test_tool_exists(self):
        """Test checking if a tool exists."""
        # Initially, no tools exist
        self.assertFalse(tool_exists("test_tool"))
        
        # Register a tool
        def dummy_handler(input_data):
            return {"success": True}
        
        register_tool("test_tool", dummy_handler)
        
        # Now the tool should exist
        self.assertTrue(tool_exists("test_tool"))

    @patch('core.tools.registry.ToolRegistry.load_plugins')
    def test_load_plugins(self, mock_load_plugins):
        """Test loading plugins."""
        # Call the load_plugins function
        load_plugins()
        
        # Check that the underlying method was called
        mock_load_plugins.assert_called_once_with(False)
        
        # Call with reload=True
        load_plugins(reload=True)
        
        # Check that the underlying method was called with reload=True
        mock_load_plugins.assert_called_with(True)

    @patch('core.tools.registry.ToolRegistry.register_plugin_namespace')
    def test_register_plugin_namespace(self, mock_register_namespace):
        """Test registering a plugin namespace."""
        # Call the register_plugin_namespace function
        register_plugin_namespace("test_namespace")
        
        # Check that the underlying method was called
        mock_register_namespace.assert_called_once_with("test_namespace")


if __name__ == "__main__":
    unittest.main() 