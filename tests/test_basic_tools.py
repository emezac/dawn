import os
import sys

import pytest

# Add parent directory to path to import framework modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.tools.registry import ToolRegistry
from tools.basic_tools import calculate, check_length


def test_calculate_addition():
    result = calculate("add", 2, 3)
    assert result == 5


def test_calculate_subtraction():
    result = calculate("subtract", 5, 3)
    assert result == 2


def test_calculate_multiplication():
    result = calculate("multiply", 2, 3)
    assert result == 6


def test_calculate_division():
    result = calculate("divide", 6, 3)
    assert result == 2


def test_calculate_division_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calculate("divide", 6, 0)


def test_calculate_invalid_operation():
    with pytest.raises(ValueError, match="Invalid operation: invalid"):
        calculate("invalid", 2, 3)


def test_check_length_within_range():
    result = check_length("Hello, world!", 5, 20)
    assert result["success"] is True


def test_check_length_too_short():
    result = check_length("Hi", 5, 20)
    assert result["success"] is False


def test_check_length_too_long():
    result = check_length("This is a very long string that exceeds the maximum length.", 5, 20)
    assert result["success"] is False
