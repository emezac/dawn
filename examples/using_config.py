#!/usr/bin/env python3
"""
Dawn Framework Configuration System Example

This example demonstrates how to use the Dawn Framework's configuration system.
It shows loading configuration from files, environment variables, and runtime overrides.

To run this example:
python examples/using_config.py

The example will create a temporary config directory with example configuration files,
initialize the configuration system, and demonstrate various configuration operations.
"""  # noqa: D202

import os
import sys
import json
import logging
import shutil
from pathlib import Path

# Add the project root to the Python path if needed
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import configure, get, set, as_dict, is_production, is_development, is_test

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("config_example")

def create_example_config():
    """Create example configuration files for demonstration."""
    config_dir = Path("./example_config")
    config_dir.mkdir(exist_ok=True)
    
    # Create a base config file
    config_file = config_dir / "config.json"
    config_data = {
        "environment": "development",
        "log_level": "INFO",
        "debug_mode": True,
        "llm_provider": "openai",
        "llm_model": "gpt-3.5-turbo",
        "workflow_engine": {
            "max_retries": 3,
            "retry_delay": 2,
            "timeout": 300
        },
        "vector_store": {
            "provider": "chroma",
            "path": "./data/vectors",
            "embedding_model": "all-MiniLM-L6-v2"
        },
        "http_server": {
            "host": "127.0.0.1",
            "port": 8000,
            "cors_origins": ["http://localhost:3000"]
        }
    }
    
    with open(config_file, 'w') as f:
        json.dump(config_data, f, indent=2)
    logger.info(f"Created base config file: {config_file}")
    
    # Create a production config file
    prod_config_file = config_dir / "production.json"
    prod_config_data = {
        "environment": "production",
        "log_level": "WARNING",
        "debug_mode": False,
        "workflow_engine": {
            "max_retries": 5,
            "timeout": 600
        },
        "http_server": {
            "host": "0.0.0.0",
            "port": 8080,
            "cors_origins": ["https://app.example.com"]
        }
    }
    
    with open(prod_config_file, 'w') as f:
        json.dump(prod_config_data, f, indent=2)
    logger.info(f"Created production config file: {prod_config_file}")
    
    return config_dir

def run_example():
    """Run the configuration system example."""
    try:
        # Create example configuration files
        config_dir = create_example_config()
        
        # Initialize configuration with the base config file only
        logger.info("Initializing configuration with base config file")
        configure(config_paths=[str(config_dir / "config.json")])
        
        # Demonstrate accessing configuration values
        logger.info(f"Current environment: {get('environment')}")
        logger.info(f"LLM model: {get('llm_model')}")
        logger.info(f"Debug mode: {get('debug_mode')}")
        logger.info(f"HTTP server port: {get('http_server.port')}")  # Using dot notation
        logger.info(f"Vector store provider: {get('vector_store.provider')}")
        
        # Demonstrate environment helpers
        logger.info(f"Is development? {is_development()}")
        logger.info(f"Is production? {is_production()}")
        
        # Demonstrate loading environment-specific configuration
        logger.info("\nSwitching to production environment")
        configure(config_paths=[
            str(config_dir / "config.json"),
            str(config_dir / "production.json")
        ])
        
        logger.info(f"Current environment: {get('environment')}")
        logger.info(f"Debug mode: {get('debug_mode')}")
        logger.info(f"HTTP server port: {get('http_server.port')}")
        logger.info(f"Is production? {is_production()}")
        
        # Demonstrate runtime overrides
        logger.info("\nDemonstrating runtime overrides")
        set("llm_model", "gpt-4")
        set("workflow_engine.max_retries", 10)
        logger.info(f"LLM model after override: {get('llm_model')}")
        logger.info(f"Max retries after override: {get('workflow_engine.max_retries')}")
        
        # Print complete configuration
        logger.info("\nComplete configuration (with sensitive values masked):")
        config = as_dict()
        # Set a sensitive value for demonstration
        set("llm_api_key", "sk-12345abcdef")
        
        # Print config with sensitive values masked
        for key, value in as_dict().items():
            if isinstance(value, dict):
                logger.info(f"{key}: {value}")
            else:
                # Mask sensitive values
                if key.endswith("_key") or key.endswith("_secret") or "password" in key:
                    logger.info(f"{key}: ***MASKED***")
                else:
                    logger.info(f"{key}: {value}")
        
        # Ask if user wants to clean up example files
        cleanup = input("\nClean up example files? (y/n): ").strip().lower()
        if cleanup in ('y', 'yes'):
            shutil.rmtree(config_dir)
            logger.info(f"Removed example config directory: {config_dir}")
        else:
            logger.info(f"Example config files left at: {config_dir}")
            
    except Exception as e:
        logger.error(f"Error in configuration example: {e}", exc_info=True)

if __name__ == "__main__":
    run_example() 