#!/usr/bin/env python3
"""
Core Task Definition for the Workflow Engine.

Defines the base Task class and specialized task types like DirectHandlerTask.
"""  # noqa: D202

from typing import Any, Callable, Dict, List, Optional, TypedDict, Union
import sys

# Add NotRequired compatibility for Python versions before 3.11
if sys.version_info >= (3, 11):
    from typing import NotRequired
else:
    # For Python 3.10 and earlier versions
    from typing_extensions import NotRequired

import json
# Imports moved into methods where first used to potentially mitigate import cycles
# import inspect
# import traceback
from core.utils.variable_resolver import resolve_path # Assumed utility

# --- Standardized Task Output Class ---
class TaskOutput:
    """
    Standard structure for the primary output object of a task.
    Defines the mandatory standardized output format.
    """
    def __init__(self, 
                 success: bool, 
                 status: str,
                 result: Any = None,
                 response: Any = None,
                 error: Optional[str] = None,
                 error_code: Optional[str] = None,
                 error_type: Optional[str] = None,
                 error_details: Optional[Dict[str, Any]] = None,
                 warning: Optional[str] = None,
                 warning_code: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        
        self.success = success
        self.status = status
        
        # Handle result/response consistency
        if result is not None and response is None:
            self.result = result
            self.response = result
        elif response is not None and result is None:
            self.result = response
            self.response = response
        else:
            self.result = result
            self.response = response
            
        self.error = error
        self.error_code = error_code
        self.error_type = error_type
        self.error_details = error_details or {}
        
        self.warning = warning
        self.warning_code = warning_code
        self.metadata = metadata or {}
        
        # Basic validation
        valid_statuses = ["completed", "failed", "skipped", "warning"]
        if self.status not in valid_statuses:
             raise ValueError(f"Invalid status: {self.status}. Must be one of {valid_statuses}")
        if not self.success and not self.error:
             self.error = "Task failed without specific error message."

    def to_dict(self) -> Dict[str, Any]:
        """Convert the TaskOutput object to a dictionary."""
        # Start with core attributes
        data = {
            "success": self.success,
            "status": self.status,
            "result": self.result,
            "response": self.response,
            "metadata": self.metadata
        }
        # Add optional fields only if they have a value
        if self.error is not None: data["error"] = self.error
        if self.error_code is not None: data["error_code"] = self.error_code
        if self.error_type is not None: data["error_type"] = self.error_type
        if self.error_details: data["error_details"] = self.error_details # Add if not empty
        if self.warning is not None: data["warning"] = self.warning
        if self.warning_code is not None: data["warning_code"] = self.warning_code
        
        return data

def validate_output_format(data: Dict[str, Any]) -> TaskOutput:
    """
    Validate and standardize task output data, returning a TaskOutput object.
    
    Args:
        data: The output data dictionary to validate and standardize.
        
    Returns:
        A TaskOutput object representing the standardized output.
    """
    # Extract fields with defaults
    success = data.get("success", "error" not in data) # Infer if missing
    status = data.get("status")
    result = data.get("result")
    response = data.get("response")
    error = data.get("error")
    error_code = data.get("error_code")
    error_type = data.get("error_type")
    error_details = data.get("error_details")
    warning = data.get("warning")
    warning_code = data.get("warning_code")
    metadata = data.get("metadata", {})

    # Handle status logic
    valid_statuses = ["completed", "failed", "skipped", "warning", "success"]
    if status not in valid_statuses:
        if status is not None:
             print(f"Warning: Invalid status '{status}'. Inferring from success.")
        status = "completed" if success else "failed"
    elif status == "success": # Map legacy status
         status = "completed"

    # Handle result/response consistency (prefer result if both exist)
    if result is None and response is not None:
        result = response
    elif response is None and result is not None:
        response = result
        
    # Ensure error message exists if failed
    if not success and error is None:
        error = "Task failed without specific error message."

    # Collect non-standard keys into metadata
    standard_keys = {
        "success", "status", "result", "response", "error", "error_code",
        "error_type", "error_details", "warning", "warning_code", "metadata"
    }
    for key, value in data.items():
        if key not in standard_keys and key not in metadata:
            metadata[key] = value

    # Create and return the TaskOutput object
    try:
        return TaskOutput(
            success=bool(success),
            status=str(status),
            result=result,
            response=response,
            error=str(error) if error is not None else None,
            error_code=str(error_code) if error_code is not None else None,
            error_type=str(error_type) if error_type is not None else None,
            error_details=error_details,
            warning=str(warning) if warning is not None else None,
            warning_code=str(warning_code) if warning_code is not None else None,
            metadata=metadata
        )
    except ValueError as e: # Catch status validation error from __init__
         print(f"Error creating TaskOutput object: {e}. Returning basic failure output.")
         # Fallback to a guaranteed valid failure state
         return TaskOutput(
             success=False,
             status="failed",
             error=f"Internal error processing task output: {e}",
             error_code="INTERNAL_OUTPUT_ERROR"
         )


# --- Base Task Class ---
class Task:
    """
    Represents a fundamental unit of work within a workflow.

    Stores task state, input/output, configuration for execution control
    (retries, branching), and basic metadata. Intended to be subclassed
    or used directly for simple tool execution tasks managed by the engine.
    """  # noqa: D202

    def __init__(
        self,
        task_id: str,
        name: str,
        # Core execution config
        tool_name: Optional[str] = None,        # Tool to execute (if not direct handler/LLM)
        is_llm_task: bool = False,              # Flag for LLM-specific handling
        # Input/Output
        input_data: Optional[Dict[str, Any]] = None,
        # Workflow control
        next_task_id_on_success: Optional[str] = None,
        next_task_id_on_failure: Optional[str] = None,
        condition: Optional[str] = None,        # Condition string for branching
        parallel: bool = False,                 # Hint for parallel execution possibility
        # Error handling
        max_retries: int = 0,
        # File Search specific (often for LLM tasks)
        use_file_search: bool = False,
        file_search_vector_store_ids: Optional[List[str]] = None,
        file_search_max_results: int = 5,
        # Validation flags (implementation specific to engine/handlers)
        validate_input: bool = False,
        validate_output: bool = False,
        # --- Accept arbitrary keyword arguments ---
        **kwargs
    ):
        """
        Initializes a Task instance.

        Args:
            task_id: Unique identifier for the task within the workflow.
            name: Human-readable name for the task.
            tool_name: Name of the tool registered in the ToolRegistry to execute. Required if not is_llm_task and not overridden by a subclass like DirectHandlerTask.
            is_llm_task: Set to True if this task involves a call to the LLMInterface.
            input_data: Static input data or template for dynamic input resolution.
            next_task_id_on_success: ID of the next task if this one completes successfully.
            next_task_id_on_failure: ID of the next task if this one fails.
            condition: A string expression evaluated by the engine to determine branching after success (overrides next_task_id_on_success if condition evaluates to a task ID).
            parallel: Indicates if the engine might schedule this task in parallel (engine implementation dependent).
            max_retries: Number of times to retry the task upon failure.
            use_file_search: Flag to enable file search context injection (typically for LLM tasks).
            file_search_vector_store_ids: List of vector store IDs to use for file search.
            file_search_max_results: Maximum number of file search results to inject.
            validate_input: Flag indicating input validation should be performed.
            validate_output: Flag indicating output validation should be performed.
            **kwargs: Catches extra arguments (like 'description', 'output_key') passed by subclasses or workflow definitions.
        """
        self.id = task_id
        self.name = name
        self.status: str = "pending" # Valid statuses: pending, running, completed, failed, skipped
        self.input_data: Dict[str, Any] = input_data or {}
        self.output_data: TaskOutput = {} # Standardized output structure
        self.output_annotations: List[Any] = [] # For storing annotations from LLMs or tools

        # Execution details
        self.is_llm_task: bool = is_llm_task
        self.tool_name: Optional[str] = tool_name # Relevant for engine executing tool tasks

        # Workflow control attributes
        self.next_task_id_on_success: Optional[str] = next_task_id_on_success
        self.next_task_id_on_failure: Optional[str] = next_task_id_on_failure
        self.condition: Optional[str] = condition
        self.parallel: bool = parallel

        # Retry mechanism
        self.retry_count: int = 0
        self.max_retries: int = max_retries

        # File Search Context (primarily for LLM tasks)
        self.use_file_search: bool = use_file_search
        self.file_search_vector_store_ids: List[str] = file_search_vector_store_ids or []
        self.file_search_max_results: int = file_search_max_results

        # Validation Flags
        self.validate_input: bool = validate_input
        self.validate_output: bool = validate_output

        # Error state storage
        self.error: Optional[str] = None
        self.error_details: Optional[Dict[str, Any]] = None # More structured error info

        # --- Store common optional kwargs if provided ---
        # These are not strictly required by the base Task execution logic
        # but are useful for definition, UI, and potentially subclasses.
        self.description: Optional[str] = kwargs.get("description", None)
        # output_key is more relevant for workflow variable mapping, engine might use it
        self.output_key: Optional[str] = kwargs.get("output_key", None)
        # Store depends_on if provided via kwargs (useful for subclasses like DirectHandlerTask)
        self.depends_on: List[str] = kwargs.get("depends_on", [])

        # --- Placeholder for potentially injected dependencies ---
        self.tool_registry = None # Engine might inject this

        # --- Basic Validation (Can be expanded) ---
        # Removed the strict tool_name check here, as subclasses handle their needs.
        # Engine should validate executable target (tool, handler, LLM) before running.


    def set_status(self, status: str) -> None:
        """Sets the task status, ensuring it's a valid predefined value."""
        valid_statuses = ["pending", "running", "completed", "failed", "skipped"]
        if status not in valid_statuses:
            # Log error instead of raising? Or raise? Let's raise for now.
            raise ValueError(f"Invalid status '{status}' for task '{self.id}'. Must be one of {valid_statuses}")
        self.status = status

    def increment_retry(self) -> None:
        """Increments the task's retry counter."""
        self.retry_count += 1

    def can_retry(self) -> bool:
        """Checks if the task has remaining retry attempts."""
        return self.retry_count < self.max_retries

    def set_input(self, data: Dict[str, Any]) -> None:
        """
        Sets the input data for the task. Usually called by the engine
        after resolving dynamic inputs.
        """
        if not isinstance(data, dict):
             # Handle non-dict input if necessary, maybe wrap it?
             print(f"Warning: Setting non-dict input for task {self.id}: {type(data)}")
             self.input_data = {"value": data} # Example: Wrap in a default key
        else:
             self.input_data = data

    def set_output(self, data: Union[Dict[str, Any], Any]) -> None:
        """
        Sets the task's output, standardizing it into the TaskOutput structure.

        Args:
            data: The output from the task's execution (tool, handler, LLM).
                  Can be a dictionary (preferred) or other data type.
        """
        processed_data: Dict[str, Any] = {}

        # --- Step 1: Ensure data is a dictionary --- 
        if isinstance(data, TaskOutput): # Handle if TaskOutput object is passed directly
             processed_data = data.to_dict()
        elif isinstance(data, dict):
            processed_data = data.copy() # Work with a copy
        elif isinstance(data, Exception):
            # If an exception object was returned, format it as an error
            import traceback
            print(f"Task {self.id} output was an exception: {data}")
            processed_data = {
                "success": False,
                "status": "failed",
                "error": f"Execution returned exception: {str(data)}",
                "error_type": type(data).__name__,
                "error_details": {"traceback": traceback.format_exc()}
            }
        else:
            # If other type, wrap it as the primary result/response
            print(f"Warning: Task {self.id} received non-dict output: {type(data)}. Wrapping.")
            processed_data = {"success": True, "result": data, "response": data}

        # --- Step 2: Standardize the output format --- 
        # validate_output_format now returns a TaskOutput object
        standardized_output_obj = validate_output_format(processed_data)
        
        # --- Step 3: Store error information directly on the task for easy access --- 
        # Use attribute access on the TaskOutput object
        if not standardized_output_obj.success:
            self.error = standardized_output_obj.error # Use attribute access
            self.error_details = standardized_output_obj.error_details # Use attribute access
        else:
            self.error = None # Clear previous errors on success
            self.error_details = None
        
        # --- Step 4: Handle annotations if present --- 
        # Annotations might be in the original dict or metadata
        self.output_annotations = processed_data.get("annotations", standardized_output_obj.metadata.get("annotations", []))
        
        # --- Step 5: Assign the standardized output OBJECT --- 
        self.output_data = standardized_output_obj # Store the object itself
        
        # --- Step 6: Update task status based on final output --- 
        # Use attribute access on the TaskOutput object
        self.set_status(standardized_output_obj.status)


    def get_output_value(self, path: Optional[str] = None, default: Any = None) -> Any:
        """
        Safely retrieves a value from the task's output data using dot notation.

        Args:
            path: Dot-separated path string (e.g., "result.items[0].name", "response.text").
                  If None or empty, returns the primary 'response' value, falling back to 'result'.
            default: Value to return if the path is not found or output is empty.

        Returns:
            The resolved value or the default.
        """
        if not isinstance(self.output_data, TaskOutput):
             # If output_data is not a TaskOutput object (e.g., old format dict), handle gracefully or log error
             print(f"Warning: output_data for task {self.id} is not a TaskOutput object ({type(self.output_data)}). Returning default.")
             return default

        if not path:
            # Return primary output field if no path specified
            return self.output_data.response if self.output_data.response is not None else self.output_data.result

        # Use the path resolver utility - import here if needed
        try:
            from core.utils.variable_resolver import resolve_path # Assumed utility
        except ImportError:
             print("Error: core.utils.variable_resolver.resolve_path not found. Cannot resolve output path.")
             return default # Or raise?

        try:
            # Try resolving within the TaskOutput object's dictionary representation
            output_dict = self.output_data.to_dict()
            return resolve_path(output_dict, path)
        except (KeyError, IndexError, TypeError, ValueError):
            # If direct resolution fails, specifically try resolving within 'response' or 'result' attributes
            base_data = self.output_data.response if self.output_data.response is not None else self.output_data.result
            if base_data is not None:
                try:
                     return resolve_path(base_data, path)
                except (KeyError, IndexError, TypeError, ValueError):
                     pass # Path not found in base_data either
            return default # Path not found anywhere

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the task object into a dictionary."""
        output_data_dict = self.output_data.to_dict() if isinstance(self.output_data, TaskOutput) else self.output_data
        task_dict = {
            "task_id": self.id,
            "name": self.name,
            "status": self.status,
            "input_data": self.input_data,
            "output_data": output_data_dict, # Use the dict representation
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
            # Include optional fields if they have values
            "description": self.description,
            "output_key": self.output_key,
            "depends_on": self.depends_on,
        }
         # Add task_type if defined (useful for deserialization/subclass identification)
        if hasattr(self, 'task_type'):
            task_dict['task_type'] = self.task_type
        if hasattr(self, 'handler_name') and self.handler_name: # Add handler_name if present
            task_dict['handler_name'] = self.handler_name

        # Filter out keys with None values for cleaner output (optional)
        return {k: v for k, v in task_dict.items() if v is not None and v != []}


    def __repr__(self) -> str:
        """Provides a concise string representation of the task."""
        return f"{self.__class__.__name__}(id='{self.id}', name='{self.name}', status='{self.status}')"

    def set_tool_registry(self, tool_registry):
        """
        Injects the ToolRegistry instance. Called by the engine.

        Args:
            tool_registry: The tool registry instance.
        """
        self.tool_registry = tool_registry


# --- Direct Handler Task ---
class DirectHandlerTask(Task):
    """
    A specialized Task that executes a Python callable directly or via registry lookup.

    Useful for simple logic, data transformation, or service calls within the workflow
    without the overhead of defining a full Tool. The handler function is expected
    to return a dictionary conforming roughly to the TaskOutput structure.
    """  # noqa: D202

    def __init__(
        self,
        task_id: str,
        name: str,
        # Handler specification (at least one required)
        handler: Optional[Callable] = None,        # Direct callable
        handler_name: Optional[str] = None,      # Name for registry lookup
        # Standard Task parameters
        input_data: Optional[Dict[str, Any]] = None,
        max_retries: int = 0,
        next_task_id_on_success: Optional[str] = None,
        next_task_id_on_failure: Optional[str] = None,
        condition: Optional[str] = None,
        parallel: bool = False,
        # Specific to handlers/subgraphs - passed via kwargs to Task
        depends_on: Optional[List[str]] = None, # Dependencies for execution order
        timeout: Optional[int] = None,         # Execution timeout (engine implementation)
        **kwargs # Catches description, output_key, etc.
    ):
        """
        Initializes a DirectHandlerTask.

        Args:
            task_id: Unique task identifier.
            name: Human-readable task name.
            handler: The Python function/callable to execute directly. Takes precedence over handler_name.
            handler_name: The string name used to look up the handler function in the HandlerRegistry. Required if 'handler' is not provided.
            input_data: Input data dictionary or template.
            max_retries: Maximum retry attempts on failure.
            next_task_id_on_success: Next task ID on success.
            next_task_id_on_failure: Next task ID on failure.
            condition: Conditional branching expression.
            parallel: Parallel execution hint.
            depends_on: List of task IDs this task depends on.
            timeout: Optional execution timeout in seconds (enforced by engine).
            **kwargs: Additional arguments (like 'description', 'output_key') passed to the base Task constructor.
        """
        if handler is None and handler_name is None:
            raise ValueError(f"DirectHandlerTask '{task_id}' requires either 'handler' callable or 'handler_name' string.")

        # Ensure depends_on from kwargs is passed correctly to Task constructor
        if depends_on is not None:
             kwargs['depends_on'] = depends_on

        super().__init__(
            task_id=task_id,
            name=name,
            is_llm_task=False, # Handlers are not LLM tasks by default
            tool_name=None,    # Direct handlers don't use tools directly
            input_data=input_data, # Pass input_data through
            max_retries=max_retries,
            next_task_id_on_success=next_task_id_on_success,
            next_task_id_on_failure=next_task_id_on_failure,
            condition=condition,
            parallel=parallel,
            # Pass all other keyword args (description, output_key, depends_on etc.)
            **kwargs
        )

        # Store DirectHandlerTask specific attributes
        self.handler: Optional[Callable] = handler
        self.handler_name: Optional[str] = handler_name
        # `depends_on` is now also stored in the base class via kwargs
        self.timeout: Optional[int] = timeout # Specific timeout for this task type

        # --- Set identifier ---
        self.task_type: str = "direct_handler"
        # Add flag for convenience?
        self.is_direct_handler = True

        # --- Infer handler_name if missing and handler is provided ---
        if self.handler is not None and self.handler_name is None:
            try:
                self.handler_name = self.handler.__name__
            except AttributeError:
                self.handler_name = f"callable_{id(self.handler)}" # Fallback for lambdas/non-functions


    def execute(self, processed_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes the assigned handler function IF it was provided directly.

        NOTE: This method is primarily for cases where the `handler` callable
        was passed during initialization. The WorkflowEngine is typically
        responsible for looking up handlers by `handler_name` from the registry
        and then calling the appropriate execution function (which might involve
        this `execute` method or other logic).

        Args:
            processed_input: The resolved input data provided by the engine.
                             If None, uses the task's static `input_data`.

        Returns:
            A dictionary representing the standardized task output (TaskOutput).
        """
        if not callable(self.handler):
            # This indicates an issue: execute() called but no direct handler.
            # The engine should have used the registry based on handler_name.
            error_msg = f"Task '{self.id}': execute() called but no direct callable handler assigned."
            if self.handler_name:
                error_msg += f" Engine should resolve handler '{self.handler_name}' first."
            else:
                error_msg += " No handler or handler_name was properly configured."
            print(f"ERROR - {error_msg}")
            self.set_output({"success": False, "error": error_msg, "status": "failed"})
            return self.output_data

        input_to_use = processed_input if processed_input is not None else self.input_data

        print(f"Executing direct handler for task '{self.id}' ({self.handler_name or 'anonymous'})...")
        try:
            # Use inspect to call handler correctly (1 or 2 args)
            import inspect # Import locally
            handler_sig = inspect.signature(self.handler)
            param_count = len(handler_sig.parameters)

            if param_count == 1:
                # Assumes handler(input_data: dict) -> dict
                result = self.handler(input_to_use)
            elif param_count == 2:
                # Assumes handler(task: Task, input_data: dict) -> dict
                result = self.handler(self, input_to_use)
            else:
                raise TypeError(f"Handler '{self.handler_name or 'anonymous'}' for task '{self.id}' has an invalid signature: {param_count} parameters detected. Expected 1 (input_data) or 2 (task, input_data).")

            # Standardize and store the output
            self.set_output(result)
            print(f"Direct handler for task '{self.id}' finished with status: {self.status}")

        except Exception as e:
            import traceback # Import locally
            error_msg = f"Exception during direct handler execution for task '{self.id}': {str(e)}"
            print(f"ERROR - {error_msg}\n{traceback.format_exc()}")
            # Set output with error details including traceback
            self.set_output({
                "success": False,
                "error": error_msg,
                "error_type": type(e).__name__,
                "error_details": {"traceback": traceback.format_exc()},
                "status": "failed"
            })

        return self.output_data # Return the standardized output stored in the task


    def to_dict(self) -> Dict[str, Any]:
        """Serializes the DirectHandlerTask to a dictionary."""
        # Start with the base class dictionary which now includes optional fields
        task_dict = super().to_dict()
        # Add/override specific fields for DirectHandlerTask
        task_dict['task_type'] = self.task_type
        task_dict['is_direct_handler'] = True
        # handler callable itself cannot be serialized, rely on handler_name
        task_dict['handler_name'] = self.handler_name
        # Include timeout if it exists and wasn't None
        if self.timeout is not None and 'timeout' not in task_dict:
             task_dict['timeout'] = self.timeout
        # depends_on should be included by base class now

        # Filter out None values again if desired
        return {k: v for k, v in task_dict.items() if v is not None and v != []}


# --- Custom Task Base Class ---
class CustomTask(Task):
    """
    Base class for creating new, specialized task types.

    Subclasses should define a unique `task_type` identifier and potentially
    override the `execute` method or provide specific logic for the engine
    to use based on the `task_type`.
    """  # noqa: D202

    def __init__(
        self,
        task_id: str,
        name: str,
        task_type: str, # REQUIRED: Unique identifier for this custom task type
        input_data: Optional[Dict[str, Any]] = None,
        max_retries: int = 0,
        next_task_id_on_success: Optional[str] = None,
        next_task_id_on_failure: Optional[str] = None,
        condition: Optional[str] = None,
        parallel: bool = False,
        is_llm_task: bool = False, # Allow custom tasks to be LLM tasks
        **kwargs # Capture description, output_key, depends_on, and custom params
    ):
        """
        Initializes a CustomTask instance.

        Args:
            task_id: Unique task identifier.
            name: Human-readable task name.
            task_type: String identifier for this custom task's type (e.g., "send_email", "database_query").
            input_data: Input data dictionary or template.
            max_retries: Maximum retry attempts.
            next_task_id_on_success: Next task on success.
            next_task_id_on_failure: Next task on failure.
            condition: Conditional branching expression.
            parallel: Parallel execution hint.
            is_llm_task: Flag if this custom task involves LLM calls.
            **kwargs: Additional arguments passed to Task base class (description, output_key, depends_on) and stored as attributes on the CustomTask instance for specific logic.
        """
        if not task_type:
            raise ValueError(f"CustomTask '{task_id}' requires a non-empty 'task_type' identifier.")

        super().__init__(
            task_id=task_id,
            name=name,
            is_llm_task=is_llm_task,
            tool_name=None, # Custom tasks don't use tool_name directly
            input_data=input_data, # Pass through input_data
            max_retries=max_retries,
            next_task_id_on_success=next_task_id_on_success,
            next_task_id_on_failure=next_task_id_on_failure,
            condition=condition,
            parallel=parallel,
            # Pass standard optional args and any others up to Task
            **kwargs
        )

        # Store the specific type identifier
        self.task_type: str = task_type

        # Store any *additional* keyword arguments from kwargs that were NOT
        # handled by the base Task.__init__ directly as attributes on this instance.
        # This allows custom task definitions like CustomTask(..., custom_param='value')
        base_task_params = {
            'task_id', 'name', 'is_llm_task', 'tool_name', 'input_data',
            'max_retries', 'next_task_id_on_success', 'next_task_id_on_failure',
            'condition', 'parallel', 'use_file_search', 'file_search_vector_store_ids',
            'file_search_max_results', 'validate_input', 'validate_output',
            'description', 'output_key', 'depends_on' # Include those stored by Task from kwargs
        }
        for key, value in kwargs.items():
            if key not in base_task_params:
                if hasattr(self, key):
                     print(f"Warning: CustomTask kwarg '{key}' for task '{self.id}' conflicts with an existing Task attribute. Consider renaming.")
                else:
                     setattr(self, key, value)


    # Custom tasks NEED to define how they execute.
    # This could be an overridden execute method, or the engine could look
    # for a handler based on self.task_type. An explicit override is clearer.
    def execute(self, processed_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Placeholder execute method. Subclasses MUST override this.

        The engine will call this method to run the custom task's logic.
        It should perform its action and return a dictionary conforming
        to TaskOutput.
        """
        error_msg = f"Execute method not implemented for CustomTask type '{self.task_type}' (task_id='{self.id}')."
        print(f"ERROR - {error_msg}")
        self.set_output({"success": False, "error": error_msg, "status": "failed"})
        return self.output_data # Return standardized error output


    def to_dict(self) -> Dict[str, Any]:
        """Serializes the CustomTask to a dictionary."""
        task_dict = super().to_dict()
        # Ensure task_type is present
        task_dict['task_type'] = self.task_type

        # Add custom attributes stored from kwargs during init
        base_task_params = set(Task.__init__.__code__.co_varnames[1:Task.__init__.__code__.co_argcount]) | {'description', 'output_key', 'depends_on'} # Get base params programmatically + optional ones
        # Add known attributes from Task that might not be in __init__ args
        known_task_attrs = base_task_params | {'status', 'output_data', 'output_annotations', 'retry_count', 'error', 'error_details', 'tool_registry', 'task_type'}

        for key, value in self.__dict__.items():
            # Include attributes that are not standard Task attributes (or already included)
            # and are not internal/private
            if not key.startswith('_') and key not in known_task_attrs and key not in task_dict:
                 # Basic serialization check - skip callables for now
                 if not callable(value):
                     task_dict[key] = value
                 else:
                      print(f"Warning: Skipping callable attribute '{key}' during CustomTask serialization for task '{self.id}'.")

        return task_dict