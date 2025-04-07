from typing import Dict, Optional, Any

class Task:
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
        parallel: bool = False
    ):
        self.id = task_id
        self.name = name
        self.status = "pending"
        self.input_data = input_data or {}
        self.output_data = {}
        self.is_llm_task = is_llm_task
        self.tool_name = tool_name
        self.retry_count = 0
        self.max_retries = max_retries
        self.next_task_id_on_success = next_task_id_on_success
        self.next_task_id_on_failure = next_task_id_on_failure
        self.condition = condition
        self.parallel = parallel

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
        }

    def __repr__(self) -> str:
        return f"Task(id={self.id}, name={self.name}, status={self.status})"