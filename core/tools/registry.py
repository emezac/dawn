
from typing import Dict, Any, Callable, Optional

from tools.web_search_tool import WebSearchTool
from tools.file_read_tool import FileReadTool
from tools.file_upload_tool import FileUploadTool
from tools.vector_store_tool import VectorStoreTool
from tools.write_markdown_tool import WriteMarkdownTool

from openai import APIError, APIConnectionError, RateLimitError, BadRequestError

# Optional: Define a custom exception for tool failures
class ToolExecutionError(Exception):
    """Custom exception for errors during tool execution."""
    pass

class ToolRegistry:
    """
    Registry for tools that can be used by the agent.
    Initializes and provides access to tool handler methods.
    """
    def __init__(self):
        """
        Initialize the tool registry and register the default tool handlers.
        """
        self.tools: Dict[str, Callable] = {}
        self.register_tool("web_search", self.web_search_tool_handler)
        self.register_tool("file_read", self.file_read_tool_handler)
        self.register_tool("file_upload", self.file_upload_tool_handler)
        self.register_tool("vector_store_create", self.vector_store_create_tool_handler)
        self.register_tool("write_markdown", self.write_markdown_tool_handler)

    def register_tool(self, name: str, func: Callable) -> None:
        """
        Register a tool function with the registry.

        Args:
            name: The unique name to identify the tool.
            func: The callable function or method that executes the tool's logic.

        Raises:
            ValueError: If a tool with the same name is already registered.
        """
        if name in self.tools:
            # Keep the error for potentially overwriting tools unintentionally
            raise ValueError(f"Tool with name '{name}' already registered.")
        self.tools[name] = func

    def get_tool(self, name: str) -> Optional[Callable]:
        """
        Retrieve a tool function by its registered name.

        Args:
            name: The name of the tool to retrieve.

        Returns:
            The callable tool function if found, otherwise None.
        """
        return self.tools.get(name)

    def execute_tool(self, name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a registered tool using the provided input data.
        Catches exceptions raised by the tool handler.

        Args:
            name: The name of the tool to execute.
            data: A dictionary containing the input data required by the tool.

        Returns:
            A dictionary containing the execution result:
            {'success': True, 'result': Any} or
            {'success': False, 'error': str, 'error_type': str}
        """
        tool_func = self.get_tool(name)
        if not tool_func:
            return {
                "success": False,
                "result": None,
                "error": f"Tool '{name}' not found in registry",
                "error_type": "ToolNotFound"
            }
        try:
            # Execute the handler. Assume it returns raw data on success
            # AND raises an appropriate Exception on failure.
            result_data = tool_func(**data)
            return {
                "success": True,
                "result": result_data,
                "error": None,
                "error_type": None
            }
        except (APIConnectionError, RateLimitError) as recoverable_api_e:
            # Log specific details if needed
            # logger.warning(f"Recoverable API Error executing tool '{name}': {recoverable_api_e}")
            return {
                "success": False, "result": None,
                "error": f"API Error (Recoverable?): {str(recoverable_api_e)}",
                "error_type": type(recoverable_api_e).__name__
            }
        # --- Catch common configuration or usage errors ---
        except (ValueError, TypeError, KeyError, FileNotFoundError, BadRequestError) as config_usage_e:
            # Log specific details if needed
            # logger.error(f"Configuration/Usage Error executing tool '{name}': {config_usage_e}", exc_info=True)
            return {
                "success": False, "result": None,
                "error": f"Tool Usage/Config Error: {str(config_usage_e)}",
                "error_type": type(config_usage_e).__name__
            }
        # --- Catch other OpenAI API errors ---
        except APIError as api_e:
            # logger.error(f"OpenAI API Error executing tool '{name}': {api_e}", exc_info=True)
            return {
                "success": False, "result": None,
                "error": f"API Error: {str(api_e)}",
                "error_type": type(api_e).__name__
            }
        # --- Catch our custom tool error ---
        except ToolExecutionError as tool_e:
             # logger.error(f"Tool Execution Error for tool '{name}': {tool_e}", exc_info=True)
            return {
                "success": False, "result": None,
                "error": str(tool_e),
                "error_type": type(tool_e).__name__
            }
        # --- Catch any other unexpected exceptions ---
        except Exception as e:
            # Log unexpected errors with traceback
            # logger.exception(f"Unexpected Error executing tool '{name}': {e}") # Use logger.exception
            return {
                "success": False, "result": None,
                "error": f"Unexpected Error: {str(e)}",
                "error_type": type(e).__name__
            }

    # --- Tool Handler Methods ---
    # Handlers now simply call the underlying tool method and return its result.
    # They rely on the tool method OR the execute_tool wrapper to handle exceptions.

    def web_search_tool_handler(self, **data) -> Any:
        """Handler for the Web Search tool."""
        # Optional: Add input validation here if needed
        web_search_tool = WebSearchTool()
        query = data.get("query", "")
        if not query: raise ValueError("Missing 'query' for web search.")
        context_size = data.get("context_size", "medium")
        user_location = data.get("user_location", None)
        # Let perform_search raise exceptions on API failure directly to execute_tool
        return web_search_tool.perform_search(query, context_size, user_location)

    def file_read_tool_handler(self, **data) -> Any:
        """Handler for the File Read (RAG) tool."""
        # Optional: Add input validation here if needed
        file_read_tool = FileReadTool()
        vector_store_ids = data.get("vector_store_ids", [])
        query = data.get("query", "")
        if not vector_store_ids: raise ValueError("Missing 'vector_store_ids' for file read.")
        if not query: raise ValueError("Missing 'query' for file read.")
        max_num_results = data.get("max_num_results", 5)
        include_search_results = data.get("include_search_results", False)
        # Let perform_file_read raise exceptions directly to execute_tool
        return file_read_tool.perform_file_read(vector_store_ids, query, max_num_results, include_search_results)


    def file_upload_tool_handler(self, **data) -> Any:
        """Handler for the File Upload tool."""
        file_upload_tool = FileUploadTool()
        file_path = data.get("file_path", "")
        purpose = data.get("purpose", "assistants")
        if not file_path: raise ValueError("Missing 'file_path' for file upload.")
        # Let upload_file raise exceptions directly to execute_tool
        file_id = file_upload_tool.upload_file(file_path, purpose)
        # Optional: Basic validation on the returned ID format
        if not file_id or not isinstance(file_id, str) or not file_id.startswith("file-"):
             # If validation fails *after* a successful API call (unlikely here but possible), raise our custom error
             raise ToolExecutionError(f"Invalid file ID format received from upload: {file_id}")
        return file_id

    def vector_store_create_tool_handler(self, **data) -> Any:
        """Handler for the Vector Store Create tool."""
        vector_store_tool = VectorStoreTool()
        name = data.get("name", "Default Vector Store")
        file_ids = data.get("file_ids", [])
        if not file_ids or not isinstance(file_ids, list):
             raise ValueError("Missing or invalid 'file_ids' list for vector store creation.")
        # Let create_vector_store raise exceptions directly to execute_tool
        vs_id = vector_store_tool.create_vector_store(name, file_ids)
        # Optional: Basic validation on the returned ID format
        if not vs_id or not isinstance(vs_id, str) or not vs_id.startswith("vs_"):
             raise ToolExecutionError(f"Invalid vector store ID format received: {vs_id}")
        return vs_id

    def write_markdown_tool_handler(self, **data) -> Any:
        """Handler for the Write Markdown File tool."""
        write_tool = WriteMarkdownTool()
        file_path = data.get("file_path", "")
        content = data.get("content", "") # Allow empty content? Add check if needed.
        if not file_path: raise ValueError("Missing 'file_path' for writing markdown.")
        # Let write_markdown_file raise exceptions (e.g., PermissionError) directly to execute_tool
        result_path = write_tool.write_markdown_file(file_path, content)
        # Optional: Validate if path exists after writing?
        return result_path