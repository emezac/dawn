#!/usr/bin/env python3
"""
Dawn Framework Configuration System Example

This example demonstrates how to use the Dawn Framework's unified
configuration system to configure, access, and leverage settings in your
workflows and applications.

This example covers:
1. Configuring the system at startup
2. Accessing configuration values
3. Using environment-specific settings
4. Defining workflow behavior based on configuration
"""  # noqa: D202

import os
import sys
import json
import time
import random
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Make sure core modules are in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import configuration system
from core.config import configure, get, set, is_development, is_production
from core.workflow.engine import WorkflowEngine
from core.workflow.task import Task
from core.workflow.workflow import Workflow

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample configuration
SAMPLE_CONFIG = {
    "environment": "development",  # development, testing, production
    "llm_provider": "openai",
    "llm_model": "gpt-3.5-turbo",
    "max_retries": 3,
    "debug_mode": True,
    "api_endpoint": "https://api.example.com/v1"
}


def setup_configuration():
    """Initialize and set up the configuration system."""
    logger.info("Setting up configuration system...")
    
    # Determine where we're running
    env = os.getenv("DAWN_ENVIRONMENT", "development")
    
    # Look for configuration file in multiple locations
    config_paths = [
        f"./config/{env}.yaml",
        "./config/config.yaml",
        "./config.yaml"
    ]
    
    # Create config directory if it doesn't exist
    os.makedirs("./config", exist_ok=True)
    
    # If no configuration file exists, create a sample one
    if not any(os.path.exists(path) for path in config_paths):
        logger.info("No configuration file found, creating sample config...")
        with open("./config/config.yaml", "w") as f:
            import yaml
            yaml.dump(SAMPLE_CONFIG, f)
        
        # Add sample config path
        config_paths.append("./config/config.yaml")
    
    # Initialize the configuration system
    try:
        configure(config_paths=config_paths, environment=env)
        logger.info(f"Configuration loaded successfully for environment: {get('environment')}")
        
        # Override a value at runtime
        if is_development():
            set("debug_mode", True)
            logger.info("Debug mode enabled for development environment")
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        sys.exit(1)


def create_configuration_workflow() -> Workflow:
    """Create a workflow that demonstrates configuration usage."""
    workflow = Workflow(name="configuration_example_workflow")
    
    # Task 1: Check current configuration
    async def check_configuration(context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Task 1: Checking configuration settings")
        
        # Access configuration values
        env = get("environment")
        model = get("llm_model")
        debug = get("debug_mode", False)
        
        logger.info(f"Current environment: {env}")
        logger.info(f"Using LLM model: {model}")
        logger.info(f"Debug mode: {'enabled' if debug else 'disabled'}")
        
        # Store values in context for downstream tasks
        return {
            "environment": env,
            "model": model,
            "debug_mode": debug,
            "api_endpoint": get("api_endpoint"),
            "max_retries": get("max_retries", 3)
        }
    
    # Task 2: Simulate API call with configurable retry logic
    async def make_api_call(context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Task 2: Making API call with retry logic")
        
        api_endpoint = context.get("api_endpoint", "https://default-api.example.com")
        max_retries = context.get("max_retries", 3)
        
        logger.info(f"API endpoint: {api_endpoint}")
        logger.info(f"Max retries: {max_retries}")
        
        # Simulate an API call with potential failures
        success = False
        attempts = 0
        error = None
        
        # In development mode, use a higher failure rate to test retry logic
        failure_rate = 0.7 if is_development() else 0.3
        
        while not success and attempts < max_retries:
            attempts += 1
            logger.info(f"API call attempt {attempts}/{max_retries}")
            
            # Simulate API call with random success/failure
            if random.random() > failure_rate:
                logger.info("API call succeeded")
                success = True
                break
            else:
                error = "Simulated API error"
                logger.warning(f"API call failed: {error}, retrying in 1 second...")
                time.sleep(1)  # Wait before retrying
        
        # Return result
        if success:
            return {
                "api_result": {
                    "status": "success",
                    "data": {"message": "API call completed successfully"},
                    "attempts": attempts
                }
            }
        else:
            logger.error(f"API call failed after {attempts} attempts")
            return {
                "api_result": {
                    "status": "error",
                    "error": error,
                    "attempts": attempts
                }
            }
    
    # Task 3: Process results according to environment
    async def process_results(context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Task 3: Processing results according to environment")
        
        api_result = context.get("api_result", {})
        environment = context.get("environment", "development")
        
        if api_result.get("status") == "success":
            logger.info("Processing successful API result")
            
            # Different processing logic based on environment
            if is_production():
                logger.info("Production mode: Storing result in production database")
                # Simulate production-specific processing
                return {
                    "processed_result": {
                        "env": environment,
                        "status": "processed",
                        "production_id": random.randint(10000, 99999)
                    }
                }
            else:
                logger.info(f"Non-production mode ({environment}): Using simplified processing")
                # Simulate dev/test processing
                return {
                    "processed_result": {
                        "env": environment,
                        "status": "processed",
                        "debug_info": f"Processed with {context.get('model')}"
                    }
                }
        else:
            logger.warning("Processing error result")
            
            # Error handling differs by environment
            if is_production():
                logger.error("Production error: Would send alert to operations team")
                return {
                    "processed_result": {
                        "status": "error",
                        "action": "alert_ops",
                        "severity": "high"
                    }
                }
            else:
                logger.warning(f"Development error: Detailed diagnostics for debugging")
                return {
                    "processed_result": {
                        "status": "error",
                        "action": "log_only",
                        "debug_data": api_result
                    }
                }
    
    # Task 4: Final task (always runs, regardless of previous task success/failure)
    async def complete_workflow(context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Task 4: Completing workflow")
        
        # Access processed results
        processed_result = context.get("processed_result", {})
        
        # Get configuration to determine logging verbosity
        debug_mode = get("debug_mode", False)
        
        if debug_mode:
            # In debug mode, log detailed information
            logger.info(f"Debug details: {json.dumps(context, indent=2)}")
        
        # Workflow completion logic
        logger.info(f"Workflow completed with status: {processed_result.get('status', 'unknown')}")
        return {
            "workflow_status": processed_result.get("status", "unknown"),
            "completion_time": time.time(),
            "environment": get("environment")
        }
    
    # Register tasks with the workflow
    workflow.add_task(Task(name="check_configuration", handler=check_configuration))
    workflow.add_task(Task(name="make_api_call", handler=make_api_call, 
                         depends_on=["check_configuration"]))
    workflow.add_task(Task(name="process_results", handler=process_results,
                         depends_on=["make_api_call"]))
    workflow.add_task(Task(name="complete_workflow", handler=complete_workflow,
                         depends_on=["process_results"], always_run=True))
    
    return workflow


def main():
    """Main function to run the configuration example."""
    logger.info("Starting configuration example")
    
    # Setup configuration
    setup_configuration()
    
    # Create and run the workflow
    workflow = create_configuration_workflow()
    engine = WorkflowEngine()
    
    logger.info("Running configuration example workflow")
    try:
        result = engine.run_workflow(workflow)
        logger.info(f"Workflow completed successfully")
        logger.info(f"Final workflow status: {result.get('workflow_status', 'unknown')}")
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
    
    logger.info("Configuration example completed")


if __name__ == "__main__":
    main() 