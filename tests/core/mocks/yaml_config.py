"""
Mock YAML config module for testing.

This module provides mock implementations of config.get and config.set
to avoid the dependency on PyYAML during testing.
"""

# Internal storage for config values
_config_values = {}

def get(key, default=None):
    """
    Get a configuration value.
    
    Args:
        key: The configuration key
        default: Default value if key not found
        
    Returns:
        The configuration value or default
    """
    return _config_values.get(key, default)

def set(key, value):
    """
    Set a configuration value.
    
    Args:
        key: The configuration key
        value: The value to set
    """
    _config_values[key] = value 