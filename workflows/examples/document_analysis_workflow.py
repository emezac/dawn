"""
Example document analysis workflow for testing demonstration.

This workflow reads a document, extracts entities, and generates a summary.
It includes error handling for common failure cases.
"""

from typing import Dict, Any, List
from core.workflow.workflow import Workflow
from core.workflow.task import Task, TaskStatus
from tasks.examples.extract_entities_task import ExtractEntitiesTask
from tasks.examples.summarize_document_task import SummarizeDocumentTask


class ReadDocumentTask(Task):
    """Task to read a document from the file system."""  # noqa: D202
    
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
    
    def execute(self, context):
        """Execute the task."""
        document_path = context.variables.get("document_path", "Unknown file")
        
        # Set error message
        error_message = f"The document '{document_path}' could not be found. Please check the file path and try again."
        context.variables["error_message"] = error_message
        
        return {"error_message": error_message}


class HandleLLMErrorTask(Task):
    """Task to handle LLM API errors."""  # noqa: D202
    
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
        super().__init__()
        self.tasks = {
            "read_document": ReadDocumentTask(),
            "extract_entities": ExtractEntitiesTask(),
            "summarize_document": SummarizeDocumentTask(),
            "handle_file_not_found": HandleFileNotFoundTask(),
            "handle_llm_error": HandleLLMErrorTask()
        }
    
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