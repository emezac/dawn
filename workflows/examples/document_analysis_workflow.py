"""
Example document analysis workflow for testing demonstration.

This workflow reads a document, extracts entities, and generates a summary.
It includes error handling for common failure cases.
"""

from typing import Dict, Any, List
from core.workflow import Workflow
from core.task import Task
from core.utils.testing import TaskStatus
from tasks.examples.extract_entities_task import ExtractEntitiesTask
from tasks.examples.summarize_document_task import SummarizeDocumentTask
import types


class ReadDocumentTask(Task):
    """Task to read a document from the file system."""  # noqa: D202
    
    def __init__(self):
        """Initialize the task."""
        super().__init__(
            task_id="read_document", 
            name="Read Document Task",
            tool_name="file_system"
        )
    
    def execute(self, context):
        """Execute the task."""
        # Get document path from context
        document_path = context.variables.get("document_path")
        if not document_path:
            raise ValueError("Document path is required")
            
        try:
            # Execute file system tool to read the document
            result = self.tool_registry.execute_tool(
                "file_system",
                {
                    "path": document_path,
                    "operation": "read"
                }
            )
            
            # Store document content in context
            context.variables["document_content"] = result["content"]
            
            return {"document_content": result["content"]}
        except FileNotFoundError as e:
            # Re-raise with the original exception to preserve the stack trace
            raise FileNotFoundError(f"File not found: {document_path}") from e


class HandleFileNotFoundTask(Task):
    """Task to handle file not found errors."""  # noqa: D202
    
    def __init__(self):
        """Initialize the task."""
        super().__init__(
            task_id="handle_file_not_found", 
            name="Handle File Not Found Task",
            tool_name="error_handler"
        )
    
    def execute(self, context):
        """Execute the task."""
        document_path = context.variables.get("document_path", "Unknown file")
        
        # Set error message
        error_message = f"The document '{document_path}' could not be found. Please check the file path and try again."
        context.variables["error_message"] = error_message
        
        return {"error_message": error_message}


class HandleLLMErrorTask(Task):
    """Task to handle LLM API errors."""  # noqa: D202
    
    def __init__(self):
        """Initialize the task."""
        super().__init__(
            task_id="handle_llm_error", 
            name="Handle LLM Error Task",
            tool_name="error_handler"
        )
    
    def execute(self, context):
        """Execute the task."""
        # Get error information from exception context if available
        error_type = context.variables.get("error_type", "Unknown error")
        error_message = context.variables.get("error_message", "An error occurred while processing the document")
        
        # Create a user-friendly error message
        user_message = f"Sorry, we encountered an issue while analyzing the document: {error_message}"
        context.variables["error_message"] = user_message
        
        return {"error_message": user_message}


