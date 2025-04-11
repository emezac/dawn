"""
Utility module for OpenAI Vector Store ID validation.
"""

import re
from typing import Optional, Tuple


def is_valid_vector_store_id(vs_id: any) -> bool:
    """
    Validate if the provided value is a valid vector store ID.
    Currently checks:
    1. Not None
    2. Is a string
    3. Not empty
    4. Starts with "vs_" prefix
    5. Has at least one character after the "vs_" prefix

    Args:
        vs_id: The value to validate as a vector store ID

    Returns:
        bool: True if the ID is valid, False otherwise
    """
    if vs_id is None or not isinstance(vs_id, str) or not vs_id:
        return False

    # Check that it starts with "vs_" prefix and has at least one character after
    return vs_id.startswith("vs_") and len(vs_id) > 3


def is_strict_valid_vector_store_id(vs_id: any) -> bool:
    """
    Perform strict validation of vector store ID.
    Uses regex pattern to validate format: vs_[a-zA-Z0-9]{24}

    Args:
        vs_id: The value to validate as a vector store ID

    Returns:
        bool: True if the ID passes strict validation, False otherwise
    """
    if not is_valid_vector_store_id(vs_id):
        return False

    # OpenAI vector store IDs typically follow pattern: vs_[a-zA-Z0-9]{24}
    pattern = r"^vs_[a-zA-Z0-9]{24}$"
    return bool(re.match(pattern, vs_id))


def validate_vector_store_id(vs_id: any, strict: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Validate a vector store ID and return validation status and error message.

    Args:
        vs_id: The value to validate as a vector store ID
        strict: Whether to use strict validation rules

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if vs_id is None:
        return False, "Vector store ID cannot be None"

    if not isinstance(vs_id, str):
        return False, f"Vector store ID must be a string, got {type(vs_id).__name__}"

    if not vs_id:
        return False, "Vector store ID cannot be empty"

    if not vs_id.startswith("vs_"):
        return False, "Vector store ID must start with 'vs_' prefix"

    if strict:
        pattern = r"^vs_[a-zA-Z0-9]{24}$"
        if not re.match(pattern, vs_id):
            return False, "Vector store ID must follow pattern: vs_[a-zA-Z0-9]{24}"

    return True, None


def assert_valid_vector_store_id(vs_id: any, strict: bool = False) -> None:
    """
    Assert that the provided value is a valid vector store ID.
    Raises ValueError with specific error message if invalid.

    Args:
        vs_id: The value to validate as a vector store ID
        strict: Whether to use strict validation rules

    Raises:
        ValueError: If the ID doesn't pass validation
    """
    is_valid, error_message = validate_vector_store_id(vs_id, strict)
    if not is_valid:
        raise ValueError(error_message)
