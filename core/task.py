from typing import Any, Callable, Dict, List, Optional


class Task:
    """
    Represents a unit of work within a workflow with properties for status tracking,
    input/output data, and execution control like retry logic and conditional branching.
    """

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
    ):
        self.id = task_id
        self.name = name
        self.status = "pending"
        self.input_data = input_data or {}
        self.output_data = {}
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

        if not self.is_llm_task and not self.tool_name:
            raise ValueError("Non-LLM tasks must specify a tool_name")

    def set_status(self, status: str) -> None:
        valid_statuses = ["pending", "running", "completed", "failed"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")
        self.status = status

    def increment_retry(self) -> None:
        self.retry_count += 1

    def can_retry(self) -> bool:
        return self.retry_count < self.max_retries

    def set_input(self, data: Dict[str, Any]) -> None:
        self.input_data = data

    def set_output(self, data: Dict[str, Any]) -> None:
        self.output_data = data
        self.output_annotations = data.get("annotations", [])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
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
        }

    def __repr__(self) -> str:
        return f"Task(id={self.id}, name={self.name}, status={self.status})"


class DirectHandlerTask(Task):
    """
    A Task subclass that directly executes a handler function without using the tool registry.

    This provides a way to integrate custom task handling directly into workflows without
    needing to register tools in the global registry.
    """

    def __init__(
        self,
        task_id: str,
        name: str,
        handler: Callable[[Dict[str, Any]], Dict[str, Any]],
        input_data: Optional[Dict[str, Any]] = None,
        condition: Optional[str] = None,
        next_task_id_on_success: Optional[str] = None,
        next_task_id_on_failure: Optional[str] = None,
        max_retries: int = 0,
        parallel: bool = False,
    ):
        """
        Initialize a new DirectHandlerTask.

        Args:
            task_id: Unique identifier for the task
            name: Human-readable name for the task
            handler: Function that will be called with the task's input_data
            input_data: Initial input data for the task
            condition: Optional condition for task execution
            next_task_id_on_success: ID of the next task to execute on success
            next_task_id_on_failure: ID of the next task to execute on failure
            max_retries: Maximum number of times to retry the task if it fails
            parallel: Whether this task can be executed in parallel with others
        """
        # Initialize with Task constructor, using special tool_name format
        super().__init__(
            task_id=task_id,
            name=name,
            tool_name="__direct_handler__",  # Special placeholder value
            is_llm_task=False,
            input_data=input_data,
            condition=condition,
            next_task_id_on_success=next_task_id_on_success,
            next_task_id_on_failure=next_task_id_on_failure,
            max_retries=max_retries,
            parallel=parallel,
        )

        # Store the handler function
        self.handler = handler
        # Add a flag to identify this as a direct handler task
        self.is_direct_handler = True

    def execute(self, processed_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the handler function directly with the provided input data.

        Args:
            processed_input: Optional processed input data. If not provided,
                           the task's current input_data will be used.

        Returns:
            Dict with the result of the handler execution, containing at least:
            - success: bool indicating if the execution was successful
            - result/response: The output data of the handler
            - error: Error message if execution failed (optional)
        """
        try:
            # Use provided processed input or fall back to task's input_data
            input_to_use = processed_input if processed_input is not None else self.input_data

            # Execute the handler
            result = self.handler(input_to_use)

            # Ensure result is properly formatted
            if not isinstance(result, dict):
                return {"success": False, "error": f"Handler returned non-dict value: {type(result).__name__}"}

            # If success flag is not present, infer from presence of error
            if "success" not in result and "status" not in result:
                result["success"] = "error" not in result

            return result

        except Exception as e:
            # Capture any exceptions from the handler
            import traceback

            return {
                "success": False,
                "error": f"Handler execution failed: {str(e)}",
                "exception_type": type(e).__name__,
                "traceback": traceback.format_exc(),
            }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the task to a dictionary representation.

        Returns:
            Dict representation of the task, including direct handler specific fields
        """
        base_dict = super().to_dict()
        base_dict["is_direct_handler"] = True
        base_dict["handler_name"] = self.handler.__name__ if hasattr(self.handler, "__name__") else "anonymous_function"
        return base_dict
