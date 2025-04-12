#!/usr/bin/env python3
"""
Dawn Framework Configuration System

This module provides a unified configuration system for the Dawn Framework.
It supports loading configuration from multiple sources in the following order of precedence:

1. Runtime overrides (via set() function)
2. Environment variables (prefixed with DAWN_)
3. Environment-specific config file (e.g., production.json, development.json)
4. Base config file (config.json)
5. Default values from schema

Usage:
    # Initialize with specific config files
    from core.config import configure
    configure(config_paths=["config/config.json", "config/production.json"])

    # Get configuration values
    from core.config import get
    api_key = get("llm_api_key")
    debug_mode = get("debug_mode", False)  # With default value
    db_connection = get("database.connection_string")  # Nested values with dot notation

    # Override configuration at runtime
    from core.config import set
    set("llm_model", "gpt-4")

    # Get complete configuration
    from core.config import as_dict
    all_config = as_dict()

    # Environment helpers
    from core.config import is_production, is_development, is_test
    if is_production():
        # Do production-specific setup
        pass
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Type, Callable
import yaml

# Module level variables for storing configuration
_config: Dict[str, Any] = {}
_runtime_overrides: Dict[str, Any] = {}
_schema: Dict[str, Any] = {}
_logger = logging.getLogger("dawn.config")

# Default configuration schema
DEFAULT_SCHEMA = {
    "environment": {
        "type": str,
        "default": "development",
        "env_var": "DAWN_ENVIRONMENT",
        "description": "Application environment (development, test, production)",
        "constraints": {
            "allowed_values": ["development", "test", "production"]
        }
    },
    "log_level": {
        "type": str,
        "default": "INFO",
        "env_var": "DAWN_LOG_LEVEL",
        "description": "Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        "constraints": {
            "allowed_values": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        }
    },
    "debug_mode": {
        "type": bool,
        "default": False,
        "env_var": "DAWN_DEBUG_MODE",
        "description": "Enable debug mode for additional logging and features"
    },
    "strict_config_validation": {
        "type": bool,
        "default": False,
        "env_var": "DAWN_STRICT_CONFIG_VALIDATION",
        "description": "Raise exceptions on configuration validation errors"
    },
    "llm_provider": {
        "type": str,
        "default": "openai",
        "env_var": "DAWN_LLM_PROVIDER",
        "description": "LLM provider to use (openai, anthropic, etc.)"
    },
    "llm_model": {
        "type": str,
        "default": "gpt-3.5-turbo",
        "env_var": "DAWN_LLM_MODEL",
        "description": "Default LLM model to use"
    },
    "llm_api_key": {
        "type": str,
        "default": None,
        "env_var": "DAWN_LLM_API_KEY",
        "description": "API key for the LLM provider",
        "sensitive": True,
        "nullable": True
    },
    "llm_temperature": {
        "type": float,
        "default": 0.7,
        "env_var": "DAWN_LLM_TEMPERATURE",
        "description": "Temperature setting for LLM calls",
        "constraints": {
            "min": 0.0,
            "max": 2.0
        }
    },
    "workflow_engine": {
        "type": dict,
        "default": {
            "max_retries": 3,
            "retry_delay": 2,
            "timeout": 600
        },
        "description": "Workflow engine configuration",
        "schema": {
            "max_retries": {
                "type": int,
                "default": 3,
                "description": "Maximum number of retries for failed tasks",
                "constraints": {
                    "min": 0,
                    "max": 10
                }
            },
            "retry_delay": {
                "type": int,
                "default": 2,
                "description": "Delay between retries in seconds",
                "constraints": {
                    "min": 0,
                    "max": 60
                }
            },
            "timeout": {
                "type": int,
                "default": 600,
                "description": "Maximum execution time for workflows in seconds",
                "constraints": {
                    "min": 0,
                    "max": 3600
                }
            }
        }
    },
    "vector_store": {
        "type": dict,
        "default": {
            "provider": "chroma",
            "path": "./data/vectors",
            "embedding_model": "all-MiniLM-L6-v2"
        },
        "description": "Vector database configuration",
        "schema": {
            "provider": {
                "type": str,
                "default": "chroma",
                "description": "Vector store provider to use"
            },
            "path": {
                "type": str,
                "default": "./data/vectors",
                "description": "Path to store vector data"
            },
            "embedding_model": {
                "type": str,
                "default": "all-MiniLM-L6-v2",
                "description": "Embedding model to use for vectors"
            }
        }
    },
    "http_server": {
        "type": dict,
        "default": {
            "host": "127.0.0.1",
            "port": 8080,
            "cors_origins": ["http://localhost:3000"]
        },
        "description": "HTTP server configuration",
        "schema": {
            "host": {
                "type": str,
                "default": "127.0.0.1",
                "description": "Host to bind the server to"
            },
            "port": {
                "type": int,
                "default": 8080,
                "description": "Port to bind the server to",
                "constraints": {
                    "min": 1,
                    "max": 65535
                }
            },
            "cors_origins": {
                "type": list,
                "default": ["http://localhost:3000"],
                "description": "Allowed CORS origins",
                "item_type": str
            }
        }
    },
    "data_directory": {
        "type": str,
        "default": "./data",
        "env_var": "DAWN_DATA_DIR",
        "description": "Directory for storing application data"
    },
    "cache_directory": {
        "type": str,
        "default": "./cache",
        "env_var": "DAWN_CACHE_DIR",
        "description": "Directory for caching data"
    },
    "tool_registry": {
        "type": dict,
        "default": {
            "tool_paths": ["./core/tools", "./plugins"],
            "auto_discover": True
        },
        "description": "Tool registry configuration",
        "schema": {
            "tool_paths": {
                "type": list,
                "default": ["./core/tools", "./plugins"],
                "description": "Paths to search for tools",
                "item_type": str
            },
            "auto_discover": {
                "type": bool,
                "default": True,
                "description": "Automatically discover tools in tool_paths"
            }
        }
    },
    "debug_mode.log_level": {
        "type": str,
        "default": "DEBUG",
        "description": "Logging level for debug mode",
        "constraints": {
            "allowed_values": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        }
    },
    "debug_mode.log_file": {
        "type": str,
        "default": None,
        "description": "File to write debug logs to",
        "nullable": True,
        "optional": True
    },
    "debug_mode.enable_web_panel": {
        "type": bool,
        "default": True,
        "description": "Enable web debug panel"
    },
    "debug_mode.enable_web_middleware": {
        "type": bool,
        "default": True,
        "description": "Enable debug middleware for web requests"
    },
    "debug_mode.performance_monitoring": {
        "type": bool,
        "default": True,
        "description": "Enable performance monitoring in debug mode"
    }
}

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
    else:
        # Look for config files in common locations
        common_paths = [
            Path("./config/config.json"),
            Path("./config/config.yaml"),
            Path("./config/config.yml"),
            Path("../config/config.json"),
            Path("../config/config.yaml"),
            Path("../config/config.yml"),
            Path("./config.json"),
            Path("./config.yaml"),
            Path("./config.yml"),
        ]
        
        for path in common_paths:
            if path.exists():
                _logger.info(f"Found config file at {path}")
                file_config = _load_config_file(str(path))
                _deep_update(_config, file_config)
                break
    
    # Override with environment-specific config if available
    env = environment or os.environ.get("DAWN_ENVIRONMENT", _config.get("environment", "development"))
    _config["environment"] = env
    
    # Try to load environment-specific config
    for env_path_template in [
        "./config/{env}.json",
        "./config/{env}.yaml",
        "./config/{env}.yml",
        "../config/{env}.json",
        "../config/{env}.yaml",
        "../config/{env}.yml",
        "./{env}.json",
        "./{env}.yaml",
        "./{env}.yml",
    ]:
        env_path = Path(env_path_template.format(env=env.lower()))
        if env_path.exists():
            _logger.info(f"Found environment-specific config at {env_path}")
            env_config = _load_config_file(str(env_path))
            _deep_update(_config, env_config)
            break
    
    # Override with environment variables
    env_config = _load_from_env(_schema)
    _deep_update(_config, env_config)
    
    # Add runtime overrides
    _deep_update(_config, _runtime_overrides)
    
    # Validate configuration
    _validate_config(_config, _schema)
    
    # Configure logging based on configuration
    _configure_logging()
    
    _logger.info(f"Configuration initialized for environment: {_config.get('environment')}")
    return _config

def reload() -> Dict[str, Any]:
    """Reload the configuration, keeping runtime overrides.
    
    Returns:
        Dict containing the complete configuration
    """
    _logger.info("Reloading configuration")
    old_env = _config.get("environment")
    return configure(environment=old_env)

def get(key: str, default: Any = None) -> Any:
    """Get a configuration value by key.
    
    Args:
        key: Configuration key (supports dot notation for nested values)
        default: Default value to return if key is not found
        
    Returns:
        Configuration value or default if not found
    """
    # Auto-initialize if not already done
    if not _config and not _schema:
        configure()
    
    # Handle dot notation for nested dicts
    if "." in key:
        parts = key.split(".")
        current = _config
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current
    
    return _config.get(key, default)

def set(key: str, value: Any) -> None:
    """Set a configuration value at runtime.
    
    Args:
        key: The configuration key (using dot notation for nested keys)
        value: The value to set
    """
    global _config, _runtime_overrides, _schema
    
    # Initialize if needed
    if not _config:
        configure()
    
    # Handle dotted keys
    if "." in key:
        parts = key.split(".")
        current = _runtime_overrides
        
        # Navigate/create the path in runtime_overrides
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]
        
        # Set the value at the leaf
        current[parts[-1]] = value
    else:
        _runtime_overrides[key] = value
    
    # Validate the new value if schema is available
    if _schema:
        # Create a temporary config with the new value
        temp_config = _config.copy()
        _deep_update(temp_config, _runtime_overrides)
        
        # Find schema entry for this key
        schema_entry = None
        if "." in key:
            # For nested keys like "workflow_engine.max_retries"
            parts = key.split(".")
            if parts[0] in _schema and isinstance(_schema[parts[0]], dict):
                if "schema" in _schema[parts[0]] and parts[1] in _schema[parts[0]]["schema"]:
                    schema_entry = _schema[parts[0]]["schema"][parts[1]]
                elif key in _schema:  # Check if the full dotted key exists
                    schema_entry = _schema[key]
        else:
            # For top-level keys
            if key in _schema:
                schema_entry = _schema[key]
        
        # Validate against schema entry if found
        if schema_entry:
            errors = []
            
            # Type validation
            if "type" in schema_entry and value is not None:
                expected_type = schema_entry["type"]
                
                if expected_type in (str, int, float, bool) and not isinstance(value, expected_type):
                    try:
                        # Try to convert
                        value = expected_type(value)
                        # Update the runtime override with the converted value
                        if "." in key:
                            current[parts[-1]] = value
                        else:
                            _runtime_overrides[key] = value
                    except (ValueError, TypeError):
                        errors.append(f"Configuration error: '{key}' should be of type {expected_type.__name__}")
                
                elif expected_type == dict and not isinstance(value, dict):
                    errors.append(f"Configuration error: '{key}' should be a dictionary")
                
                elif expected_type == list and not isinstance(value, list):
                    errors.append(f"Configuration error: '{key}' should be a list")
            
            # Constraints validation
            if not errors and "constraints" in schema_entry and value is not None:
                constraints = schema_entry["constraints"]
                
                # Check minimum value
                if "min" in constraints and value < constraints["min"]:
                    errors.append(f"Configuration error: '{key}' must be at least {constraints['min']}")
                
                # Check maximum value
                if "max" in constraints and value > constraints["max"]:
                    errors.append(f"Configuration error: '{key}' must be at most {constraints['max']}")
                
                # Check allowed values
                if "allowed_values" in constraints and value not in constraints["allowed_values"]:
                    errors.append(f"Configuration error: '{key}' must be one of {constraints['allowed_values']}")
                
                # Check regex pattern
                if "pattern" in constraints and isinstance(value, str):
                    import re
                    if not re.match(constraints["pattern"], value):
                        errors.append(f"Configuration error: '{key}' must match pattern '{constraints['pattern']}'")
            
            # Raise error if validation failed and strict mode is enabled
            if errors and get("strict_config_validation", False):
                error_summary = "\n".join(errors)
                raise ValueError(f"Configuration validation failed:\n{error_summary}")
            elif errors:
                for error in errors:
                    _logger.warning(error)
    
    # Update the actual config
    _update_config_with_overrides()
    
    _logger.debug(f"Configuration updated: {key} = {value}")

def _update_config_with_overrides() -> None:
    """Update the configuration with runtime overrides."""
    global _config, _runtime_overrides
    
    # Start with the base config
    for section in _config:
        if section in _runtime_overrides and isinstance(_config[section], dict) and isinstance(_runtime_overrides[section], dict):
            # Deep update for nested dictionaries
            _deep_update(_config[section], _runtime_overrides[section])
        elif section in _runtime_overrides:
            # Direct override for simple values
            _config[section] = _runtime_overrides[section]
    
    # Add any new sections from runtime overrides
    for section in _runtime_overrides:
        if section not in _config:
            _config[section] = _runtime_overrides[section]

def as_dict() -> Dict[str, Any]:
    """Get the complete configuration as a dictionary.
    
    Returns:
        Dict containing the complete configuration
    """
    # Auto-initialize if not already done
    if not _config and not _schema:
        configure()
        
    return _config

def is_production() -> bool:
    """Check if running in production environment.
    
    Returns:
        True if environment is set to production
    """
    return get("environment", "").lower() == "production"

def is_development() -> bool:
    """Check if running in development environment.
    
    Returns:
        True if environment is set to development
    """
    return get("environment", "").lower() == "development"

def is_test() -> bool:
    """Check if running in test environment.
    
    Returns:
        True if environment is set to test
    """
    return get("environment", "").lower() == "test"

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
                return yaml.safe_load(f) or {}
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
    
    # Look for prefixed environment variables for nested configurations
    for env_name, env_value in os.environ.items():
        if env_name.startswith("DAWN_"):
            parts = env_name.lower().split("_")
            if len(parts) > 2:
                # Build nested structure for longer prefixes
                # e.g., DAWN_HTTP_SERVER_PORT -> http_server.port
                section = parts[1]
                subsection = "_".join(parts[2:-1]) if len(parts) > 3 else parts[2]
                value_key = parts[-1]
                
                # Check for direct matches in schema first
                direct_key = f"{section}.{subsection}.{value_key}" if len(parts) > 3 else f"{section}.{value_key}"
                found = False
                
                for schema_key, schema_info in schema.items():
                    if isinstance(schema_info, dict) and "env_var" in schema_info and schema_info["env_var"] == env_name:
                        found = True
                        break
                
                if not found:
                    # Convert to the appropriate type if we can infer it
                    if env_value.lower() in ('true', 'false', 't', 'f', 'yes', 'no', 'y', 'n', '1', '0'):
                        env_value = env_value.lower() in ('true', 't', 'yes', 'y', '1')
                    elif env_value.isdigit():
                        env_value = int(env_value)
                    elif env_value.replace('.', '', 1).isdigit() and env_value.count('.') == 1:
                        env_value = float(env_value)
                    
                    # Add to nested config
                    if len(parts) > 3:
                        if section not in result:
                            result[section] = {}
                        if subsection not in result[section]:
                            result[section][subsection] = {}
                        result[section][subsection][value_key] = env_value
                    else:
                        if section not in result:
                            result[section] = {}
                        result[section][value_key] = env_value
    
    return result

def _validate_config(config: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """Validate configuration against schema.
    
    Args:
        config: Configuration to validate
        schema: Configuration schema
        
    Returns:
        True if validation passed, False otherwise
    """
    validation_passed = True
    validation_errors = []
    
    # Validate top-level keys
    for key, info in schema.items():
        # Skip optional keys that aren't specified
        if key not in config and info.get("optional", False):
            continue
            
        # Check if required keys are present
        if key not in config:
            validation_errors.append(f"Missing required configuration key: '{key}'")
            validation_passed = False
            continue
            
        # Skip null values for nullable fields
        if config[key] is None and info.get("nullable", False):
            continue
            
        # Validate type if specified
        if "type" in info and config[key] is not None:
            expected_type = info["type"]
            
            # Handle different type specifications
            if expected_type == dict:
                if not isinstance(config[key], dict):
                    validation_errors.append(f"Configuration error: '{key}' should be a dictionary")
                    validation_passed = False
                elif "schema" in info and isinstance(info["schema"], dict):
                    # Recursively validate nested dictionary
                    nested_valid = _validate_config(config[key], info["schema"])
                    if not nested_valid:
                        validation_passed = False
                        
            elif expected_type == list:
                if not isinstance(config[key], list):
                    validation_errors.append(f"Configuration error: '{key}' should be a list")
                    validation_passed = False
                elif "item_type" in info:
                    # Validate each item in the list
                    item_type = info["item_type"]
                    for i, item in enumerate(config[key]):
                        if not isinstance(item, item_type):
                            validation_errors.append(
                                f"Configuration error: Item {i} in '{key}' should be of type {item_type.__name__}"
                            )
                            validation_passed = False
                            
            elif expected_type in (str, int, float, bool):
                if not isinstance(config[key], expected_type):
                    # Try to convert to the right type
                    try:
                        config[key] = expected_type(config[key])
                        _logger.debug(f"Converted '{key}' from {type(config[key]).__name__} to {expected_type.__name__}")
                    except (ValueError, TypeError):
                        validation_errors.append(
                            f"Configuration error: '{key}' should be of type {expected_type.__name__}"
                        )
                        validation_passed = False
        
        # Validate value against constraints if specified
        if validation_passed and "constraints" in info and config[key] is not None:
            constraints = info["constraints"]
            
            # Check minimum value
            if "min" in constraints and config[key] < constraints["min"]:
                validation_errors.append(
                    f"Configuration error: '{key}' must be at least {constraints['min']}"
                )
                validation_passed = False
                
            # Check maximum value
            if "max" in constraints and config[key] > constraints["max"]:
                validation_errors.append(
                    f"Configuration error: '{key}' must be at most {constraints['max']}"
                )
                validation_passed = False
                
            # Check allowed values
            if "allowed_values" in constraints and config[key] not in constraints["allowed_values"]:
                validation_errors.append(
                    f"Configuration error: '{key}' must be one of {constraints['allowed_values']}"
                )
                validation_passed = False
                
            # Check regex pattern
            if "pattern" in constraints and isinstance(config[key], str):
                import re
                if not re.match(constraints["pattern"], config[key]):
                    validation_errors.append(
                        f"Configuration error: '{key}' must match pattern '{constraints['pattern']}'"
                    )
                    validation_passed = False
    
    # Log validation errors
    if validation_errors:
        for error in validation_errors:
            _logger.warning(error)
        
        # Optional: raise an exception on validation failure
        if get("strict_config_validation", False):
            error_summary = "\n".join(validation_errors)
            raise ValueError(f"Configuration validation failed:\n{error_summary}")
    
    return validation_passed

def _deep_update(target: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
    """Deep update target dict with source.
    
    Args:
        target: Target dictionary to update
        source: Source dictionary
        
    Returns:
        Updated target dictionary
    """
    for key, value in source.items():
        if isinstance(value, dict) and key in target and isinstance(target[key], dict):
            _deep_update(target[key], value)
        else:
            target[key] = value
    return target

def _configure_logging() -> None:
    """Configure logging based on configuration."""
    log_level_name = get("log_level", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    
    # Configure root logger
    logging.getLogger().setLevel(log_level)
    
    # Update logger for this module
    global _logger
    _logger.setLevel(log_level)
    
    _logger.debug("Logging configured with level: %s", log_level_name)

# Auto-initialize config if this module is imported directly
if __name__ != "__main__":
    configure() 