class DocumentAnalysisWorkflow(Workflow):
    """
    Workflow for analyzing documents.
    
    This workflow:
    1. Reads a document from the file system
    2. Extracts entities from the document
    3. Generates a summary of the document
    
    It includes error handling for common failure cases.
    """  # noqa: D202
    
    def __init__(self):
        """Initialize the workflow."""
        super().__init__(workflow_id="document_analysis_workflow", name="Document Analysis Workflow")
        self.tasks = {
            "read_document": ReadDocumentTask(),
            "extract_entities": ExtractEntitiesTask(),
            "summarize_document": SummarizeDocumentTask(),
            "handle_file_not_found": HandleFileNotFoundTask(),
            "handle_llm_error": HandleLLMErrorTask()
        }
        self.tool_registry = None  # Will be set later with set_tool_registry
    
    def set_tool_registry(self, registry):
        """Set the tool registry for the workflow and all its tasks."""
        self.tool_registry = registry
        for task in self.tasks.values():
            task.tool_registry = registry
    
    def get_next_task(self, context):
        """
        Determine the next task to execute based on the current state.
        
        Args:
            context: The execution context
            
        Returns:
            The ID of the next task to execute, or None if the workflow is complete
        """
        # Check if any tasks have been executed
        if not context.task_data:
            # Start with reading the document
            return "read_document"
        
        # Check for errors in the last task
        last_task_id = context.get_last_executed_task()
        if last_task_id:
            last_task_status = context.get_task_status(last_task_id)
            if last_task_status == TaskStatus.FAILED:
                error = context.get_task_error(last_task_id)
                
                # Handle specific error types
                if isinstance(error, FileNotFoundError):
                    context.variables["error_type"] = "FileNotFoundError"
                    context.variables["error_message"] = str(error)
                    return "handle_file_not_found"
                elif last_task_id in ["extract_entities", "summarize_document"]:
                    context.variables["error_type"] = "LLMError"
                    context.variables["error_message"] = str(error)
                    return "handle_llm_error"
        
        # Normal workflow progression
        if context.is_task_completed("read_document") and not context.is_task_executed("extract_entities"):
            return "extract_entities"
        
        if context.is_task_completed("extract_entities") and not context.is_task_executed("summarize_document"):
            return "summarize_document"
        
        # Workflow is complete if we reach here
        return None 

    def execute(self, context):
        """
        Execute the workflow with the given context.
        
        Args:
            context: Dictionary or ExecutionContext with variables for the workflow
            
        Returns:
            Dictionary with execution results
        """
        if not hasattr(context, 'variables'):
            # If context is a dict, convert it to a simple ExecutionContext
            from core.utils.testing import ExecutionContext
            context = ExecutionContext(variables=context)
        
        # Add missing methods if using the simple ExecutionContext from testing
        if not hasattr(context, 'get_last_executed_task'):
            def get_last_executed_task(self):
                """Get the ID of the last executed task."""
                if not self.task_data:
                    return None
                return list(self.task_data.keys())[-1]
            context.get_last_executed_task = types.MethodType(get_last_executed_task, context)
        
        if not hasattr(context, 'get_task_status'):
            def get_task_status(self, task_id):
                """Get the status of a task."""
                if task_id not in self.task_data:
                    return TaskStatus.PENDING
                return TaskStatus.COMPLETED if self.task_data[task_id].get('status') == 'completed' else TaskStatus.FAILED
            context.get_task_status = types.MethodType(get_task_status, context)
        
        if not hasattr(context, 'get_task_error'):
            def get_task_error(self, task_id):
                """Get the error of a task."""
                if task_id not in self.task_data:
                    return None
                return self.task_data[task_id].get('error')
            context.get_task_error = types.MethodType(get_task_error, context)
        
        if not hasattr(context, 'is_task_completed'):
            def is_task_completed(self, task_id):
                """Check if a task is completed."""
                if task_id not in self.task_data:
                    return False
                return self.task_data[task_id].get('status') == 'completed'
            context.is_task_completed = types.MethodType(is_task_completed, context)
        
        if not hasattr(context, 'is_task_executed'):
            def is_task_executed(self, task_id):
                """Check if a task has been executed."""
                return task_id in self.task_data
            context.is_task_executed = types.MethodType(is_task_executed, context)
        
        # Initialize workflow
        self.status = "running"
        context.task_data = {}
        
        # Execute tasks in sequence based on the get_next_task logic
        current_task_id = self.get_next_task(context)
        while current_task_id:
            # Get the task
            task = self.tasks.get(current_task_id)
            if not task:
                self.set_status("failed")
                return {"success": False, "error": f"Task '{current_task_id}' not found"}
            
            # Execute the task
            print(f"Executing task: {task.id} ({task.__class__.__name__})")
            try:
                task_result = task.execute(context)
                task.status = "completed"
                context.task_data[task.id] = {
                    "status": "completed",
                    "result": task_result
                }
            except Exception as e:
                task.status = "failed"
                context.task_data[task.id] = {
                    "status": "failed",
                    "error": str(e),
                    "error_type": type(e).__name__
                }
                
                # Store the exception for error handling paths
                context.variables["error"] = str(e)
                
                # Move to next task based on error handling logic
                current_task_id = self.get_next_task(context)
                continue
            
            # Get the next task
            current_task_id = self.get_next_task(context)
        
        # Workflow completed
        self.set_status("completed")
        return {"success": True, "context": context.variables} 