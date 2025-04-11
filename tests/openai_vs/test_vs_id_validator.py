"""
Tests for the Vector Store ID validation utilities.
"""

import os
import sys
import unittest

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tools.openai_vs.utils.vs_id_validator import (
    assert_valid_vector_store_id,
    is_strict_valid_vector_store_id,
    is_valid_vector_store_id,
    validate_vector_store_id,
)


class TestVectorStoreIDValidator(unittest.TestCase):
    """Test case for vector store ID validation utilities."""

    def test_is_valid_vector_store_id(self):
        """Test basic vector store ID validation."""
        # Valid IDs
        self.assertTrue(is_valid_vector_store_id("vs_abc123"))
        self.assertTrue(is_valid_vector_store_id("vs_" + "a" * 100))  # Long ID
        self.assertTrue(is_valid_vector_store_id("vs_abc-123"))  # Hyphen
        self.assertTrue(is_valid_vector_store_id("vs_abc.123"))  # Period
        self.assertTrue(is_valid_vector_store_id("vs_abc+123"))  # Plus
        self.assertTrue(is_valid_vector_store_id("vs_abc?123"))  # Question mark

        # Invalid IDs
        self.assertFalse(is_valid_vector_store_id(None))
        self.assertFalse(is_valid_vector_store_id(""))
        self.assertFalse(is_valid_vector_store_id("abc123"))
        self.assertFalse(is_valid_vector_store_id("vsabc123"))
        self.assertFalse(is_valid_vector_store_id("vs abc123"))
        self.assertFalse(is_valid_vector_store_id(123))
        self.assertFalse(is_valid_vector_store_id(["vs_abc123"]))
        self.assertFalse(is_valid_vector_store_id({"id": "vs_abc123"}))

    def test_is_strict_valid_vector_store_id(self):
        """Test strict vector store ID validation with regex pattern."""
        # Valid IDs
        self.assertTrue(is_strict_valid_vector_store_id("vs_" + "a" * 24))
        self.assertTrue(is_strict_valid_vector_store_id("vs_" + "0" * 24))
        self.assertTrue(is_strict_valid_vector_store_id("vs_" + "A" * 24))
        self.assertTrue(is_strict_valid_vector_store_id("vs_abc123def456ghi789jkl012"))
        self.assertTrue(is_strict_valid_vector_store_id("vs_" + "a" * 12 + "0" * 12))

        # Invalid IDs - basic checks
        self.assertFalse(is_strict_valid_vector_store_id(None))
        self.assertFalse(is_strict_valid_vector_store_id(""))
        self.assertFalse(is_strict_valid_vector_store_id("abc123"))
        self.assertFalse(is_strict_valid_vector_store_id(123))

        # Invalid IDs - format-specific checks
        self.assertFalse(is_strict_valid_vector_store_id("vs_" + "a" * 23))  # Too short
        self.assertFalse(is_strict_valid_vector_store_id("vs_" + "a" * 25))  # Too long
        self.assertFalse(is_strict_valid_vector_store_id("vs_abc-123def456ghi789jkl"))  # Contains hyphen
        self.assertFalse(is_strict_valid_vector_store_id("vs_abc.123def456ghi789jkl"))  # Contains period
        self.assertFalse(is_strict_valid_vector_store_id("vs_abc+123def456ghi789jkl"))  # Contains plus
        self.assertFalse(is_strict_valid_vector_store_id("vs_abc?123def456ghi789jkl"))  # Contains question mark
        self.assertFalse(is_strict_valid_vector_store_id("vs_abc 123def456ghi789jkl"))  # Contains space

    def test_validate_vector_store_id(self):
        """Test the validation function that returns status and error message."""
        # Basic validation
        valid, error = validate_vector_store_id("vs_abc123", strict=False)
        self.assertTrue(valid)
        self.assertIsNone(error)

        # Strict validation - valid ID
        valid, error = validate_vector_store_id("vs_abc123def456ghi789jkl012", strict=True)
        self.assertTrue(valid)
        self.assertIsNone(error)

        # Strict validation - invalid ID
        valid, error = validate_vector_store_id("vs_abc-123", strict=True)
        self.assertFalse(valid)
        self.assertIn("must follow pattern", error)

        # Different error messages
        valid, error = validate_vector_store_id(None)
        self.assertFalse(valid)
        self.assertEqual("Vector store ID cannot be None", error)

        valid, error = validate_vector_store_id("")
        self.assertFalse(valid)
        self.assertEqual("Vector store ID cannot be empty", error)

        valid, error = validate_vector_store_id("abc123")
        self.assertFalse(valid)
        self.assertEqual("Vector store ID must start with 'vs_' prefix", error)

        valid, error = validate_vector_store_id(123)
        self.assertFalse(valid)
        self.assertEqual("Vector store ID must be a string, got int", error)

    def test_assert_valid_vector_store_id(self):
        """Test the assertion function that raises ValueError."""
        # Valid IDs should not raise exceptions
        try:
            assert_valid_vector_store_id("vs_abc123")
            assert_valid_vector_store_id("vs_abc123def456ghi789jkl012", strict=True)
        except ValueError:
            self.fail("Valid vector store ID raised ValueError")

        # Invalid IDs should raise ValueError with appropriate message
        with self.assertRaises(ValueError) as context:
            assert_valid_vector_store_id(None)
        self.assertEqual("Vector store ID cannot be None", str(context.exception))

        with self.assertRaises(ValueError) as context:
            assert_valid_vector_store_id("")
        self.assertEqual("Vector store ID cannot be empty", str(context.exception))

        with self.assertRaises(ValueError) as context:
            assert_valid_vector_store_id("abc123")
        self.assertEqual("Vector store ID must start with 'vs_' prefix", str(context.exception))

        with self.assertRaises(ValueError) as context:
            assert_valid_vector_store_id("vs_abc123", strict=True)
        self.assertIn("must follow pattern", str(context.exception))


if __name__ == "__main__":
    unittest.main()
