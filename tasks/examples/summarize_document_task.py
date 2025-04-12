"""
Example document summarization task for testing demonstration.

This task generates a summary of a document using an LLM.
"""

from typing import Dict, Any
from core.workflow.task import Task


class SummarizeDocumentTask(Task):
    """
    Task that summarizes a document.
    
    This task:
    1. Takes a document content as input
    2. Uses an LLM to generate a summary
    3. Returns the summary
    """  # noqa: D202
    
    def execute(self, context):
        """
        Execute the task.
        
        Args:
            context: The execution context
            
        Returns:
            Dict containing the summary
            
        Raises:
            ValueError: If document_content is not provided
        """
        # Get document content from context
        document_content = context.variables.get("document_content")
        if not document_content:
            raise ValueError("document_content is required for summarization")
        
        # Get summary prompt, or use default if not provided
        summary_prompt = context.variables.get(
            "summary_prompt",
            "Please provide a concise summary of the following document:"
        )
        
        # Build the complete prompt
        prompt = f"{summary_prompt}\n\n{document_content}"
        
        # Execute LLM tool to generate summary
        result = self.tool_registry.execute_tool(
            "openai",
            {
                "prompt": prompt,
                "temperature": 0.3,
                "max_tokens": 200
            }
        )
        
        # Store summary in context
        summary = result["content"]
        context.variables["summary"] = summary
        
        return {"summary": summary} 