"""
Example entity extraction task for testing demonstration.

This task extracts entities from a document using an LLM.
"""

from typing import Dict, Any
from core.workflow.task import Task


class ExtractEntitiesTask(Task):
    """
    Task that extracts entities from a document.
    
    This task:
    1. Takes a document content as input
    2. Uses an LLM to extract entities
    3. Returns the extracted entities
    """  # noqa: D202
    
    def execute(self, context):
        """
        Execute the task.
        
        Args:
            context: The execution context
            
        Returns:
            Dict containing the extracted entities
            
        Raises:
            ValueError: If document_content is not provided
        """
        # Get document content from context
        document_content = context.variables.get("document_content")
        if not document_content:
            raise ValueError("document_content is required for entity extraction")
        
        # Get extraction prompt, or use default if not provided
        extraction_prompt = context.variables.get(
            "extraction_prompt",
            "Please extract all entities (people, organizations, locations) from the following document:"
        )
        
        # Build the complete prompt
        prompt = f"{extraction_prompt}\n\n{document_content}"
        
        # Execute LLM tool to extract entities
        result = self.tool_registry.execute_tool(
            "openai",
            {
                "prompt": prompt,
                "temperature": 0.0,
                "max_tokens": 100
            }
        )
        
        # Store entities in context
        entities = result["content"]
        context.variables["entities"] = entities
        
        return {"entities": entities} 