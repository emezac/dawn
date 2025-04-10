import logging

from pythonjsonlogger import jsonlogger

# Create a logger
logger = logging.getLogger("agent_framework")
logHandler = logging.StreamHandler()

# Define the log format
formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(workflow_id)s %(task_id)s %(event)s %(message)s")
logHandler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)


# Example logging usage
def log_task_event(workflow_id, task_id, event, status, message=""):
    logger.info(
        message,
        extra={"workflow_id": workflow_id, "task_id": task_id, "event": event, "status": status},
    )


# Example usage
if __name__ == "__main__":
    log_task_event("wf_001", "task_01", "task_started", "in_progress", "Task execution started.")
    log_task_event("wf_001", "task_01", "task_completed", "success", "Task completed successfully.")
