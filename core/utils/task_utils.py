"""
Utility functions for working with task outputs and input values.
"""

import logging
from typing import Any, Dict, Optional
from core.utils.variable_resolver import resolve_path

logger = logging.getLogger(__name__)

def get_output_value(output_dict: Dict[str, Any], field_path: str) -> Any:
    """
    Safely extract a value from a nested dictionary using a dot-notation path.
    
    Args:
        output_dict: The dictionary to extract from (e.g., task output data)
        field_path: Dot-notation path (e.g., "result.items.0.name")
    
    Returns:
        The extracted value, or None if the path doesn't exist
    """
    if not output_dict:
        return None
        
    if not field_path:
        return output_dict
    
    current = output_dict
    parts = field_path.split('.')
    
    try:
        for part in parts:
            # Handle numeric indexes in lists
            if isinstance(current, list) and part.isdigit():
                idx = int(part)
                if idx < len(current):
                    current = current[idx]
                else:
                    logger.warning(f"Index {idx} out of range in list of length {len(current)}")
                    return None
            # Handle dictionary keys    
            elif isinstance(current, dict) and part in current:
                current = current[part]
            # If key not found in dict
            else:
                logger.warning(f"Key '{part}' not found in {type(current)}")
                return None
        return current
    except Exception as e:
        logger.warning(f"Error accessing path '{field_path}': {e}")
        return None 