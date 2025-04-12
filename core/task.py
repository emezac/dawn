from typing import Any, Callable, Dict, List, Optional, TypedDict, Union
import json


class TaskOutput(TypedDict, total=False):
    """Standard structure for task output data."""  # noqa: D202
    
    response: Any  # The main response data
    result: Any    # Alternative name for response data
    error: Optional[str]  # Error message if task failed
    error_type: Optional[str]  # Type of error that occurred
    error_details: Optional[Dict[str, Any]]  # Additional error details
    metadata: Optional[Dict[str, Any]]  # Additional metadata about the execution


class Task:
    """
    Represents a unit of work within a workflow with properties for status tracking,
    input/output data, and execution control like retry logic and conditional branching.
    """  # noqa: D202

    def __init__(
        self,
        task_id: str,
        name: str,
        is_llm_task: bool = False,
        tool_name: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        max_retries: int = 0,
        next_task_id_on_success: Optional[str] = None,
        next_task_id_on_failure: Optional[str] = None,
        condition: Optional[str] = None,
        parallel: bool = False,
        use_file_search: bool = False,
        file_search_vector_store_ids: Optional[List[str]] = None,
        file_search_max_results: int = 5,
        validate_input: bool = False,
        validate_output: bool = False,
    ):
        self.id = task_id
        self.name = name
        self.status = "pending"
        self.input_data = input_data or {}
        self.output_data: TaskOutput = {}
        self.output_annotations = []
        self.is_llm_task = is_llm_task
        self.tool_name = tool_name
        self.retry_count = 0
        self.max_retries = max_retries
        self.next_task_id_on_success = next_task_id_on_success
        self.next_task_id_on_failure = next_task_id_on_failure
        self.condition = condition
        self.parallel = parallel
        self.use_file_search = use_file_search
        self.file_search_vector_store_ids = file_search_vector_store_ids or []
        self.file_search_max_results = file_search_max_results
        self.validate_input = validate_input
        self.validate_output = validate_output
        
        # Error information
        self.error = None
        self.error_details = None

        if not self.is_llm_task and not self.tool_name:
            raise ValueError("Non-LLM tasks must specify a tool_name")

    def set_status(self, status: str) -> None:
        """Set the task status, validating that it's a known status."""
        valid_statuses = ["pending", "running", "completed", "failed", "skipped"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")
        self.status = status

    def increment_retry(self) -> None:
        """Increment the retry counter."""
        self.retry_count += 1

    def can_retry(self) -> bool:
        """Check if the task can be retried based on retry count."""
        return self.retry_count < self.max_retries

    def set_input(self, data: Dict[str, Any]) -> None:
        """Set the input data for the task."""
        self.input_data = data

    def set_output(self, data: Dict[str, Any]) -> None:
        """
        Set the output data for the task with standard format.
        
        Args:
            data: Dictionary containing output data. Should contain either 'response' or 
                 'result' key for successful tasks, or 'error' for failed tasks.
        """
        # Ensure we have a standard structure
        output_data: TaskOutput = {}
        
        # Handle response data
        if "response" in data:
            output_data["response"] = data["response"]
        
        # Handle result data
        if "result" in data:
            output_data["result"] = data["result"]
            if "response" not in output_data:
                output_data["response"] = data["result"]
        
        # Handle error data
        if "error" in data:
            output_data["error"] = data["error"]
            self.error = data["error"]
            
            if "error_type" in data:
                output_data["error_type"] = data["error_type"]
                
            if "error_details" in data:
                output_data["error_details"] = data["error_details"]
                self.error_details = data["error_details"]
        
        # Store any additional data
        for key, value in data.items():
            if key not in output_data and key != "annotations":
                output_data[key] = value
        
        # Extract annotations if present
        self.output_annotations = data.get("annotations", [])
        
        # Store the output data
        self.output_data = output_data
    
    def get_output_value(self, path: Optional[str] = None, default: Any = None) -> Any:
        """
        Get a value from the output data by path.
        
        Args:
            path: Dot notation path to the value (e.g., "result.items[0].name")
                If None, returns the entire output_data
            default: Default value to return if path doesn't exist
            
        Returns:
            The value at the specified path, or default if not found
        """
        if not path:
            # Return the entire output data
            if "response" in self.output_data:
                return self.output_data["response"]
            elif "result" in self.output_data:
                return self.output_data["result"]
            return self.output_data
        
        # Use the path resolver
        from core.utils.variable_resolver import resolve_path
        
        try:
            # Determine which field to use as the root
            # Prefer response, then result, then the entire output_data
            if path.startswith("response.") and "response" in self.output_data:
                root_data = self.output_data["response"]
                sub_path = path[len("response."):]
                return resolve_path(root_data, sub_path)
            elif path.startswith("result.") and "result" in self.output_data:
                root_data = self.output_data["result"]
                sub_path = path[len("result."):]
                return resolve_path(root_data, sub_path)
            elif "response" in self.output_data:
                # Try to resolve directly in the response field
                return resolve_path(self.output_data["response"], path)
            elif "result" in self.output_data:
                # Try to resolve directly in the result field
                return resolve_path(self.output_data["result"], path)
            else:
                # Try to resolve in the entire output_data
                return resolve_path(self.output_data, path)
        except (KeyError, IndexError, ValueError):
            return default

    def to_dict(self) -> Dict[str, Any]:
        """Convert the task to a dictionary representation."""
        return {
            "task_id": self.id,
            "name": self.name,
            "status": self.status,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "is_llm_task": self.is_llm_task,
            "tool_name": self.tool_name,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "next_task_id_on_success": self.next_task_id_on_success,
            "next_task_id_on_failure": self.next_task_id_on_failure,
            "condition": self.condition,
            "parallel": self.parallel,
            "use_file_search": self.use_file_search,
            "file_search_vector_store_ids": self.file_search_vector_store_ids,
            "file_search_max_results": self.file_search_max_results,
            "output_annotations": self.output_annotations,
            "error": self.error,
            "error_details": self.error_details,
            "validate_input": self.validate_input,
            "validate_output": self.validate_output,
        }

    def __repr__(self) -> str:
        return f"Task(id={self.id}, name={self.name}, status={self.status})"

    def set_tool_registry(self, tool_registry):
        """
        Set the tool registry for the task.
        
        Args:
            tool_registry: Tool registry to use for tool executions
        """
        self.tool_registry = tool_registry


class DirectHandlerTask(Task):
    """A task that directly executes a handler function.
    
    DirectHandlerTask supports two modes of operation:
    1. Direct handler function: Pass a Python function directly via the handler parameter
    2. Registry-based handler: Pass a string name via handler_name parameter that will be looked up in HandlerRegistry
    
    At least one of handler or handler_name must be provided. If both are provided,
    the direct handler function takes precedence.
    
    This task type allows for executing arbitrary Python functions without requiring
    them to be registered as tools, making it useful for simple data transformations,
    service calls, or other operations that don't need the full tool infrastructure.
    """  # noqa: D202
    
    def __init__(
        self,
        task_id: str,
        name: str,
        handler_name: Optional[str] = None,
        handler: Optional[Callable] = None,
        input_data: Optional[Dict[str, Any]] = None,
        max_retries: int = 0,
        depends_on: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        next_task_id_on_success: Optional[str] = None,
        next_task_id_on_failure: Optional[str] = None,
        condition: Optional[str] = None,
        parallel: bool = False,
        **kwargs
    ):
        """Initialize a DirectHandlerTask.
        
        Args:
            task_id: Unique identifier for the task
            name: Descriptive name for the task
            handler_name: The name of the handler function to execute (required if handler not provided)
            handler: The handler function to execute directly (if provided, takes precedence over handler_name)
            input_data: Input data for the task
            max_retries: Maximum number of retry attempts for the task
            depends_on: IDs of tasks that must complete before this task (not used by Task class)
            timeout: Maximum execution time in seconds (not used by Task class)
            next_task_id_on_success: Task ID to execute if this task succeeds
            next_task_id_on_failure: Task ID to execute if this task fails
            condition: Optional condition to evaluate to determine next task
            parallel: Whether this task can be executed in parallel with others
            **kwargs: Additional task parameters
        """
        # Ensure at least one of handler or handler_name is provided
        if handler is None and handler_name is None:
            raise ValueError("Either handler or handler_name must be provided")
            
        if input_data is None:
            input_data = {}
            
        super().__init__(
            task_id=task_id,
            name=name,
            is_llm_task=False,
            tool_name="N/A",  # Not using tool registry for direct handlers
            input_data=input_data,
            max_retries=max_retries,
            next_task_id_on_success=next_task_id_on_success,
            next_task_id_on_failure=next_task_id_on_failure,
            condition=condition,
            parallel=parallel,
            **kwargs
        )
        
        # Store task-specific properties that aren't part of Task.__init__
        self.handler = handler
        self.handler_name = handler_name
        self.depends_on = depends_on or []
        self.timeout = timeout
        
        # Set task_type after init for serialization
        self.task_type = "direct_handler"
        
        # Flag to indicate this is a direct handler task
        self.is_direct_handler = True
        
        # If handler is provided directly, use its name as handler_name for to_dict()
        if handler is not None and handler_name is None:
            self.handler_name = handler.__name__

    def execute(self, processed_input: Optional[Dict[str, Any]] = None, workflow_variables=None, **kwargs):
        """Execute the handler function with the task input.
        
        Args:
            processed_input: Optional processed input data. If not provided,
                           the task's current input_data will be used.
            workflow_variables: Variables from the workflow that can be referenced in input
            **kwargs: Additional execution parameters
            
        Returns:
            Dict with the result of the handler execution, containing at least:
            - success: bool indicating if the execution was successful
            - result/response: The output data of the handler
            - error: Error message if execution failed (optional)
        """
        # Determine which input to use (processed_input takes precedence over task.input_data)
        input_to_use = processed_input if processed_input is not None else self.input_data
        
        # Apply variable resolution if workflow_variables are provided
        if workflow_variables and not processed_input:
            try:
                from core.variable_resolver import resolve_variables
                input_to_use = resolve_variables(input_to_use, workflow_variables)
            except ImportError:
                # If the resolver module isn't available, just use the input as is
                pass
        
        try:
            # If handler is provided directly, use it
            if self.handler is not None:
                # Pass both self (task) and input_data to handler
                result = self.handler(self, input_to_use)
                
            # Otherwise, use the handler registry to look up by name
            elif hasattr(self, 'handler_name') and self.handler_name:
                try:
                    from core.services import get_handler_registry
                    handler_registry = get_handler_registry()
                    result = handler_registry.execute_handler(self.handler_name, self, input_to_use)
                except (ImportError, ValueError) as e:
                    return {
                        "success": False,
                        "error": f"Handler execution failed: {str(e)}",
                        "error_type": type(e).__name__
                    }
            else:
                return {
                    "success": False,
                    "error": f"Task {self.id} has no handler function or handler_name",
                    "error_type": "ConfigurationError"
                }
            
            # Ensure result is properly formatted as a dictionary
            if not isinstance(result, dict):
                return {
                    "success": False,
                    "error": f"Handler returned non-dict value: {result}",
                    "result": result,
                    "response": result
                }
                
            # If the result doesn't have a success field, assume success if no error
            if "success" not in result:
                result["success"] = "error" not in result
                
            # Ensure both result and response fields exist for compatibility
            if "result" in result and "response" not in result:
                result["response"] = result["result"]
            elif "response" in result and "result" not in result:
                result["result"] = result["response"]
                
            return result
            
        except Exception as e:
            import traceback
            return {
                "success": False,
                "error": f"Handler execution failed: {str(e)}",
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc()
            }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the task to a dictionary representation.

        Returns:
            Dict representation of the task, including direct handler specific fields
        """
        base_dict = super().to_dict()
        base_dict["is_direct_handler"] = True
        base_dict["handler_name"] = self.handler_name
        return base_dict

    def set_tool_registry(self, tool_registry):
        """
        Set the tool registry for the task.
        
        Args:
            tool_registry: Tool registry to use for tool executions
        """
        self.tool_registry = tool_registry


class CustomTask(Task):
    """Base class for implementing custom task types with specialized execution logic.
    
    Custom tasks can define their own execution logic while leveraging the workflow
    system's variable resolution, input processing, and conditional branching.
    """  # noqa: D202
    
    def __init__(
        self,
        task_id: str,
        name: str,
        task_type: str,
        input_data: Dict[str, Any] = None,
        max_retries: int = 0,
        next_task_id_on_success: Optional[str] = None,
        next_task_id_on_failure: Optional[str] = None,
        condition: Optional[str] = None,
        parallel: bool = False,
        is_llm_task: bool = False,  # Allow specifying if this is an LLM task
        **kwargs
    ):
        """Initialize a custom task.
        
        Args:
            task_id: Unique identifier for the task
            name: Display name for the task
            task_type: The type identifier for this custom task
            input_data: Dictionary of input parameters for the task
            max_retries: Number of times to retry the task if it fails
            next_task_id_on_success: Task ID to execute if this task succeeds
            next_task_id_on_failure: Task ID to execute if this task fails
            condition: Optional condition to evaluate to determine next task
            parallel: Whether this task can be executed in parallel with others
            is_llm_task: Whether this task is an LLM task (default: False)
            **kwargs: Additional task-specific parameters
        """
        super().__init__(
            task_id=task_id,
            name=name,
            is_llm_task=is_llm_task,  # Pass the is_llm_task parameter instead of hardcoding
            tool_name=None,     # Custom tasks don't use the tool registry directly
            input_data=input_data,
            max_retries=max_retries,
            next_task_id_on_success=next_task_id_on_success,
            next_task_id_on_failure=next_task_id_on_failure,
            condition=condition,
            parallel=parallel,
            **kwargs
        )
        self.task_type = task_type
        
        # Store any additional parameters as task attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
