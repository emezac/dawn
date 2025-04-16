"""
Tool registry for Dawn framework.

This module defines the ToolRegistry class that manages tool registration,
discovery, and execution in the Dawn framework.
"""

import inspect
import logging
from typing import Any, Callable, Dict, List, Optional, Set, TypeVar, cast

from core.errors import ErrorCode, ToolExecutionError, create_error_response
from core.tools.plugin_manager import PluginManager
from core.tools.response_format import format_tool_response

# Avoid circular imports by delaying these imports
from tools.file_read_tool import FileReadTool
from tools.file_upload_tool import FileUploadTool
from tools.openai_vs.create_vector_store import CreateVectorStoreTool
from tools.web_search_tool import WebSearchTool
from tools.write_markdown_tool import WriteMarkdownTool

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Registry for tools that can be used by the agent.
    Initializes and provides access to tool handler methods.
    """  # noqa: D202

    def __init__(self):
        """
        Initialize the tool registry and register the default tool handlers.
        """
        self.tools: Dict[str, Callable] = {}
        
        # Initialize plugin manager
        self.plugin_manager = PluginManager()
        self.plugin_namespaces: Set[str] = set()
        
        # Register legacy tools for backward compatibility
        self.register_tool("web_search", self.web_search_tool_handler)
        self.register_tool("file_read", self.file_read_tool_handler)
        self.register_tool("file_upload", self.file_upload_tool_handler)
        self.register_tool("create_vector_store", self.create_vector_store_handler)
        self.register_tool("upload_file_to_vector_store", self.upload_file_to_vector_store_tool_handler)
        self.register_tool("save_to_ltm", self.save_to_ltm_tool_handler)
        self.register_tool("list_vector_stores", self.list_vector_stores_tool_handler)
        self.register_tool("delete_vector_store", self.delete_vector_store_tool_handler)
        self.register_tool("write_markdown", self.write_markdown_tool_handler)
        # Register vector_store_create as an alias to maintain backward compatibility
        self.register_tool("vector_store_create", self.create_vector_store_handler)

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

    def register_plugin_namespace(self, namespace: str) -> None:
        """
        Register a namespace (package) where tool plugins can be found.
        
        Args:
            namespace: The package namespace to register
        """
        if namespace not in self.plugin_namespaces:
            self.plugin_namespaces.add(namespace)
            self.plugin_manager.register_plugin_namespace(namespace)
    
    def load_plugins(self, reload: bool = False) -> None:
        """
        Load all plugins from registered namespaces and register them as tools.
        
        Args:
            reload: Whether to reload already loaded plugins
        """
        # Load plugins through the plugin manager
        self.plugin_manager.load_plugins(reload)
        
        # Register all plugins as tools
        for name, plugin in self.plugin_manager.get_all_plugins().items():
            if name not in self.tools or reload:
                # Create a wrapper function to call the plugin's execute method
                def plugin_wrapper(plugin_instance=plugin, **kwargs):
                    # Validate parameters before executing
                    validated_params = plugin_instance.validate_parameters(**kwargs)
                    return plugin_instance.execute(**validated_params)
                
                try:
                    self.register_tool(name, plugin_wrapper)
                except ValueError:
                    # Skip if the tool is already registered
                    pass
    
    def get_tool(self, name: str) -> Optional[Callable]:
        """
        Retrieve a tool function by its registered name.

        Args:
            name: The name of the tool to retrieve.

        Returns:
            The callable tool function if found, otherwise None.
        """
        return self.tools.get(name)

    def tool_exists(self, name: str) -> bool:
        """
        Check if a tool with the given name exists in the registry.

        Args:
            name: The name of the tool to check.

        Returns:
            True if the tool exists, False otherwise.
        """
        return name in self.tools

    def execute_tool(self, name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a registered tool using the provided input data.
        Catches exceptions raised by the tool handler and ensures
        the response follows the standardized format.

        Args:
            name: The name of the tool to execute.
            data: A dictionary containing the input data required by the tool.

        Returns:
            A standardized response dictionary containing the execution result.
        """
        tool_func = self.get_tool(name)
        if not tool_func:
            return create_error_response(
                error_code=ErrorCode.RESOURCE_NOT_FOUND,
                resource_type="tool",
                resource_id=name
            )
            
        try:
            # Check if input_data needs to be passed as kwargs or a single argument
            sig = inspect.signature(tool_func)
            
            # Check if the function accepts **kwargs
            has_var_kwargs = any(
                param.kind == inspect.Parameter.VAR_KEYWORD
                for param in sig.parameters.values()
            )
            
            # If the function has no parameters, call it without arguments
            if len(sig.parameters) == 0:
                result = tool_func()
            # If the function accepts **kwargs, pass data as kwargs
            elif has_var_kwargs:
                result = tool_func(**data)
            # If the function has a single parameter, pass data as a single argument
            elif len(sig.parameters) == 1:
                # This supports the common pattern of func(input_data)
                result = tool_func(data)
            else:
                # Otherwise, unpack data as keyword arguments
                # This supports the pattern of func(param1=value1, param2=value2)
                result = tool_func(**data)
                
            # Ensure the result follows the standardized format
            return format_tool_response(result)
                
        # --- Catch our custom tool error ---
        except ToolExecutionError as tool_e:
            return create_error_response(
                error_code=ErrorCode.EXECUTION_TOOL_FAILED,
                tool_name=name,
                reason=str(tool_e)
            )
        # --- Catch any other unexpected exceptions ---
        except Exception as e:
            logger.exception(f"Unexpected Error executing tool '{name}': {e}")
            return create_error_response(
                error_code=ErrorCode.EXECUTION_TOOL_FAILED,
                tool_name=name,
                reason=str(e)
            )
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get metadata about all available tools, both legacy and plugin-based.
        
        Returns:
            List of dictionaries containing tool metadata
        """
        tool_metadata = []
        
        # Get plugin metadata
        plugin_metadata = self.plugin_manager.get_plugin_metadata()
        tool_metadata.extend(plugin_metadata)
        
        # Add legacy tools (tools not from plugins)
        plugin_tool_names = {m["name"] for m in plugin_metadata}
        plugin_tool_aliases = {alias for m in plugin_metadata for alias in m.get("aliases", [])}
        
        for name, func in self.tools.items():
            # Skip plugin tools that are already included
            if name in plugin_tool_names or name in plugin_tool_aliases:
                continue
                
            # Create basic metadata for legacy tools
            tool_metadata.append({
                "name": name,
                "aliases": [],
                "description": func.__doc__ or "No description available",
                "version": "legacy",
                "is_legacy": True
            })
        
        return tool_metadata

    # --- Legacy Tool Handler Methods ---
    # These methods are kept for backward compatibility

    def web_search_tool_handler(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler for the Web Search tool."""
        try:
            web_search_tool = WebSearchTool()
            query = input_data.get("query", "")
            if not query:
                return create_error_response(
                    error_code=ErrorCode.VALIDATION_MISSING_FIELD,
                    field_name="query"
                )
                
            context_size = input_data.get("context_size", "medium")
            user_location = input_data.get("user_location", None)
            
            result = web_search_tool.perform_search(query, context_size, user_location)
            return format_tool_response(result)
        except Exception as e:
            return create_error_response(
                error_code=ErrorCode.EXECUTION_TOOL_FAILED,
                tool_name="web_search",
                reason=str(e)
            )

    def file_read_tool_handler(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler for the File Read (RAG) tool."""
        try:
            file_read_tool = FileReadTool()
            
            vector_store_ids = input_data.get("vector_store_ids", [])
            if not vector_store_ids:
                return create_error_response(
                    error_code=ErrorCode.VALIDATION_MISSING_FIELD,
                    field_name="vector_store_ids"
                )
                
            query = input_data.get("query", "")
            if not query:
                return create_error_response(
                    error_code=ErrorCode.VALIDATION_MISSING_FIELD,
                    field_name="query"
                )
                
            max_num_results = input_data.get("max_num_results", 5)
            include_search_results = input_data.get("include_search_results", False)
            
            result = file_read_tool.perform_file_read(
                vector_store_ids, query, max_num_results, include_search_results
            )
            return format_tool_response(result)
        except Exception as e:
            return create_error_response(
                error_code=ErrorCode.EXECUTION_TOOL_FAILED,
                tool_name="file_read",
                reason=str(e)
            )

    def file_upload_tool_handler(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler for the File Upload tool."""
        try:
            from tools.file_upload_tool import FileUploadTool
            
            file_upload_tool = FileUploadTool()
            file_path = input_data.get("file_path", "")
            
            if not file_path:
                return create_error_response(
                    error_code=ErrorCode.VALIDATION_MISSING_FIELD,
                    field_name="file_path"
                )
                
            purpose = input_data.get("purpose", "assistants")
            
            file_id = file_upload_tool.upload_file(file_path, purpose)
            
            # Optional: Basic validation on the returned ID format
            if not file_id or not isinstance(file_id, str) or not file_id.startswith("file-"):
                return create_error_response(
                    error_code=ErrorCode.VALIDATION_INVALID_FORMAT,
                    field_name="file_id",
                    reason="must start with 'file-'",
                    received_value=file_id
                )
                
            return format_tool_response(file_id)
        except Exception as e:
            return create_error_response(
                error_code=ErrorCode.EXECUTION_TOOL_FAILED,
                tool_name="file_upload",
                reason=str(e)
            )

    def create_vector_store_handler(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler for creating a vector store."""
        try:
            from tools.openai_vs.create_vector_store import CreateVectorStoreTool
            
            create_tool = CreateVectorStoreTool()
            name = input_data.get("name", "")
            
            if not name:
                return create_error_response(
                    message="Missing 'name' parameter for vector store creation",
                    error_code=ErrorCode.VALIDATION_MISSING_FIELD,
                    details={"field_name": "name"}
                )
                
            file_ids = input_data.get("file_ids", [])
            
            result = create_tool.create_vector_store(name, file_ids)
            return format_tool_response(result)
        except Exception as e:
            return create_error_response(
                message=f"Vector store creation failed: {str(e)}",
                error_code=ErrorCode.EXECUTION_TOOL_FAILED, 
                details={"error_type": type(e).__name__}
            )

    def write_markdown_tool_handler(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handler for the write_markdown tool.
        
        Args:
            input_data (dict): Input data containing:
                - file_path: str, path where the markdown file should be written
                - content: str, markdown content to write
                
        Returns:
            dict: Response containing:
                - success: bool indicating if the operation was successful
                - result: dict containing the file path and metadata on success
                - error: str containing error message on failure
        """
        try:
            # Extract parameters
            file_path = input_data.get("file_path")
            content = input_data.get("content")
            
            if not file_path or not content:
                return {
                    "success": False,
                    "result": None,
                    "error": "Missing required parameters: file_path and content"
                }
            
            # Create tool instance and execute
            tool = WriteMarkdownTool()
            response = tool.write_markdown_file(file_path, content)
            
            # Ensure response is properly formatted
            if not isinstance(response, dict):
                return {
                    "success": False,
                    "result": None,
                    "error": "Invalid response format from write_markdown tool"
                }
                
            return response
            
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "error": str(e)
            }

    def upload_file_to_vector_store_tool_handler(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler for the Upload File to Vector Store tool."""
        try:
            from tools.openai_vs.upload_file_to_vector_store import UploadFileToVectorStoreTool

            upload_tool = UploadFileToVectorStoreTool()
            
            vector_store_id = input_data.get("vector_store_id", "")
            if not vector_store_id:
                return create_error_response(
                    message="Missing 'vector_store_id' for file upload to vector store",
                    error_code=ErrorCode.VALIDATION_MISSING_FIELD,
                    details={"field_name": "vector_store_id"}
                )
                
            file_path = input_data.get("file_path", "")
            if not file_path:
                return create_error_response(
                    message="Missing 'file_path' for file upload to vector store",
                    error_code=ErrorCode.VALIDATION_MISSING_FIELD,
                    details={"field_name": "file_path"}
                )
                
            purpose = input_data.get("purpose", "assistants")

            # Validate purpose parameter
            valid_purposes = ["assistants", "fine-tune", "batch", "user_data", "vision", "evals"]
            if purpose not in valid_purposes:
                return create_error_response(
                    message=f"Invalid purpose: '{purpose}'. Must be one of: {', '.join(valid_purposes)}",
                    error_code=ErrorCode.VALIDATION_INVALID_VALUE,
                    details={
                        "field_name": "purpose",
                        "received_value": purpose,
                        "allowed_values": valid_purposes
                    }
                )

            result = upload_tool.upload_and_add_file_to_vector_store(
                vector_store_id, file_path, purpose=purpose
            )
            return format_tool_response(result)
        except Exception as e:
            return create_error_response(
                message=f"File upload to vector store failed: {str(e)}",
                error_code=ErrorCode.EXECUTION_TOOL_FAILED,
                details={"error_type": type(e).__name__}
            )

    def save_to_ltm_tool_handler(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler for the Save to LTM tool."""
        try:
            from tools.openai_vs.save_to_ltm import SaveToLTMTool

            save_tool = SaveToLTMTool()
            
            vector_store_id = input_data.get("vector_store_id", "")
            if not vector_store_id:
                return create_error_response(
                    message="Missing 'vector_store_id' for saving to LTM",
                    error_code=ErrorCode.VALIDATION_MISSING_FIELD,
                    details={"field_name": "vector_store_id"}
                )
                
            text = input_data.get("text", "")
            if not text:
                return create_error_response(
                    message="Missing 'text' for saving to LTM",
                    error_code=ErrorCode.VALIDATION_MISSING_FIELD,
                    details={"field_name": "text"}
                )

            # Validate vector_store_id format
            if not vector_store_id.startswith("vs_"):
                return create_error_response(
                    message=f"Invalid vector_store_id format: '{vector_store_id}'. Must start with 'vs_'",
                    error_code=ErrorCode.VALIDATION_INVALID_FORMAT,
                    details={
                        "field_name": "vector_store_id",
                        "received_value": vector_store_id
                    }
                )

            result = save_tool.save_text_to_vector_store(vector_store_id, text)
            return format_tool_response(result)
        except Exception as e:
            return create_error_response(
                message=f"Saving to LTM failed: {str(e)}",
                error_code=ErrorCode.EXECUTION_TOOL_FAILED,
                details={"error_type": type(e).__name__}
            )

    def list_vector_stores_tool_handler(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler for the List Vector Stores tool."""
        try:
            from tools.openai_vs.list_vector_stores import ListVectorStoresTool

            list_tool = ListVectorStoresTool()
            result = list_tool.list_vector_stores()
            return format_tool_response(result)
        except Exception as e:
            return create_error_response(
                message=f"Listing vector stores failed: {str(e)}",
                error_code=ErrorCode.EXECUTION_TOOL_FAILED,
                details={"error_type": type(e).__name__}
            )

    def delete_vector_store_tool_handler(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler for the Delete Vector Store tool."""
        try:
            from tools.openai_vs.delete_vector_store import DeleteVectorStoreTool

            delete_tool = DeleteVectorStoreTool()
            
            vector_store_id = input_data.get("vector_store_id", "")
            if not vector_store_id:
                return create_error_response(
                    message="Missing 'vector_store_id' for deleting vector store",
                    error_code=ErrorCode.VALIDATION_MISSING_FIELD,
                    details={"field_name": "vector_store_id"}
                )

            # Validate vector_store_id format
            if not vector_store_id.startswith("vs_"):
                return create_error_response(
                    message=f"Invalid vector_store_id format: '{vector_store_id}'. Must start with 'vs_'",
                    error_code=ErrorCode.VALIDATION_INVALID_FORMAT,
                    details={
                        "field_name": "vector_store_id",
                        "received_value": vector_store_id
                    }
                )

            result = delete_tool.delete_vector_store(vector_store_id)
            return format_tool_response(result)
        except Exception as e:
            return create_error_response(
                message=f"Deleting vector store failed: {str(e)}",
                error_code=ErrorCode.EXECUTION_TOOL_FAILED,
                details={"error_type": type(e).__name__}
            )
