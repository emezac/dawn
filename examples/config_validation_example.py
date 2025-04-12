#!/usr/bin/env python3
"""
Dawn Framework Configuration Validation Example

This example demonstrates the configuration validation features of the Dawn Framework.
It shows how to define custom schema, validate configuration, and handle validation errors.

To run this example:
python examples/config_validation_example.py
"""  # noqa: D202

import os
import sys
import json
import logging
from pathlib import Path

# Add the project root to the Python path if needed
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import configuration utilities
from core.config import configure, get, set, as_dict, reload

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("config_validation_example")

def create_example_config():
    """Create example configuration files for demonstration."""
    config_dir = Path("./example_config")
    config_dir.mkdir(exist_ok=True)
    
    # Create a base config file with some intentional errors
    config_file = config_dir / "config.json"
    config_data = {
        "environment": "development",
        "log_level": "INFO",
        "debug_mode": True,
        "llm_provider": "openai",
        "llm_model": "gpt-3.5-turbo",
        "llm_temperature": 3.0,  # Invalid: above the max of 2.0
        "workflow_engine": {
            "max_retries": 20,  # Invalid: above the max of 10
            "retry_delay": 2,
            "timeout": 300
        },
        "http_server": {
            "host": "127.0.0.1",
            "port": 70000,  # Invalid: above the max port number
            "cors_origins": ["http://localhost:3000"]
        }
    }
    
    with open(config_file, 'w') as f:
        json.dump(config_data, f, indent=2)
    logger.info(f"Created example config file with validation errors: {config_file}")
    
    # Create a valid config file
    valid_config_file = config_dir / "valid_config.json"
    valid_config_data = {
        "environment": "development",
        "log_level": "INFO",
        "debug_mode": True,
        "llm_provider": "openai",
        "llm_model": "gpt-3.5-turbo",
        "llm_temperature": 0.7,  # Valid
        "workflow_engine": {
            "max_retries": 5,     # Valid
            "retry_delay": 2,
            "timeout": 300
        },
        "http_server": {
            "host": "127.0.0.1",
            "port": 8080,        # Valid
            "cors_origins": ["http://localhost:3000"]
        }
    }
    
    with open(valid_config_file, 'w') as f:
        json.dump(valid_config_data, f, indent=2)
    logger.info(f"Created valid example config file: {valid_config_file}")
    
    # Create a config file with custom fields
    custom_config_file = config_dir / "custom_config.json"
    custom_config_data = {
        "environment": "development",
        "custom_field": "custom value",
        "custom_nested": {
            "nested_field": 42
        }
    }
    
    with open(custom_config_file, 'w') as f:
        json.dump(custom_config_data, f, indent=2)
    logger.info(f"Created custom example config file: {custom_config_file}")
    
    return config_dir

def run_example():
    """Run the configuration validation example."""
    logger.info("Starting Configuration Validation Example")
    
    try:
        # Create example configuration files
        config_dir = create_example_config()
        
        # Example 1: Load configuration with validation errors
        logger.info("\n=== Example 1: Configuration with Validation Errors ===")
        try:
            # Enable strict validation to see validation errors
            os.environ["DAWN_STRICT_CONFIG_VALIDATION"] = "true"
            
            configure(config_paths=[str(config_dir / "config.json")])
        except ValueError as e:
            logger.info(f"Caught validation error (as expected): {e}")
        
        # Disable strict validation for the next examples
        os.environ["DAWN_STRICT_CONFIG_VALIDATION"] = "false"
        
        # Example 2: Load valid configuration
        logger.info("\n=== Example 2: Valid Configuration ===")
        configure(config_paths=[str(config_dir / "valid_config.json")])
        
        # Show configuration values
        logger.info("Configuration values:")
        logger.info(f"  environment: {get('environment')}")
        logger.info(f"  log_level: {get('log_level')}")
        logger.info(f"  llm_temperature: {get('llm_temperature')}")
        logger.info(f"  workflow_engine.max_retries: {get('workflow_engine.max_retries')}")
        logger.info(f"  http_server.port: {get('http_server.port')}")
        
        # Example 3: Custom Schema Validation
        logger.info("\n=== Example 3: Custom Schema Validation ===")
        
        # Define a custom schema
        custom_schema = {
            "environment": {
                "type": str,
                "default": "development",
                "description": "Application environment"
            },
            "custom_field": {
                "type": str,
                "description": "A custom configuration field"
            },
            "custom_nested": {
                "type": dict,
                "description": "A nested configuration object",
                "schema": {
                    "nested_field": {
                        "type": int,
                        "description": "A nested field",
                        "constraints": {
                            "min": 0,
                            "max": 100
                        }
                    }
                }
            }
        }
        
        # Configure with custom schema
        configure(
            config_paths=[str(config_dir / "custom_config.json")],
            schema=custom_schema
        )
        
        # Show custom configuration values
        logger.info("Custom configuration values:")
        logger.info(f"  environment: {get('environment')}")
        logger.info(f"  custom_field: {get('custom_field')}")
        logger.info(f"  custom_nested.nested_field: {get('custom_nested.nested_field')}")
        
        # Example 4: Setting invalid values at runtime
        logger.info("\n=== Example 4: Setting Invalid Values at Runtime ===")
        
        # Enable strict validation again
        set("strict_config_validation", True)
        
        try:
            # Try to set an invalid value
            set("llm_temperature", 5.0)  # Should fail (above max of 2.0)
        except ValueError as e:
            logger.info(f"Caught validation error on set (as expected): {e}")
        
        # Set a valid value
        set("llm_temperature", 0.5)  # Should work
        logger.info(f"Set llm_temperature to valid value: {get('llm_temperature')}")
        
        # Clean up
        import shutil
        if config_dir.exists():
            prompt = input("\nClean up example files? (y/n): ").strip().lower()
            if prompt in ('y', 'yes'):
                shutil.rmtree(config_dir)
                logger.info(f"Removed example config directory: {config_dir}")
            else:
                logger.info(f"Example config files left at: {config_dir}")
        
        logger.info("\nConfiguration Validation Example completed.")
        
    except Exception as e:
        logger.error(f"Error in configuration validation example: {e}", exc_info=True)

if __name__ == "__main__":
    run_example() 