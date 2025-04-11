"""
Variable Resolution Utilities for Dawn Framework.

This module provides functionality for resolving variable references in task inputs.
It supports complex nested data structures and offers robust error handling.
"""

import re
from typing import Any, Dict, List, Optional, Union


def resolve_path(data: Dict[str, Any], path: str) -> Any:
    """
    Resolve a dot notation path in a nested data structure.
    
    Args:
        data: The data structure to traverse
        path: A dot-notation path like "field1.field2[0].field3"
        
    Returns:
        The value at the specified path
        
    Raises:
        KeyError: If a dictionary key or attribute is not found
        IndexError: If an array index is out of bounds
        ValueError: If the path syntax is invalid
    """
    if not path:
        return data
    
    # Initialize with the root data
    current = data
    
    # Split the path into parts (handling special indexing syntax)
    path_parts = []
    
    # Regular expression to match array indexing
    index_pattern = re.compile(r'(\w+)(\[\d+\])+')
    
    for part in path.split('.'):
        # Check if the part contains array indexing
        match = index_pattern.match(part)
        if match:
            # Extract the base field name
            field_name = match.group(1)
            path_parts.append(field_name)
            
            # Extract each index and add it as a separate part
            indices = re.findall(r'\[(\d+)\]', part)
            for idx in indices:
                path_parts.append(int(idx))
        else:
            path_parts.append(part)
    
    # Traverse the path
    for part in path_parts:
        if isinstance(current, dict):
            if isinstance(part, str) and part in current:
                current = current[part]
            else:
                raise KeyError(f"Key '{part}' not found in dictionary")
        elif isinstance(current, (list, tuple)) and isinstance(part, int):
            if 0 <= part < len(current):
                current = current[part]
            else:
                raise IndexError(f"Index {part} is out of bounds for list of length {len(current)}")
        else:
            raise ValueError(f"Cannot access '{part}' in {type(current).__name__}")
    
    return current


def resolve_variables(
    input_data: Union[Dict[str, Any], List[Any], str], 
    context: Dict[str, Any],
    max_depth: int = 10
) -> Any:
    """
    Recursively resolve all variable references in the input data.
    
    Args:
        input_data: The input data containing variable references
        context: The context containing the values to substitute
        max_depth: Maximum recursion depth to prevent infinite loops
        
    Returns:
        The input data with all variables resolved
    """
    if max_depth <= 0:
        raise RecursionError("Maximum recursion depth exceeded during variable resolution")
    
    # Handle different input types
    if isinstance(input_data, dict):
        return {k: resolve_variables(v, context, max_depth - 1) for k, v in input_data.items()}
    
    elif isinstance(input_data, list):
        return [resolve_variables(item, context, max_depth - 1) for item in input_data]
    
    elif isinstance(input_data, str):
        # Find all variable references
        matches = re.findall(r'\${([^}]+)}', input_data)
        
        if not matches:
            return input_data
        
        # If the entire string is a variable reference, return the full value
        if input_data == f"${{{matches[0]}}}":
            try:
                return get_variable_value(matches[0], context)
            except (KeyError, IndexError, ValueError) as e:
                # Return the original string if resolution fails
                return input_data
        
        # Otherwise, replace each reference in the string
        result = input_data
        for match in matches:
            try:
                replacement = get_variable_value(match, context)
                # Convert the replacement to string unless the entire input is just the variable
                if isinstance(replacement, (dict, list, tuple)):
                    replacement = str(replacement)
                result = result.replace(f"${{{match}}}", str(replacement))
            except (KeyError, IndexError, ValueError):
                # Skip this replacement if it fails
                continue
        
        return result
    
    # Return other types unchanged
    return input_data


def get_variable_value(variable_path: str, context: Dict[str, Any]) -> Any:
    """
    Extract a value from the context based on a variable path.
    
    Args:
        variable_path: Path to the variable (e.g., "task_name.output_data.field")
        context: Dictionary containing task outputs and other context
        
    Returns:
        The resolved value
        
    Raises:
        KeyError: If the task or field doesn't exist
        ValueError: If the variable path is invalid
    """
    parts = variable_path.split('.', 1)
    
    if len(parts) < 2:
        raise ValueError(f"Invalid variable path: {variable_path}")
    
    task_id, field_path = parts
    
    if task_id not in context:
        raise KeyError(f"Task '{task_id}' not found in context")
    
    task_data = context[task_id]
    
    # Handle special case for output_data as a shortcut to the whole output
    if field_path == "output_data":
        return task_data.get("output_data", {})
    
    # Otherwise traverse the path
    try:
        if field_path.startswith("output_data."):
            # Strip the output_data prefix and resolve in the task's output_data
            sub_path = field_path[len("output_data."):]
            return resolve_path(task_data.get("output_data", {}), sub_path)
        else:
            # Resolve in the entire task data
            return resolve_path(task_data, field_path)
    except (KeyError, IndexError, ValueError) as e:
        raise ValueError(f"Failed to resolve '{variable_path}': {str(e)}")


def build_context_from_workflow(workflow_tasks: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a context dictionary from workflow tasks for variable resolution.
    
    Args:
        workflow_tasks: Dictionary of task_id -> task data
        
    Returns:
        A context dictionary usable by the variable resolver
    """
    context = {}
    
    for task_id, task_data in workflow_tasks.items():
        # Create a simplified view of the task
        task_context = {
            "id": task_id,
            "status": task_data.get("status", "unknown"),
            "output_data": task_data.get("output_data", {}),
        }
        context[task_id] = task_context
    
    return context 