#!/usr/bin/env python
"""
Test script for verifying standardized error messages.

This script tests various error scenarios to ensure the error message templates
are properly applied and the error responses are correctly formatted.
"""  # noqa: D202

import os
import sys
import logging
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import our error handling utilities
from core.errors import (
    ErrorCode, 
    ValidationError, 
    ExecutionError, 
    ConnectionError, 
    ResourceError,
    get_error_message,
    create_error_response
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("test_error_messages")

def test_error_templates():
    """Test that error templates can be correctly formatted with context variables."""  # noqa: D202
    
    # Test validation error messages
    validation_message = get_error_message(
        ErrorCode.VALIDATION_MISSING_FIELD,
        field_name="username"
    )
    logger.info(f"Validation Error: {validation_message}")
    
    type_message = get_error_message(
        ErrorCode.VALIDATION_INVALID_TYPE,
        field_name="age",
        expected_type="int",
        received_type="str"
    )
    logger.info(f"Type Error: {type_message}")
    
    # Test execution error messages
    tool_error = get_error_message(
        ErrorCode.EXECUTION_TOOL_FAILED,
        tool_name="file_upload",
        reason="File not found"
    )
    logger.info(f"Tool Error: {tool_error}")
    
    timeout_error = get_error_message(
        ErrorCode.EXECUTION_TIMEOUT,
        timeout=30
    )
    logger.info(f"Timeout Error: {timeout_error}")
    
    # Test resource error messages
    not_found = get_error_message(
        ErrorCode.RESOURCE_NOT_FOUND,
        resource_type="vector_store",
        resource_id="vs_123456"
    )
    logger.info(f"Not Found Error: {not_found}")
    
    # Test handling of missing context variables
    try:
        missing_context = get_error_message(
            ErrorCode.RESOURCE_NOT_FOUND,
            resource_type="vector_store"
            # Missing resource_id
        )
        logger.info(f"Missing Context Error: {missing_context}")
    except Exception as e:
        logger.info(f"Missing Context Exception: {str(e)}")

def test_error_responses():
    """Test that error responses are correctly formatted."""  # noqa: D202
    
    # Test basic error response
    basic_response = create_error_response(
        message="Custom error message",
        error_code=ErrorCode.UNKNOWN_ERROR
    )
    logger.info(f"Basic Error Response: {basic_response}")
    
    # Test error response with context
    context_response = create_error_response(
        error_code=ErrorCode.VALIDATION_MISSING_FIELD,
        field_name="email"
    )
    logger.info(f"Context Error Response: {context_response}")
    
    # Test error response with details
    details_response = create_error_response(
        error_code=ErrorCode.CONNECTION_API_ERROR,
        service_name="OpenAI API",
        reason="Rate limit exceeded",
        details={"retry_after": 30}
    )
    logger.info(f"Details Error Response: {details_response}")
    
    # Test unknown error code
    unknown_code_response = create_error_response(
        error_code="CUSTOM_ERROR_CODE",
        message="This is a custom error code"
    )
    logger.info(f"Unknown Code Response: {unknown_code_response}")

def test_exceptions():
    """Test that exceptions correctly use the standardized messages."""  # noqa: D202
    
    try:
        raise ValidationError(
            error_code=ErrorCode.VALIDATION_MISSING_FIELD,
            field_name="password"
        )
    except ValidationError as e:
        logger.info(f"ValidationError: {str(e)}")
        logger.info(f"Error code: {e.error_code}")
        logger.info(f"Details: {e.details}")
    
    try:
        raise ExecutionError(
            error_code=ErrorCode.EXECUTION_TOOL_FAILED,
            tool_name="web_search",
            reason="API key not provided"
        )
    except ExecutionError as e:
        logger.info(f"ExecutionError: {str(e)}")
        logger.info(f"Error code: {e.error_code}")
        logger.info(f"Details: {e.details}")
    
    try:
        raise ConnectionError(
            error_code=ErrorCode.CONNECTION_FAILED,
            service_name="Database",
            reason="Connection refused"
        )
    except ConnectionError as e:
        logger.info(f"ConnectionError: {str(e)}")
        logger.info(f"Error code: {e.error_code}")
        logger.info(f"Details: {e.details}")
    
    try:
        raise ResourceError(
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            resource_type="file",
            resource_id="document.txt"
        )
    except ResourceError as e:
        logger.info(f"ResourceError: {str(e)}")
        logger.info(f"Error code: {e.error_code}")
        logger.info(f"Details: {e.details}")

def main():
    """Run all tests for error messages."""
    logger.info("\n=== Testing Error Message Templates ===")
    test_error_templates()
    
    logger.info("\n=== Testing Error Responses ===")
    test_error_responses()
    
    logger.info("\n=== Testing Exception Messages ===")
    test_exceptions()
    
    logger.info("\nAll error message tests completed!")

if __name__ == "__main__":
    main() 