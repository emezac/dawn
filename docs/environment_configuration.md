# Environment-Specific Configuration

The Dawn framework includes a robust configuration system that supports different environments (development, testing, production) with environment-specific settings. This document explains how to use and customize these configurations.

## Configuration Environments

The framework supports three main environments, each with its own configuration file:

1. **Development** (`config/development.json`): Used during active development, with verbose logging and developer-friendly settings.
2. **Testing** (`config/testing.json`): Used for automated tests, with mock components and minimal external dependencies.
3. **Production** (`config/production.json`): Used for production deployments, with optimized performance and security settings.

## Configuration Loading Order

The configuration system loads settings from multiple sources with the following precedence (highest to lowest):

1. **Runtime overrides**: Set via the `config.set()` function
2. **Environment variables**: Prefixed with `DAWN_` (e.g., `DAWN_LOG_LEVEL=DEBUG`)
3. **Environment-specific config file**: Based on the active environment
4. **Base config file**: Default settings in `config/config.json` (if it exists)
5. **Default schema values**: Built-in defaults defined in the configuration schema

## Using Environment Configuration

### Accessing Configuration Values

```python
from core.config import get, is_production, is_development, is_test

# Get a simple configuration value
debug = get("debug_mode")

# Get a nested configuration value using dot notation
retries = get("workflow_engine.max_retries")

# Get a value with a default fallback
port = get("http_server.port", 8080)

# Environment-specific logic
if is_production():
    # Production-specific code
elif is_development():
    # Development-specific code
elif is_test():
    # Testing-specific code
```

### Setting Configuration Values at Runtime

```python
from core.config import set

# Override a configuration value
set("llm_model", "gpt-4")

# Override a nested configuration value
set("workflow_engine.timeout", 300)
```

### Reloading Configuration

```python
from core.config import reload

# Reload configuration from files and environment variables
reload()
```

## Configuration Structure

The configuration files use a standardized structure with the following top-level sections:

### Core Settings

```json
{
  "environment": "development|testing|production",
  "debug_mode": true|false,
  "log_level": "DEBUG|INFO|WARNING|ERROR|CRITICAL",
  "strict_config_validation": true|false
}
```

### LLM Settings

```json
{
  "llm_provider": "openai|anthropic|mock",
  "llm_model": "gpt-3.5-turbo|gpt-4|claude-3-opus-20240229",
  "llm_temperature": 0.7,
  "llm_api_key": "sk-..." // Better to use env var DAWN_LLM_API_KEY
}
```

### Workflow Engine Settings

```json
{
  "workflow_engine": {
    "max_retries": 3,
    "retry_delay": 2,
    "timeout": 600
  }
}
```

### Vector Store Settings

```json
{
  "vector_store": {
    "provider": "chroma|in-memory",
    "path": "./data/vectors",
    "embedding_model": "all-MiniLM-L6-v2"
  }
}
```

### HTTP Server Settings

```json
{
  "http_server": {
    "host": "127.0.0.1",
    "port": 8080,
    "cors_origins": ["http://localhost:3000"]
  }
}
```

### Data and Cache Directories

```json
{
  "data_directory": "./data",
  "cache_directory": "./cache"
}
```

### Tool Registry Settings

```json
{
  "tool_registry": {
    "tool_paths": ["./core/tools", "./plugins"],
    "auto_discover": true
  }
}
```

### Chat Planner Settings

```json
{
  "chat_planner": {
    "llm_model": "gpt-3.5-turbo",
    "llm_temperature": 0.7,
    "max_tokens": 2000,
    "enable_plan_validation": true,
    "validation_strictness": "medium",
    "prompts": {
      "ambiguity_check": "",
      "planning": "",
      "plan_validation": "",
      "summarization": ""
    }
  }
}
```

## Environment-Specific Configuration Recommendations

### Development

The development environment prioritizes:
- Verbose logging and debugging information
- Local paths for data storage
- Fast iteration with simplified validation
- Development-oriented LLM models (cost vs. capability balance)

### Testing

The testing environment prioritizes:
- Mocked components for deterministic testing
- Minimal external dependencies
- Fast execution with reduced timeouts
- Separate test data paths to avoid conflicts

### Production

The production environment prioritizes:
- Security and stability
- Performance optimization
- Appropriate log levels for operational monitoring
- More robust error handling and retries
- Production-quality LLM models

## Customizing Configuration for Your Project

To customize the configuration for your project:

1. Start with the provided environment templates
2. Modify settings to match your project requirements
3. For component-specific configurations, add new sections following the existing pattern
4. Ensure all environments have appropriate values for your added sections

## Using Environment Variables

For sensitive information or deployment-specific settings, use environment variables instead of hardcoding values in configuration files:

```bash
# Example environment variables
export DAWN_ENVIRONMENT=production
export DAWN_LLM_API_KEY=sk-your-api-key
export DAWN_LLM_MODEL=gpt-4
```

The configuration system will automatically use these values if provided.

## Adding Custom Configuration Schemas

If you need to extend the configuration schema for your project:

```python
from core.config import add_schema_section

add_schema_section({
    "my_component": {
        "type": dict,
        "default": {
            "feature_enabled": True,
            "timeout": 30
        },
        "description": "My component configuration",
        "schema": {
            "feature_enabled": {
                "type": bool,
                "default": True,
                "description": "Enable the feature"
            },
            "timeout": {
                "type": int,
                "default": 30,
                "description": "Timeout in seconds",
                "constraints": {
                    "min": 1,
                    "max": 300
                }
            }
        }
    }
})
```

## Best Practices

1. **Environment-Specific Settings**: Use different settings for development, testing, and production environments
2. **Sensitive Data**: Never store sensitive data (API keys, credentials) in configuration files
3. **Documentation**: Document custom configuration sections in your project
4. **Validation**: Use `strict_config_validation=true` in production to catch configuration errors early
5. **Defaults**: Provide sensible defaults for all configuration values
6. **Minimal Overrides**: Override only the necessary settings in each environment 