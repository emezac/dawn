"""
Basic tools for the AI Agent Framework.

This module provides some basic tools that can be used by the agent.
"""

from typing import Dict, Any


def calculate(operation: str, a: float, b: float) -> float:
    """
    Perform basic arithmetic calculations.
    
    Args:
        operation: The operation to perform (add, subtract, multiply, divide)
        a: First number
        b: Second number
            
    Returns:
        The result of the calculation
        
    Raises:
        ValueError: If the operation is invalid or inputs are missing
    """
    if operation == 'add':
        return a + b
    elif operation == 'subtract':
        return a - b
    elif operation == 'multiply':
        return a * b
    elif operation == 'divide':
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    else:
        raise ValueError(f"Invalid operation: {operation}. Must be one of: add, subtract, multiply, divide")


def check_length(content: str, min_length: int, max_length: int) -> dict:
    """Check if the content length is within the specified range."""
    length = len(content)
    if min_length <= length <= max_length:
        return {"success": True, "length": length}
    else:
        return {"success": False, "error": f"Content length {length} is out of range."}
