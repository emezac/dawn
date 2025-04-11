"""
Example demonstrating how to use the Dawn error handling system.

This example shows:
1. How to use the error classes and utility functions
2. How to implement error handling in a tool
3. How to implement error handling in a task
4. How to handle errors at different levels
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union

from core.errors import (
    DawnError,
    ErrorCode,
    InputValidationError,
    ResourceError,
    ServiceError,
    create_error_response,
    create_success_response,
    is_error_response,
    is_success_response,
    safe_execute,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# Example Tool
class DataProcessingTool:
    """Example tool that demonstrates error handling."""

    def __init__(self):
        self.name = "data_processing_tool"

    def validate_input(self, data: Dict[str, Any]) -> Optional[InputValidationError]:
        """Validate the input data.

        Args:
            data: The input data to validate

        Returns:
            An InputValidationError if validation fails, None otherwise
        """
        if not isinstance(data, dict):
            return InputValidationError("Input must be a dictionary", error_code=ErrorCode.INVALID_INPUT_FORMAT)

        if "input_text" not in data:
            return InputValidationError(
                "Missing required field: input_text", {"field": "input_text"}, ErrorCode.MISSING_REQUIRED_FIELD
            )

        if not isinstance(data.get("input_text"), str):
            return InputValidationError(
                "Field 'input_text' must be a string",
                {"field": "input_text", "type": type(data.get("input_text")).__name__},
                ErrorCode.INVALID_FIELD_TYPE,
            )

        if len(data.get("input_text", "")) > 1000:
            return InputValidationError(
                "Field 'input_text' exceeds maximum length of 1000 characters",
                {"field": "input_text", "max_length": 1000, "actual_length": len(data.get("input_text"))},
                ErrorCode.FIELD_LENGTH_EXCEEDED,
            )

        return None

    def process_data(self, input_text: str, max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """Process the input text.

        Args:
            input_text: The text to process
            max_tokens: Maximum number of tokens to process

        Returns:
            Dictionary with processed results

        Raises:
            ServiceError: If there's an issue with the processing service
        """
        # Simulate a service call that might fail
        if "error" in input_text.lower():
            raise ServiceError(
                "External service failed to process the input",
                {"service": "text_processor", "input_length": len(input_text)},
                ErrorCode.SERVICE_UNAVAILABLE,
            )

        # Simulate processing
        words = input_text.split()
        char_count = len(input_text)
        word_count = len(words)

        return {
            "summary": f"Processed {word_count} words and {char_count} characters",
            "word_count": word_count,
            "char_count": char_count,
            "first_words": words[:5] if len(words) > 5 else words,
        }

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with the given input.

        Args:
            data: Input data for the tool

        Returns:
            Dictionary with either a success response or an error response
        """
        # 1. Validate input
        validation_error = self.validate_input(data)
        if validation_error:
            logger.error(f"Validation error: {validation_error.message}")
            return validation_error.to_response()

        # 2. Extract parameters
        input_text = data.get("input_text")
        max_tokens = data.get("max_tokens")

        # 3. Process data (with safe execution)
        try:
            result = self.process_data(input_text, max_tokens)
            return create_success_response(
                result, message="Data processed successfully", metadata={"tool_name": self.name}
            )
        except DawnError as e:
            logger.error(f"Processing error: {e.message}")
            return e.to_response()
        except Exception as e:
            logger.exception("Unexpected error processing data")
            return create_error_response(
                ErrorCode.UNEXPECTED_ERROR, str(e), details={"exception_type": type(e).__name__}
            )


# Example Task
def data_analysis_task(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Example task that uses the DataProcessingTool and handles errors.

    Args:
        documents: List of document data to process

    Returns:
        Dictionary with either success response containing results or error response
    """
    # Validate input
    if not isinstance(documents, list):
        return create_error_response(ErrorCode.INVALID_INPUT_FORMAT, "Input must be a list of documents")

    if len(documents) == 0:
        return create_error_response(ErrorCode.EMPTY_INPUT, "Document list is empty")

    # Initialize tool
    processing_tool = DataProcessingTool()

    # Process each document
    results = []
    error_count = 0

    for i, doc in enumerate(documents):
        # Add document index for reference
        doc_data = {"input_text": doc.get("content", ""), "doc_id": doc.get("id", f"doc_{i}")}

        # Process the document
        result = processing_tool.execute(doc_data)

        # Check if processing was successful
        if is_success_response(result):
            results.append({"doc_id": doc_data["doc_id"], "success": True, "data": result["data"]})
        else:
            error_count += 1
            results.append({"doc_id": doc_data["doc_id"], "success": False, "error": result["error"]})

    # Return aggregated results
    if error_count == len(documents):
        # All documents failed
        return create_error_response(
            ErrorCode.TASK_EXECUTION_ERROR,
            "All documents failed to process",
            details={"total_docs": len(documents), "failed_docs": error_count},
        )
    elif error_count > 0:
        # Some documents failed, but not all
        return create_success_response(
            {
                "documents": results,
                "summary": {"total": len(documents), "successful": len(documents) - error_count, "failed": error_count},
            },
            message="Task completed with some errors",
            metadata={"task_name": "data_analysis"},
        )
    else:
        # All documents processed successfully
        return create_success_response(
            {"documents": results, "summary": {"total": len(documents), "successful": len(documents), "failed": 0}},
            message="Task completed successfully",
            metadata={"task_name": "data_analysis"},
        )


# Example usage
def main():
    """Run the example to demonstrate error handling."""
    # Test cases
    test_cases = [
        {
            "name": "Valid input",
            "documents": [{"id": "doc1", "content": "This is a sample document with valid content."}],
        },
        {"name": "Empty input", "documents": []},
        {
            "name": "Service error",
            "documents": [{"id": "doc2", "content": "This document will trigger an error in the service."}],
        },
        {
            "name": "Mixed results",
            "documents": [
                {"id": "doc3", "content": "This is another valid document."},
                {"id": "doc4", "content": "This document will trigger an error in the service."},
                {"id": "doc5", "content": "And this is a third valid document."},
            ],
        },
    ]

    # Run test cases
    for test in test_cases:
        print(f"\n=== Running test: {test['name']} ===")
        result = safe_execute(data_analysis_task, test["documents"])
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
