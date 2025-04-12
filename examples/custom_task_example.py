"""
Custom Task Type Example (Minimal)

This example demonstrates how to create custom task types with their own execution strategies.
"""

import os
import sys
import logging
from typing import Dict, Any, List, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from core.task import CustomTask, Task, DirectHandlerTask
from core.task_execution_strategy import TaskExecutionStrategy, TaskExecutionStrategyFactory
from core.workflow import Workflow
from core.engine import WorkflowEngine
from core.llm.interface import LLMInterface
from core.tools.registry_access import get_registry
from core.services import get_services
from core.utils.logger import log_info, log_error

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================
# 1. Define a custom task type
# =============================================

class SimpleDataTask(CustomTask):
    """A simple custom task type for data operations."""  # noqa: D202
    
    def __init__(
        self,
        task_id: str,
        name: str,
        operation: str,  # Operation to perform: "uppercase", "double", etc.
        input_data: Dict[str, Any] = None,
        **kwargs
    ):
        """Initialize a simple data task."""
        super().__init__(
            task_id=task_id,
            name=name,
            task_type="simple_data",
            input_data=input_data,
            is_llm_task=True,  # Set is_llm_task=True to bypass tool_name requirement
            **kwargs
        )
        self.operation = operation


# =============================================
# 2. Define the execution strategy
# =============================================

class SimpleDataStrategy(TaskExecutionStrategy):
    """Strategy for executing simple data tasks."""  # noqa: D202
    
    async def execute(self, task: Task, **kwargs) -> Dict[str, Any]:
        """Execute a simple data task."""
        logger.info(f"Executing simple data task: {task.id}")
        processed_input = kwargs.get("processed_input", {})
        
        # Get the input text
        text = processed_input.get("text", "")
        if not text:
            return {"success": False, "error": "No text provided"}
        
        # Get the operation
        operation = getattr(task, "operation", None)
        if not operation:
            return {"success": False, "error": "No operation specified"}
        
        # Perform the operation
        try:
            if operation == "uppercase":
                result = text.upper()
            elif operation == "lowercase":
                result = text.lower()
            elif operation == "double":
                result = text + text
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
                
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": f"Operation error: {str(e)}"}


# =============================================
# 3. Define a direct handler function
# =============================================

def provide_input_text(task, input_data):
    """Direct handler function to provide input text."""
    text = input_data.get("text", "Hello, World!")
    logger.info(f"Providing input text: {text}")
    return {"success": True, "result": text}


# =============================================
# 4. Main function
# =============================================

def main():
    """Run the example workflow with custom task types"""
    logger.info("Starting Simple Custom Task Example")
    
    # Get services
    services = get_services()
    llm_interface = LLMInterface()
    tool_registry = services.tool_registry
    
    # Create a simple workflow
    workflow = Workflow(
        workflow_id="simple_data_workflow",
        name="Simple Data Workflow"
    )
    
    # Add a DirectHandlerTask to provide input (no tool needed)
    task1 = DirectHandlerTask(
        task_id="task_input",
        name="Provide Input Text",
        handler=provide_input_text,
        input_data={"text": "Hello, World!"}
    )
    workflow.add_task(task1)
    
    # Add a custom task
    task2 = SimpleDataTask(
        task_id="task_uppercase",
        name="Convert Text to Uppercase",
        operation="uppercase",
        input_data={"text": "${task_input.output_data.result}"}
    )
    workflow.add_task(task2)
    
    # Create our own engine
    logger.info("Creating workflow engine")
    engine = WorkflowEngine(
        workflow=workflow,
        llm_interface=llm_interface,
        tool_registry=tool_registry
    )
    
    # Register our custom task strategy
    logger.info("Registering custom strategy")
    engine.strategy_factory.register_strategy("simple_data", SimpleDataStrategy())
    
    # Run the workflow
    logger.info("Running workflow")
    result = engine.run()
    
    # Print results
    logger.info(f"Workflow status: {result.get('status')}")
    for task_id, task in workflow.tasks.items():
        logger.info(f"Task: {task.name} (ID: {task_id})")
        logger.info(f"  Status: {task.status}")
        logger.info(f"  Output: {task.output_data}")
    
    logger.info("Example completed")
    return result


if __name__ == "__main__":
    main() 