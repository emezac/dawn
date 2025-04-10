"""
Module for updating the ToolRegistry with the new OpenAI Vector Store tools.
"""
from tools.openai_vs.create_vector_store import CreateVectorStoreTool


def register_openai_vs_tools(registry):
    """
    Register OpenAI Vector Store tools with the provided registry.

    Args:
        registry: The ToolRegistry instance to register the tools with.
    """
    registry.register_tool("create_vector_store", create_vector_store_handler)


def create_vector_store_handler(**data):
    """
    Handler for the create_vector_store tool.

    Args:
        **data: Keyword arguments containing the tool parameters.

    Returns:
        str: The ID of the created Vector Store.

    Raises:
        ValueError: If the name parameter is missing or invalid.
    """
    tool = CreateVectorStoreTool()
    name = data.get("name", "")

    if not name:
        raise ValueError("Missing 'name' parameter for vector store creation.")

    return tool.create_vector_store(name)
