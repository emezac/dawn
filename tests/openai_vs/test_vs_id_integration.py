"""
Tests for integrating vector store ID validation with existing tools.
This test is for demonstration purposes only and does not modify the existing code.
It shows how the validation utilities could be integrated.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tools.openai_vs.delete_vector_store import DeleteVectorStoreTool
from tools.openai_vs.utils.vs_id_validator import assert_valid_vector_store_id


class DemoEnhancedDeleteVectorStoreTool(DeleteVectorStoreTool):
    """
    Enhanced version of DeleteVectorStoreTool with improved validation.
    This is for demonstration only and doesn't modify the existing implementation.
    """

    def delete_vector_store(self, vector_store_id: str, strict_validation: bool = False):
        """
        Enhanced version of delete_vector_store with improved validation.

        Args:
            vector_store_id: The ID of the Vector Store to delete.
            strict_validation: Whether to use strict validation rules.

        Returns:
            Dict: A dictionary indicating the deletion status.
        """
        # Use the validation utility instead of simple check
        assert_valid_vector_store_id(vector_store_id, strict=strict_validation)

        # Rest of the original implementation
        self.client.vector_stores.delete(vector_store_id=vector_store_id)
        return {"deleted": True, "id": vector_store_id}


class TestVectorStoreIDIntegration(unittest.TestCase):
    """Test suite demonstrating integration of validation utilities with tools."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = MagicMock()
        self.enhanced_tool = DemoEnhancedDeleteVectorStoreTool(client=self.mock_client)

    def test_enhanced_tool_validation(self):
        """Test the enhanced tool with improved validation."""
        # Valid ID with basic validation
        with patch.object(self.mock_client.vector_stores, "delete") as mock_delete:
            self.enhanced_tool.delete_vector_store("vs_abc123")
            mock_delete.assert_called_once_with(vector_store_id="vs_abc123")

        # Invalid IDs
        with self.assertRaises(ValueError) as context:
            self.enhanced_tool.delete_vector_store(None)
        self.assertEqual("Vector store ID cannot be None", str(context.exception))

        with self.assertRaises(ValueError) as context:
            self.enhanced_tool.delete_vector_store("")
        self.assertEqual("Vector store ID cannot be empty", str(context.exception))

        with self.assertRaises(ValueError) as context:
            self.enhanced_tool.delete_vector_store("abc123")
        self.assertEqual("Vector store ID must start with 'vs_' prefix", str(context.exception))

    def test_enhanced_tool_strict_validation(self):
        """Test the enhanced tool with strict validation."""
        # Valid ID with strict validation
        valid_id = "vs_abc123def456ghi789jkl012"
        with patch.object(self.mock_client.vector_stores, "delete") as mock_delete:
            self.enhanced_tool.delete_vector_store(valid_id, strict_validation=True)
            mock_delete.assert_called_once_with(vector_store_id=valid_id)

        # Valid with basic validation but invalid with strict validation
        with self.assertRaises(ValueError) as context:
            self.enhanced_tool.delete_vector_store("vs_abc", strict_validation=True)
        self.assertIn("must follow pattern", str(context.exception))


class ExampleUsage:
    """
    Example usage of the validation utilities in different contexts.
    This is not a test class but demonstrates how to use the utilities.
    """

    @staticmethod
    def example_direct_usage():
        """Example of direct usage of the validation utilities."""
        from tools.openai_vs.utils.vs_id_validator import (
            assert_valid_vector_store_id,
            is_valid_vector_store_id,
            validate_vector_store_id,
        )

        # Simple boolean check
        if is_valid_vector_store_id("vs_abc123"):
            print("Valid ID")

        # Get validation status and error
        is_valid, error = validate_vector_store_id("vs_abc123", strict=True)
        if not is_valid:
            print(f"Invalid ID: {error}")

        # Assert with exception
        try:
            assert_valid_vector_store_id("vs_abc123")
            # Continue with operation
        except ValueError as e:
            print(f"Invalid ID: {e}")

    @staticmethod
    def example_tool_integration():
        """Example of integrating validation in a tool method."""

        def process_vector_store(vector_store_id):
            from tools.openai_vs.utils.vs_id_validator import assert_valid_vector_store_id, validate_vector_store_id

            # Option 1: Basic validation - minimal change to existing code
            assert_valid_vector_store_id(vector_store_id)

            # Option 2: With customized error message
            is_valid, error = validate_vector_store_id(vector_store_id)
            if not is_valid:
                raise ValueError(f"Invalid vector store ID for processing: {error}")

            # Option 3: With strict validation for critical operations
            assert_valid_vector_store_id(vector_store_id, strict=True)

            # Continue with operation
            return f"Processed {vector_store_id}"


if __name__ == "__main__":
    unittest.main()
