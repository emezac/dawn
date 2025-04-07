# core/utils/logger.py

# Simple print-based logger. Replace with a proper logging setup (e.g., using Python's logging module) for production.

def log_workflow_start(workflow_id, workflow_name):
    """Logs the start of a workflow execution."""
    print(f"\n>>> Workflow START: {workflow_name} (ID: {workflow_id})")

def log_workflow_end(workflow_id, workflow_name, status, **kwargs):
    """Logs the end of a workflow execution."""
    # kwargs allows for future flexibility, e.g., adding duration
    print(f"<<< Workflow END: {workflow_name} (ID: {workflow_id}) | Status: {status}\n")

def log_task_start(task_id, task_name, workflow_id):
    """Logs the start of a task execution."""
    print(f"  [TASK START] >> '{task_name}' (ID: {task_id})")

def log_task_end(task_id, task_name, status, workflow_id):
    """Logs the end of a task execution."""
    print(f"  [TASK END] << '{task_name}' (ID: {task_id}) | Status: {status}")

def log_task_retry(task_id, task_name, retry_count, max_retries):
    """Logs a task retry attempt."""
    # retry_count is 0-based, so add 1 for user-friendly message
    print(f"  [TASK RETRY] !! '{task_name}' (ID: {task_id}) | Attempt {retry_count + 1} of {max_retries + 1}")

def log_task_input(task_id, input_data):
    """Logs the processed input data for a task."""
    # Avoid printing very large inputs, show keys or simplified representation
    input_preview = input_data
    if isinstance(input_data, dict) and len(str(input_data)) > 300: # Example threshold
        input_preview = {k: (type(v) if len(str(v)) < 50 else f"{type(v)}[len:{len(str(v))}]") for k, v in input_data.items()}
    print(f"  [TASK INPUT] -- '{task_id}' | Data: {input_preview}")

def log_task_output(task_id, output_data):
     """Logs the output data from a task execution."""
     # Avoid printing very large outputs
     output_preview = output_data
     if isinstance(output_data, dict) and len(str(output_data)) > 300:
          output_preview = {k: (type(v) if len(str(v)) < 50 else f"{type(v)}[len:{len(str(v))}]") for k, v in output_data.items()}
     print(f"  [TASK OUTPUT] -- '{task_id}' | Data: {output_preview}")


def log_error(message):
    """Logs an error message."""
    print(f"ERROR: {message}")

def log_info(message):
    """Logs informational messages."""
    print(f"INFO: {message}")

def log_warning(message):
    """Logs warning messages."""
    print(f"WARNING: {message}")

def log_error(message, **kwargs): # Add **kwargs here
    """Logs an error message."""
    print(f"ERROR: {message}") # Keep it simple for now