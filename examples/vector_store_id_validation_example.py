"""
Example showing how to use the vector store ID validation utilities.
"""

import os
import sys
import logging
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.registry import ToolRegistry
from tools.openai_vs.utils.vs_id_validator import (
    assert_valid_vector_store_id,
    is_strict_valid_vector_store_id,
    is_valid_vector_store_id,
    validate_vector_store_id,
)
from core.tools.registry_access import get_registry

# --- Setup ---
logging.basicConfig(level=logging.INFO)
load_dotenv()

# Get the singleton registry
registry = get_registry()

def demonstrate_validation():
    """Demonstrate different validation methods using examples."""
    print("Demonstrating Vector Store ID Validation Utilities")
    print("=" * 50)

    # Example Vector Store IDs - valid and invalid
    vs_ids = [
        "vs_abc123def456ghi789jkl012",  # Valid with strict pattern
        "vs_short",  # Valid with basic check, invalid with strict
        "vs_123",  # Valid with basic check, invalid with strict
        "vs_abc!@#",  # Valid with basic check, has invalid chars
        "",  # Invalid - empty
        None,  # Invalid - None
        "abc123",  # Invalid - missing prefix
        123,  # Invalid - wrong type
    ]

    print("\n1. Basic Boolean Validation")
    print("-" * 30)
    for vs_id in vs_ids:
        result = is_valid_vector_store_id(vs_id)
        print(f"ID: {vs_id} → Valid: {result}")

    print("\n2. Strict Boolean Validation")
    print("-" * 30)
    for vs_id in vs_ids:
        result = is_strict_valid_vector_store_id(vs_id)
        print(f"ID: {vs_id} → Strictly Valid: {result}")

    print("\n3. Validation with Error Messages")
    print("-" * 30)
    for vs_id in vs_ids:
        is_valid, error = validate_vector_store_id(vs_id, strict=False)
        if is_valid:
            print(f"ID: {vs_id} → Valid")
        else:
            print(f"ID: {vs_id} → Invalid: {error}")

    print("\n4. Strict Validation with Error Messages")
    print("-" * 30)
    for vs_id in vs_ids:
        is_valid, error = validate_vector_store_id(vs_id, strict=True)
        if is_valid:
            print(f"ID: {vs_id} → Strictly Valid")
        else:
            print(f"ID: {vs_id} → Invalid: {error}")

    print("\n5. Validation with Exception Handling")
    print("-" * 30)
    for vs_id in vs_ids:
        try:
            assert_valid_vector_store_id(vs_id)
            print(f"ID: {vs_id} → Valid")
        except ValueError as e:
            print(f"ID: {vs_id} → Error: {e}")


def real_world_example():
    """Demonstrate a real-world example using the validation in a workflow."""
    print("\nReal-World Validation Example")
    print("=" * 50)

    # Initialize the tool registry
    registry = ToolRegistry()

    # --- Create Vector Store ---
    vector_store_create_input = {"name": "Example Vector Store"}
    vector_store_result = registry.execute_tool("create_vector_store", vector_store_create_input)

    if not vector_store_result["success"]:
        print(f"Vector store creation failed: {vector_store_result['error']}")
        return

    vector_store_id = vector_store_result["result"]
    print(f"Created vector store with ID: {vector_store_id}")

    # --- Validate the Vector Store ID ---
    print("\nValidating the Vector Store ID")

    # Basic validation
    is_valid = is_valid_vector_store_id(vector_store_id)
    print(f"Basic validation: {is_valid}")

    # Strict validation
    is_strictly_valid = is_strict_valid_vector_store_id(vector_store_id)
    print(f"Strict validation: {is_strictly_valid}")

    # Validation with detailed error
    validity, error = validate_vector_store_id(vector_store_id, strict=True)
    if validity:
        print("The vector store ID passed strict validation")
    else:
        print(f"Validation error: {error}")

    # --- Try with an invalid ID ---
    invalid_id = "invalid_vs_id"
    print(f"\nTrying an invalid ID: {invalid_id}")

    try:
        assert_valid_vector_store_id(invalid_id)
        print("ID is valid (this should not be printed)")
    except ValueError as e:
        print(f"Correctly caught invalid ID: {e}")

    # --- Delete the Vector Store ---
    if is_valid:
        delete_input = {"vector_store_id": vector_store_id}
        delete_result = registry.execute_tool("delete_vector_store", delete_input)

        if delete_result["success"]:
            print(f"Successfully deleted vector store: {vector_store_id}")
        else:
            print(f"Failed to delete vector store: {delete_result['error']}")


def integration_example():
    """Show how to integrate validation in custom functions."""
    print("\nIntegration Example")
    print("=" * 50)

    def process_vector_store(vs_id, strict=False):
        """Example function that processes a vector store."""
        print(f"Processing vector store ID: {vs_id}")

        # Method 1: Use assert function (raises error if invalid)
        try:
            assert_valid_vector_store_id(vs_id, strict=strict)
        except ValueError as e:
            print(f"Validation failed: {e}")
            return False

        # Method 2: Get validation result and handle explicitly
        is_valid, error = validate_vector_store_id(vs_id, strict=strict)
        if not is_valid:
            print(f"Validation failed: {error}")
            return False

        # Continue with processing if validation passes
        print(f"Vector store ID {vs_id} is valid, continuing with processing...")
        return True

    # Example usage
    print("\nProcessing with basic validation:")
    process_vector_store("vs_example123")

    print("\nProcessing with strict validation:")
    process_vector_store("vs_example123", strict=True)

    print("\nProcessing invalid ID:")
    process_vector_store("invalid_id")


if __name__ == "__main__":
    demonstrate_validation()
    real_world_example()
    integration_example()
