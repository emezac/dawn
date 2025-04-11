#!/usr/bin/env python
"""
Test script for the error handling and response format improvements.
"""  # noqa: D202

import os
import sys
import logging
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import necessary modules
from core.tools.registry_access import get_registry, register_tool, execute_tool
from core.errors import ValidationError, ErrorCode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_error_format")

# Define some test tool functions with different patterns

def no_args_tool():
    """Test tool that takes no arguments."""
    return {"success": True, "result": "No args tool worked"}

def single_arg_tool(data):
    """Test tool that takes a single argument (dict)."""
    return {"success": True, "result": f"Single arg tool worked with: {data}"}

def kwargs_tool(**kwargs):
    """Test tool that takes keyword arguments."""
    return {"success": True, "result": f"Kwargs tool worked with: {kwargs}"}

def error_tool(data):
    """Test tool that returns an error."""
    return {"success": False, "error": "Simulated error", "error_code": "TEST_ERROR"}

def exception_tool(data):
    """Test tool that raises an exception."""
    raise ValueError("Test exception")

def validation_tool(data):
    """Test tool that performs validation."""
    if "required_field" not in data:
        raise ValidationError(
            message="Missing required field",
            error_code=ErrorCode.VALIDATION_MISSING_FIELD,
            field_name="required_field"
        )
    return {"success": True, "result": f"Validation passed for {data['required_field']}"}

def dual_field_tool(data):
    """Test tool that returns both response and result fields."""
    return {
        "success": True,
        "result": "Result value", 
        "response": "Response value"
    }

def register_test_tools():
    """Register all test tools."""
    registry = get_registry()
    registry.register_tool("no_args_tool", no_args_tool)
    registry.register_tool("single_arg_tool", single_arg_tool)
    registry.register_tool("kwargs_tool", kwargs_tool)
    registry.register_tool("error_tool", error_tool)
    registry.register_tool("exception_tool", exception_tool)
    registry.register_tool("validation_tool", validation_tool)
    registry.register_tool("dual_field_tool", dual_field_tool)

def main():
    """Run tests for various tool patterns and error handling cases."""
    register_test_tools()
    logger.info("Testing error handling and response formats")

    # Test tools with different argument patterns
    logger.info("\n=== Testing different function signatures ===")
    result1 = execute_tool("no_args_tool", {})
    logger.info(f"No args tool result: {result1}")

    result2 = execute_tool("single_arg_tool", {"key": "value"})
    logger.info(f"Single arg tool result: {result2}")

    result3 = execute_tool("kwargs_tool", {"key1": "value1", "key2": "value2"})
    logger.info(f"Kwargs tool result: {result3}")

    # Test error handling
    logger.info("\n=== Testing error handling ===")
    result4 = execute_tool("error_tool", {})
    logger.info(f"Error tool result: {result4}")

    result5 = execute_tool("exception_tool", {})
    logger.info(f"Exception tool result: {result5}")

    # Test validation
    logger.info("\n=== Testing validation ===")
    result6 = execute_tool("validation_tool", {"not_required": "value"})
    logger.info(f"Validation tool (missing field) result: {result6}")

    result7 = execute_tool("validation_tool", {"required_field": "value"})
    logger.info(f"Validation tool (with field) result: {result7}")
    
    # Test dual fields
    logger.info("\n=== Testing dual response/result fields ===")
    result8 = execute_tool("dual_field_tool", {})
    logger.info(f"Dual field tool result: {result8}")

    # Verify field presence
    if "result" in result8 and "response" in result8:
        logger.info("✅ Both 'result' and 'response' fields are present")
    else:
        logger.error("❌ Missing either 'result' or 'response' field")

    logger.info("\nAll tests completed!")

if __name__ == "__main__":
    main() 