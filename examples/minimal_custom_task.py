"""
Minimal Custom Task Type Example

This is a minimal example demonstrating custom task types with proper error handling.
"""

import os
import sys
import logging
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from core.task import CustomTask, Task, DirectHandlerTask
from core.task_execution_strategy import TaskExecutionStrategy
from core.workflow import Workflow
from core.engine import WorkflowEngine
from core.llm.interface import LLMInterface
from core.services import get_services

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define a custom task type
class TextProcessingTask(CustomTask):
    """A simple custom task for text processing."""  # noqa: D202
    
    def __init__(
        self,
        task_id: str,
        name: str,
        operation: str,  # Operation to perform (uppercase, reverse, etc.)
        input_data: Dict[str, Any] = None,
        **kwargs
    ):
        super().__init__(
            task_id=task_id,
            name=name,
            task_type="text_processor",  # Custom task type identifier
            input_data=input_data,
            is_llm_task=True,  # Set is_llm_task=True to bypass tool_name requirement
            **kwargs
        )
        self.operation = operation

# Define a strategy for the custom task type
class TextProcessingStrategy(TaskExecutionStrategy):
    """Strategy for executing text processing tasks."""  # noqa: D202
    
    async def execute(self, task, **kwargs):
        """Execute a text processing task."""
        logger.info(f"Executing text processing task: {task.id}")
        
        # Get processed input
        processed_input = kwargs.get("processed_input", {})
        text = processed_input.get("text", "")
        
        if not text:
            return {"success": False, "error": "No text provided"}
            
        # Get operation
        operation = getattr(task, "operation", "")
        
        try:
            # Process text based on operation
            if operation == "uppercase":
                result = text.upper()
            elif operation == "lowercase":
                result = text.lower()
            elif operation == "reverse":
                result = text[::-1]
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
                
            logger.info(f"Text processing result: {result}")
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Text processing error: {str(e)}")
            return {"success": False, "error": f"Processing error: {str(e)}"}

def provide_input(task, input_data):
    """Direct handler function to provide input text."""
    text = input_data.get("text", "Hello, World!")
    logger.info(f"Providing input text: {text}")
    return {"success": True, "result": text}

def main():
    """Run the minimal custom task example."""
    logger.info("Starting Minimal Custom Task Example")
    
    # Get services
    services = get_services()
    llm_interface = LLMInterface()
    tool_registry = services.tool_registry
    
    # Create workflow
    workflow = Workflow(
        workflow_id="text_processor_workflow",
        name="Text Processor Workflow"
    )
    
    # Add input task using DirectHandlerTask (no tool required)
    task1 = DirectHandlerTask(
        task_id="provide_input",
        name="Provide Input Text",
        handler=provide_input,
        input_data={"text": "This is a test string."}
    )
    workflow.add_task(task1)
    
    # Add custom text processing task
    task2 = TextProcessingTask(
        task_id="process_text",
        name="Process Text",
        operation="uppercase",
        input_data={"text": "${provide_input.output_data.result}"}
    )
    workflow.add_task(task2)
    
    # Create workflow engine
    logger.info("Creating workflow engine")
    engine = WorkflowEngine(
        workflow=workflow,
        llm_interface=llm_interface,
        tool_registry=tool_registry
    )
    
    # Register the custom strategy
    logger.info("Registering custom strategy")
    engine.strategy_factory.register_strategy("text_processor", TextProcessingStrategy())
    
    # Run the workflow
    logger.info("Running workflow")
    result = engine.run()
    
    # Display results
    logger.info(f"Workflow status: {result.get('status')}")
    
    for task_id, task in workflow.tasks.items():
        logger.info(f"Task: {task.name} (ID: {task_id})")
        logger.info(f"  Status: {task.status}")
        if task.status == "completed":
            logger.info(f"  Output: {task.output_data}")
        elif task.status == "failed":
            logger.info(f"  Error: {task.output_data.get('error', 'Unknown error')}")
    
    logger.info("Minimal example completed successfully")
    return result

if __name__ == "__main__":
    main() 