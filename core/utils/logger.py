def log_workflow_start(workflow_id, workflow_name):
    print(f"Workflow {workflow_name} (ID: {workflow_id}) started.")

def log_workflow_end(workflow_id, workflow_name, status):
    print(f"Workflow {workflow_name} (ID: {workflow_id}) ended with status: {status}.")

def log_task_start(task_id, task_name, workflow_id):
    print(f"Task {task_name} (ID: {task_id}) in workflow {workflow_id} started.")

def log_task_end(task_id, task_name, status, workflow_id):
    print(f"Task {task_name} (ID: {task_id}) in workflow {workflow_id} ended with status: {status}.")

def log_task_retry(task_id, task_name, retry_count, max_retries):
    print(f"Retrying task {task_name} (ID: {task_id}). Attempt {retry_count} of {max_retries}.")

def log_task_input(task_id, input_data):
    print(f"Task {task_id} input: {input_data}")

def log_task_output(task_id, output_data):
    print(f"Task {task_id} output: {output_data}")

def log_error(message):
    print(f"Error: {message}") 