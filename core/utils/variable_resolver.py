"""
Variable Resolution Utilities for Dawn Framework.

This module provides functionality for resolving variable references in task inputs.
It supports complex nested data structures and offers robust error handling.
"""

import re
from typing import Any, Dict, List, Optional, Union

# Import TaskOutput if it's defined elsewhere, otherwise assume it's available
# from ..task import TaskOutput # Example relative import if needed

def resolve_path(data: Any, path: str) -> Any:
    """
    Resolve a dot notation path in a nested data structure (dict, list, or object).
    
    Args:
        data: The data structure (dict, list, object) to traverse
        path: A dot-notation path like "field1.field2[0].attribute3"
        
    Returns:
        The value at the specified path
        
    Raises:
        KeyError: If a dictionary key is not found
        AttributeError: If an object attribute is not found
        IndexError: If an array index is out of bounds
        ValueError: If the path syntax is invalid or traversal fails
    """
    if not path:
        return data
    
    current = data
    
    # Regex to split path by dots, but not dots within brackets []
    # And also captures array indexing like [0]
    # Parts can be: field_name, [index], .attribute_name
    parts = re.findall(r'\.([\w_]+)|\[(\d+)\]|([\w_]+)', '.' + path) # Prepend dot to handle leading field

    for dot_attr, index, first_field in parts:
        part = dot_attr or first_field # Prioritize dot access/first field
        index_val = int(index) if index is not None else None

        if index_val is not None:
            # Handle list/tuple indexing
            if isinstance(current, (list, tuple)):
                if 0 <= index_val < len(current):
                    current = current[index_val]
                else:
                    raise IndexError(f"Index {index_val} out of bounds for list/tuple of length {len(current)} in path '{path}'")
            else:
                raise ValueError(f"Cannot apply index [{index_val}] to non-list/tuple type {type(current).__name__} in path '{path}'")
        elif part: # Handle dict key or object attribute
            if isinstance(current, dict):
                # Use get() for safer access, returning None if key missing
                value = current.get(part)
                if value is not None:
                     current = value
                # --- Levantar KeyError si la clave NO existe ---
                elif part not in current: # Check explicitly if key is absent
                     raise KeyError(f"Key '{part}' not found in dictionary in path '{path}'")
                # --- Si la clave existe pero el valor es None, current se vuelve None ---
                else:
                     current = None # Allow resolving path to None

            # Check if it's an object with attributes (and not a list/tuple/dict already handled)
            elif hasattr(current, part):
                 try:
                     current = getattr(current, part)
                 except AttributeError: # Catch specific AttributeError
                     raise AttributeError(f"Attribute '{part}' not found on {type(current).__name__} in path '{path}'")
                 except Exception as e: # Catch other potential getattr errors
                     # Use ValueError for unexpected getattr issues
                     raise ValueError(f"Error accessing attribute '{part}' on {type(current).__name__} in path '{path}': {e}")
            # --- Si no es dict ni tiene el atributo ---
            elif current is None: # If traversing yielded None previously
                raise ValueError(f"Cannot access key/attribute '{part}' in None object in path '{path}'")
            else:
                 # Raise AttributeError if it's not a dict and lacks the attr
                raise AttributeError(f"Key/attribute '{part}' not found in type {type(current).__name__} in path '{path}'")
        else:
            # Should not happen with the regex, but safety check
            raise ValueError(f"Invalid path segment encountered in path '{path}'")
            
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
    Handles paths like task_id.output_data.field or task_id.output_data.to_dict().field
    """
    # variable_path is expected to be like "task_id.some.path.here"
    parts = variable_path.split('.', 1)
    
    if len(parts) < 2:
        # Maybe it's a top-level workflow variable?
        if variable_path in context: # Check if the whole path is a key in the top-level context
            return context[variable_path]
        raise ValueError(f"Invalid variable path format: '{variable_path}'. Expected 'task_id.path' or 'workflow_variable_name'.")
    
    task_id, remaining_path = parts
    
    if task_id not in context:
        raise KeyError(f"Task ID '{task_id}' not found in resolution context")
    
    task_context_data = context[task_id]
    
    # Resolve the remaining path within the task's context data
    try:
        # task_context_data could be the TaskOutput object or a dict representation
        return resolve_path(task_context_data, remaining_path)
    except (KeyError, IndexError, AttributeError, ValueError, TypeError) as e:
        raise ValueError(f"Failed to resolve path '{remaining_path}' within task '{task_id}': {type(e).__name__}: {e}")


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