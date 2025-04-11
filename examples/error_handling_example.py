"""
Example demonstrating the standardized error handling system in Dawn framework.

This example shows how to implement a tool handler that uses the standardized
error response format and various utilities for error handling.
"""

import os
import sys
import logging
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.errors import (
    DawnError, 
    ValidationError, 
    ExecutionError, 
    ResourceError, 
    ErrorCode,
    main_wrapper,
    ExitCodes
)
from core.tools.response_format import (
    standardize_tool_response,
    validate_tool_input,
    format_tool_response,
    with_warning,
    create_error_response,
    create_success_response
)
from core.tools.registry_access import register_tool, execute_tool, get_available_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Example 1: Simple tool handler with manual error handling
def calculator_tool_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    A simple calculator tool handler with manual error handling.
    
    Args:
        input_data: Dictionary containing operation and operands
        
    Returns:
        Standardized response dictionary
    """
    try:
        # Validate required fields
        if "operation" not in input_data:
            return create_error_response(
                message="Missing required field: 'operation'",
                error_code=ErrorCode.VALIDATION_MISSING_FIELD,
                details={"field_name": "operation"}
            )
        
        # Get operation and operands
        operation = input_data.get("operation")
        a = input_data.get("a")
        b = input_data.get("b")
        
        # Validate operation type
        valid_operations = ["add", "subtract", "multiply", "divide"]
        if operation not in valid_operations:
            return create_error_response(
                message=f"Invalid operation: '{operation}'. Must be one of: {', '.join(valid_operations)}",
                error_code=ErrorCode.VALIDATION_INVALID_VALUE,
                details={
                    "field_name": "operation",
                    "received_value": operation,
                    "allowed_values": valid_operations
                }
            )
        
        # Validate operands
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            return create_error_response(
                message="Operands 'a' and 'b' must be numbers",
                error_code=ErrorCode.VALIDATION_INVALID_TYPE,
                details={
                    "field_a_type": type(a).__name__,
                    "field_b_type": type(b).__name__,
                    "expected_type": "int or float"
                }
            )
        
        # Perform the operation
        result = None
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                return create_error_response(
                    message="Division by zero is not allowed",
                    error_code=ErrorCode.VALIDATION_INVALID_VALUE,
                    details={"field_name": "b", "received_value": b}
                )
            result = a / b
        
        # Return success response
        return create_success_response(
            result=result,
            message=f"Operation '{operation}' completed successfully",
            metadata={"operation": operation, "a": a, "b": b}
        )
    
    except Exception as e:
        # Handle unexpected exceptions
        return create_error_response(
            message=f"Calculator tool failed: {str(e)}",
            error_code=ErrorCode.EXECUTION_TOOL_FAILED,
            details={"error_type": type(e).__name__}
        )


# Example 2: Using the standardize_tool_response decorator
@standardize_tool_response
def addition_tool_handler(input_data: Dict[str, Any]) -> Any:
    """
    A simple addition tool handler using the standardize_tool_response decorator.
    
    Args:
        input_data: Dictionary containing numbers to add
        
    Returns:
        Result that will be automatically formatted as a standardized response
    """
    # Check for required field
    if "numbers" not in input_data:
        raise ValidationError(
            message="Missing required field: 'numbers'",
            error_code=ErrorCode.VALIDATION_MISSING_FIELD,
            field_name="numbers"
        )
    
    numbers = input_data.get("numbers", [])
    
    # Validate numbers field
    if not isinstance(numbers, list):
        raise ValidationError(
            message="Field 'numbers' must be a list",
            error_code=ErrorCode.VALIDATION_INVALID_TYPE,
            field_name="numbers",
            expected_type="list",
            received_value=numbers
        )
    
    # Validate all items are numbers
    non_numbers = [x for x in numbers if not isinstance(x, (int, float))]
    if non_numbers:
        raise ValidationError(
            message="All items in 'numbers' must be numbers",
            error_code=ErrorCode.VALIDATION_INVALID_TYPE,
            field_name="numbers",
            expected_type="list of numbers",
            received_value=non_numbers
        )
    
    # Perform the addition
    total = sum(numbers)
    
    # Return the result (will be automatically formatted)
    return total


# Example 3: Using the validate_tool_input decorator
@validate_tool_input(
    schema={
        "file_path": {"type": str},
        "content": {"type": str}
    },
    required_fields=["file_path"]
)
@standardize_tool_response
def file_writer_tool_handler(input_data: Dict[str, Any]) -> Any:
    """
    A tool handler that writes content to a file,
    using the validate_tool_input decorator for input validation.
    
    Args:
        input_data: Dictionary containing file_path and content
        
    Returns:
        Result that will be automatically formatted as a standardized response
    """
    file_path = input_data["file_path"]  # We know this exists due to validation
    content = input_data.get("content", "")  # Default to empty string
    
    try:
        # Check if the directory exists
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            raise ResourceError(
                message=f"Directory does not exist: {directory}",
                error_code=ErrorCode.RESOURCE_NOT_FOUND,
                resource_type="directory",
                resource_id=directory
            )
        
        # Write the file
        with open(file_path, "w") as f:
            f.write(content)
        
        # Return success with file size
        return {
            "file_path": file_path,
            "size_bytes": len(content),
            "status": "written"
        }
    
    except ResourceError as e:
        # Re-raise ResourceError
        raise e
    except Exception as e:
        # Handle other exceptions
        raise ExecutionError(
            message=f"Failed to write to file: {str(e)}",
            error_code=ErrorCode.EXECUTION_TOOL_FAILED,
            cause=e
        )


# Example 4: Returning a warning response
@standardize_tool_response
def data_processor_tool_handler(input_data: Dict[str, Any]) -> Any:
    """
    A tool handler that processes data with potential warnings.
    
    Args:
        input_data: Dictionary containing data to process
        
    Returns:
        Result with potential warnings
    """
    data = input_data.get("data", [])
    if not data:
        raise ValidationError(
            message="Missing or empty 'data' field",
            error_code=ErrorCode.VALIDATION_MISSING_FIELD,
            field_name="data"
        )
    
    # Process the data
    processed_data = []
    skipped_items = []
    
    for item in data:
        if isinstance(item, (int, float, str, bool, dict, list)):
            # Process the item
            processed_data.append(item)
        else:
            # Skip unsupported types
            skipped_items.append({
                "item": str(item),
                "type": type(item).__name__
            })
    
    # If we skipped some items, return a warning
    if skipped_items:
        return with_warning(
            result=processed_data,
            warning=f"Skipped {len(skipped_items)} items with unsupported types",
            warning_code="UNSUPPORTED_DATA_TYPES",
            details={"skipped_items": skipped_items}
        )
    
    # Otherwise return success
    return processed_data


# Register all the example tools
def register_example_tools():
    """Register all the example tools with the registry."""
    register_tool("calculator", calculator_tool_handler, replace=True)
    register_tool("addition", addition_tool_handler, replace=True)
    register_tool("file_writer", file_writer_tool_handler, replace=True)
    register_tool("data_processor", data_processor_tool_handler, replace=True)


# Test all the tools
def test_calculator_tool():
    """Test the calculator tool."""
    logger.info("\n=== Testing Calculator Tool ===")
    
    # Test valid addition
    result = execute_tool("calculator", {
        "operation": "add",
        "a": 5,
        "b": 3
    })
    logger.info(f"Addition result: {result}")
    
    # Test missing operation
    result = execute_tool("calculator", {
        "a": 5,
        "b": 3
    })
    logger.info(f"Missing operation: {result}")
    
    # Test invalid operation
    result = execute_tool("calculator", {
        "operation": "square",
        "a": 5,
        "b": 3
    })
    logger.info(f"Invalid operation: {result}")
    
    # Test division by zero
    result = execute_tool("calculator", {
        "operation": "divide",
        "a": 5,
        "b": 0
    })
    logger.info(f"Division by zero: {result}")


def test_addition_tool():
    """Test the addition tool."""
    logger.info("\n=== Testing Addition Tool ===")
    
    # Test valid addition
    result = execute_tool("addition", {
        "numbers": [1, 2, 3, 4, 5]
    })
    logger.info(f"Addition result: {result}")
    
    # Test missing numbers field
    result = execute_tool("addition", {})
    logger.info(f"Missing numbers: {result}")
    
    # Test invalid numbers field
    result = execute_tool("addition", {
        "numbers": "not a list"
    })
    logger.info(f"Invalid numbers type: {result}")
    
    # Test non-number elements
    result = execute_tool("addition", {
        "numbers": [1, 2, "3", 4, 5]
    })
    logger.info(f"Non-number elements: {result}")


def test_file_writer_tool():
    """Test the file writer tool."""
    logger.info("\n=== Testing File Writer Tool ===")
    
    # Test writing to a file
    temp_file = os.path.join(os.getcwd(), "test_output.txt")
    result = execute_tool("file_writer", {
        "file_path": temp_file,
        "content": "This is a test file."
    })
    logger.info(f"Write file result: {result}")
    
    # Test missing file_path
    result = execute_tool("file_writer", {
        "content": "This is a test file."
    })
    logger.info(f"Missing file_path: {result}")
    
    # Test invalid directory
    result = execute_tool("file_writer", {
        "file_path": "/invalid/directory/test.txt",
        "content": "This is a test file."
    })
    logger.info(f"Invalid directory: {result}")
    
    # Clean up the temp file
    if os.path.exists(temp_file):
        os.remove(temp_file)


def test_data_processor_tool():
    """Test the data processor tool."""
    logger.info("\n=== Testing Data Processor Tool ===")
    
    # Test with all valid data
    result = execute_tool("data_processor", {
        "data": [1, 2, 3, "string", True, {"key": "value"}, [1, 2, 3]]
    })
    logger.info(f"All valid data: {result}")
    
    # Test with some invalid data
    class CustomType:
        pass
    
    # We can't directly pass a CustomType to execute_tool as it can't be JSON serialized,
    # so we'll use a placeholder string instead for the example
    result = execute_tool("data_processor", {
        "data": [1, 2, 3, "custom_type_placeholder"]
    })
    logger.info(f"Some invalid data (simulated): {result}")
    
    # Test with empty data
    result = execute_tool("data_processor", {
        "data": []
    })
    logger.info(f"Empty data: {result}")
    
    # Test with no data field
    result = execute_tool("data_processor", {})
    logger.info(f"No data field: {result}")


@main_wrapper
def main():
    """
    Main function that demonstrates all the examples.
    
    This function is wrapped with the main_wrapper decorator to catch
    all exceptions and return appropriate exit codes.
    """
    logger.info("Starting error handling example...")
    
    # Register the example tools
    register_example_tools()
    
    # List available tools
    tools = get_available_tools()
    logger.info(f"Available tools: {[t['name'] for t in tools]}")
    
    # Test all the tools
    test_calculator_tool()
    test_addition_tool()
    test_file_writer_tool()
    test_data_processor_tool()
    
    logger.info("\nAll tests completed successfully!")
    return ExitCodes.SUCCESS


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
