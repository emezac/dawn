# Dawn Framework Configuration System

This document describes the unified configuration system used in the Dawn Framework.

## Overview

The Dawn Framework uses a centralized configuration system that supports multiple configuration sources with a clear precedence order. This allows for flexible configuration across different environments while maintaining sensible defaults.

## Configuration Sources

Configuration values are loaded from the following sources in order of precedence (highest to lowest):

1. **Runtime Overrides**: Values set programmatically during execution via the `set()` function
2. **Environment Variables**: Values set as environment variables with the prefix `DAWN_`
3. **Environment-Specific Config Files**: Values from environment-specific configuration files (e.g., `production.json`)
4. **Base Config File**: Values from the base configuration file (e.g., `config.json`)
5. **Default Values**: Default values defined in the configuration schema

## Basic Usage

### Initialization

You should initialize the configuration system at application startup:

```python
from core.config import configure

# Initialize with configuration files
configure(config_paths=["config/config.json", "config/production.json"])

# Or with explicit environment
configure(config_paths=["config/config.json"], environment="production")
```

### Accessing Configuration

Use the `get()` function to access configuration values:

```python
from core.config import get

# Get a top-level configuration value
log_level = get("log_level")

# Get a nested configuration value using dot notation
server_port = get("http_server.port")

# Get with a default value (if the key doesn't exist)
timeout = get("custom_timeout", 30)
```

### Setting Runtime Overrides

Use the `set()` function to override configuration values at runtime:

```python
from core.config import set

# Override a configuration value
set("log_level", "DEBUG")

# Override a nested configuration value
set("workflow_engine.max_retries", 5)
```

### Environment Helpers

Use helper functions to check the current environment:

```python
from core.config import is_production, is_development, is_test

if is_production():
    # Connect to production resources
    ...
elif is_development():
    # Use development settings
    ...
```

### Getting All Configuration

Get the complete configuration as a dictionary:

```python
from core.config import as_dict

# Get all configuration values
config = as_dict()
```

## Environment Variables

You can override any configuration value using environment variables with the prefix `DAWN_`. Nested keys are separated by double underscores.

Examples:

- `DAWN_LOG_LEVEL=DEBUG`
- `DAWN_HTTP_SERVER__PORT=8080`
- `DAWN_WORKFLOW_ENGINE__MAX_RETRIES=5`

## Configuration Files

The configuration system supports both JSON and YAML files. Files are loaded in the order specified, with later files overriding values from earlier files.

Example configuration structure:

```json
{
  "environment": "development",
  "log_level": "INFO",
  "debug_mode": true,
  "llm_provider": "openai",
  "llm_model": "gpt-3.5-turbo",
  "workflow_engine": {
    "max_retries": 3,
    "retry_delay": 2,
    "timeout": 300
  },
  "http_server": {
    "host": "127.0.0.1",
    "port": 8000
  }
}
```

## Environment-Specific Configuration

You can create environment-specific configuration files to override values for different environments:

- `config.json` - Base configuration
- `development.json` - Development environment overrides
- `test.json` - Test environment overrides
- `production.json` - Production environment overrides

The environment is determined by:

1. The `environment` parameter passed to `configure()`
2. The `DAWN_ENVIRONMENT` environment variable
3. The `environment` value in the configuration files
4. Default to "development" if not specified

## Configuration Schema

The configuration system uses a schema to validate configuration values and provide default values. The schema defines the type, default value, and description for each configuration key.

## Sensitive Configuration Values

Sensitive values (like API keys and passwords) are handled specially:

- They are masked in logs and when printing the configuration
- They can be loaded from environment variables for better security
- They are identified by key patterns: keys ending with "_key", "_secret", or containing "password"

## Complete Example

See `examples/using_config.py` for a complete example of using the configuration system.

## API Reference

### `configure(config_paths=None, environment=None)`

Initialize the configuration system.

- `config_paths`: List of paths to configuration files
- `environment`: Explicitly set the environment

### `get(key, default=None)`

Get a configuration value.

- `key`: The configuration key (can use dot notation for nested keys)
- `default`: Default value to return if the key doesn't exist

### `set(key, value)`

Set a runtime override for a configuration value.

- `key`: The configuration key (can use dot notation for nested keys)
- `value`: The value to set

### `as_dict()`

Get the complete configuration as a dictionary.

### `is_production()`

Check if the current environment is production.

### `is_development()`

Check if the current environment is development.

### `is_test()`

Check if the current environment is test.

### `reload()`

Reload the configuration from all sources. 