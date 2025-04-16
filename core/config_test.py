#!/usr/bin/env python3
"""
Test version of Dawn Framework Configuration System that doesn't depend on PyYAML

This module provides the same API as core.config but doesn't require the PyYAML package.
It should only be used for testing.
"""  # noqa: D202

import os
import sys
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Type, Callable

# Module level variables for storing configuration
_config: Dict[str, Any] = {}
_runtime_overrides: Dict[str, Any] = {}
_schema: Dict[str, Any] = {}
_logger = logging.getLogger("dawn.config")

# Default schema
DEFAULT_SCHEMA = {
    "environment": {
        "type": str,
        "env_var": "DAWN_ENVIRONMENT",
        "default": "development",
        "description": "Deployment environment (development, test, production)"
    },
    "debug_mode": {
        "type": bool,
        "env_var": "DAWN_DEBUG_MODE",
        "default": False,
        "description": "Enable debug mode"
    },
    "log_level": {
        "type": str,
        "env_var": "DAWN_LOG_LEVEL",
        "default": "info",
        "description": "Logging level (debug, info, warning, error, critical)"
    },
}


def get(key: str, default: Any = None) -> Any:
    """Get a configuration value.
    
    Args:
        key: Configuration key, can use dot notation for nested values
        default: Default value if key not found
        
    Returns:
        The configuration value or default
    """
    global _config
    
    # Handle dot notation for nested access
    if '.' in key:
        parts = key.split('.')
        value = _config
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        return value
    
    return _config.get(key, default)


def set(key: str, value: Any) -> None:
    """Override a configuration value at runtime.
    
    Args:
        key: Configuration key, can use dot notation for nested values
        value: New value to set
    """
    global _runtime_overrides, _config
    
    # Handle dot notation for nested values
    if '.' in key:
        parts = key.split('.')
        
        # Update runtime overrides
        target = _runtime_overrides
        for i, part in enumerate(parts[:-1]):
            if part not in target:
                target[part] = {}
            target = target[part]
        target[parts[-1]] = value
        
        # Update current config
        target = _config
        for i, part in enumerate(parts[:-1]):
            if part not in target:
                target[part] = {}
            target = target[part]
        target[parts[-1]] = value
    else:
        _runtime_overrides[key] = value
        _config[key] = value


def as_dict() -> Dict[str, Any]:
    """Get the complete configuration as a dictionary.
    
    Returns:
        Dict of all configuration values
    """
    return _config.copy()


def configure(
    config_paths: Optional[List[str]] = None,
    environment: Optional[str] = None,
    schema: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Initialize the configuration system.
    
    Args:
        config_paths: List of paths to configuration files, will be merged in order
                     (later files override earlier ones)
        environment: Explicitly set the environment, overrides env var and config files
        schema: Custom schema to use for validation and defaults
               
    Returns:
        Dict containing the complete configuration
    """
    global _config, _schema
    
    # Initialize logging
    logging.basicConfig(level=logging.INFO)
    
    # Load schema
    _schema = schema or DEFAULT_SCHEMA
    
    # Start with default values from schema
    _config = {}
    for key, info in _schema.items():
        if "default" in info:
            _config[key] = info["default"]
    
    # Override with config files if provided
    if config_paths:
        for config_path in config_paths:
            if config_path and os.path.exists(config_path):
                file_config = _load_config_file(config_path)
                _deep_update(_config, file_config)

    # Override with environment-specific config if available
    env = environment or os.environ.get("DAWN_ENVIRONMENT", _config.get("environment", "development"))
    _config["environment"] = env
    
    # Override with environment variables
    env_config = _load_from_env(_schema)
    _deep_update(_config, env_config)
    
    # Add runtime overrides
    _deep_update(_config, _runtime_overrides)
    
    # Configure logging based on configuration
    _configure_logging()
    
    _logger.info(f"Configuration initialized for environment: {_config.get('environment')}")
    return _config


def is_production() -> bool:
    """Check if running in production environment.
    
    Returns:
        True if in production environment
    """
    return get("environment", "").lower() == "production"


def is_development() -> bool:
    """Check if running in development environment.
    
    Returns:
        True if in development environment
    """
    return get("environment", "").lower() == "development"


def is_test() -> bool:
    """Check if running in test environment.
    
    Returns:
        True if in test environment
    """
    return get("environment", "").lower() == "test"


def _deep_update(target: Dict[str, Any], source: Dict[str, Any]) -> None:
    """Recursively update a dictionary with another dictionary.
    
    Args:
        target: Dictionary to update
        source: Dictionary with updates
    """
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            _deep_update(target[key], value)
        else:
            target[key] = value


def _load_config_file(file_path: str) -> Dict[str, Any]:
    """Load configuration from a file.
    
    Args:
        file_path: Path to configuration file
        
    Returns:
        Dict containing the configuration from the file
    """
    try:
        with open(file_path, 'r') as f:
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ('.yaml', '.yml'):
                # Mock YAML loading with JSON for tests
                return json.load(f)
            else:
                return json.load(f)
    except Exception as e:
        _logger.warning(f"Error loading config from {file_path}: {str(e)}")
        return {}


def _load_from_env(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Load configuration from environment variables based on schema.
    
    Args:
        schema: Configuration schema with env_var mappings
        
    Returns:
        Dict containing configuration values loaded from environment variables
    """
    result = {}
    
    # Process top-level schema items
    for key, info in schema.items():
        if isinstance(info, dict) and "env_var" in info:
            env_value = os.environ.get(info["env_var"])
            if env_value is not None:
                # Convert to the right type
                if info["type"] == bool:
                    result[key] = env_value.lower() in ('true', 't', 'yes', 'y', '1')
                elif info["type"] == int:
                    result[key] = int(env_value)
                elif info["type"] == float:
                    result[key] = float(env_value)
                else:
                    result[key] = env_value
    
    return result


def _validate_config(config: Dict[str, Any], schema: Dict[str, Any]) -> None:
    """Validate configuration against schema.
    
    Args:
        config: Configuration to validate
        schema: Schema to validate against
    """
    # Simple validation for now
    for key, info in schema.items():
        if key in config and isinstance(info, dict) and "type" in info:
            expected_type = info["type"]
            if not isinstance(config[key], expected_type):
                _logger.warning(f"Config value for '{key}' has incorrect type. Expected {expected_type.__name__}, got {type(config[key]).__name__}")


def _configure_logging() -> None:
    """Configure logging based on the loaded configuration."""
    log_level_str = get("log_level", "info").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    
    # Set root logger level
    logging.getLogger().setLevel(log_level)
    
    # Set Dawn loggers level
    dawn_logger = logging.getLogger("dawn")
    dawn_logger.setLevel(log_level)
    
    # Configure handler if needed
    if not dawn_logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        dawn_logger.addHandler(handler)
    
    _logger.debug(f"Logging configured with level: {log_level_str}") 