# Dawn Framework Debug Mode

This document describes the debug mode features in the Dawn Framework, including how to enable debug mode, what features are available, and how to use them effectively.

## Overview

Debug mode in the Dawn Framework provides additional logging, performance metrics, and debugging tools for development environments. It's designed to help developers identify issues, understand workflow execution, and monitor application performance.

**Important**: Debug mode is intended for development environments only and should not be enabled in production due to its performance impact and potentially sensitive information exposure.

## Enabling Debug Mode

Debug mode can be enabled through configuration or environment variables:

### Using Configuration

```python
from core.config import configure, set

# Enable debug mode at initialization
configure(config_paths=["config/config.json"], environment="development")
set("debug_mode", True)
```

Or in your configuration file (`config.json` or `development.json`):

```json
{
  "environment": "development",
  "debug_mode": true,
  "debug_mode.log_level": "DEBUG",
  "debug_mode.enable_web_panel": true,
  "debug_mode.enable_web_middleware": true,
  "debug_mode.performance_monitoring": true
}
```

### Using Environment Variables

```bash
export DAWN_DEBUG_MODE=true
export DAWN_ENVIRONMENT=development
```

### Using the Debug Initializer

The easiest way to enable debug mode is to import the debug initializer at application startup:

```python
# Import this at application startup
from core.utils.debug_initializer import setup_debug_mode

# Optionally force enable debug mode
setup_debug_mode(force_enable=True)
```

## Debug Features

### 1. Enhanced Logging

Debug mode provides enhanced logging with:

- More detailed log messages at the DEBUG level
- Function call information (file, line, function name)
- Optional file-based logging
- Prettified output for complex data structures

Example usage:

```python
from core.utils.debug import debug_log

# Log a simple message
debug_log("Processing request")

# Log a message with data
user_data = {"id": 123, "name": "John Doe", "roles": ["admin", "editor"]}
debug_log("User data received", user_data)
```

### 2. Performance Monitoring

Debug mode includes performance monitoring for:

- Workflow execution time
- Task execution time
- Tool execution time
- Database query time
- API request time

The performance data is available in the debug panel and through the debug API.

Example usage:

```python
from core.utils.debug import measure_execution_time

@measure_execution_time
def expensive_operation():
    # This function's execution time will be logged
    ...
```

### 3. Workflow Debugging

Debug mode provides advanced workflow debugging features:

- Detailed task execution tracking
- Variable resolution monitoring
- Execution path visualization
- Detailed error information

The workflow debugger is automatically enabled for all workflows when debug mode is active.

### 4. Web Debug Panel

Debug mode includes a web-based debug panel accessible at `/debug` when using the Dawn web server. The debug panel provides:

- System information
- Configuration overview (with sensitive values masked)
- Workflow execution history
- Task performance metrics
- Variable resolution history
- Error logs

The debug panel auto-refreshes every 10 seconds to show the latest information.

### 5. Debug Middleware

Debug mode includes middleware for the web server that provides:

- Request/response logging
- Performance timing for API calls
- Debug headers (`X-Debug-Time`, `X-Debug-Request-ID`)
- Enhanced error responses with debug information

## Debug Mode Configuration

Debug mode supports the following configuration options:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `debug_mode` | `bool` | `false` | Master switch for debug mode |
| `debug_mode.log_level` | `str` | `"DEBUG"` | Logging level for debug mode |
| `debug_mode.log_file` | `str` | `null` | Optional file path for debug logs |
| `debug_mode.enable_web_panel` | `bool` | `true` | Enable the web debug panel |
| `debug_mode.enable_web_middleware` | `bool` | `true` | Enable debug middleware for web requests |
| `debug_mode.performance_monitoring` | `bool` | `true` | Enable performance monitoring |

## Debug API

Debug mode exposes a REST API at `/debug/api` when using the Dawn web server. The API provides programmatic access to debug information.

### Endpoints

- `GET /debug/api` - Get all debug data
- `GET /debug/api/workflows` - Get workflow execution history
- `GET /debug/api/workflows/{id}` - Get details for a specific workflow
- `GET /debug/api/errors` - Get error history
- `GET /debug/api/performance` - Get performance metrics
- `GET /debug/api/system` - Get system information
- `GET /debug/api/config` - Get configuration (with sensitive values masked)

## Debug Utilities

### Variable Dumping

Debug mode includes utilities for dumping variables:

```python
from core.utils.debug import dump_variables

# Dump local variables
variables = dump_variables()
```

### Execution Time Measurement

```python
from core.utils.debug import measure_execution_time

# Use as a decorator
@measure_execution_time
def my_function():
    ...

# Or as a context manager
with measure_execution_time("operation_name"):
    ...
```

### Debug Assertion

```python
from core.utils.debug import debug_assert

# Only checked in debug mode
debug_assert(len(items) > 0, "Items list cannot be empty")
```

## Best Practices

1. **Enable in Development Only**: Debug mode should only be enabled in development environments.
2. **Use Selective Logging**: Use `debug_log` for important information to avoid log file bloat.
3. **Secure Debug Panel**: If exposing the debug panel in shared development environments, consider adding authentication.
4. **Monitor Performance Impact**: Debug mode adds overhead, so monitor performance impact.
5. **Clean Up Debug Code**: Remove `debug_log` calls before merging to production code.

## Troubleshooting

### Debug Mode Not Working

If debug mode doesn't seem to be working:

1. Ensure `debug_mode` is set to `True` in configuration.
2. Ensure `environment` is set to `development`.
3. Check that the debug initializer is imported at application startup.
4. Verify that logs show "Debug mode is ENABLED" at startup.

### Debug Panel Not Accessible

If the debug panel is not accessible:

1. Ensure the web server is running.
2. Verify that logs show "Debug panel enabled at /debug".
3. Check that the route isn't being overridden by another handler.

## Examples

### Basic Debug Mode Usage

```python
# app.py
from core.utils.debug_initializer import setup_debug_mode
from core.utils.debug import debug_log

# Set up debug mode
setup_debug_mode()

def main():
    debug_log("Application starting")
    # ...

if __name__ == "__main__":
    main()
```

### Workflow Debugging

```python
# workflow_example.py
from core.utils.debug_initializer import setup_debug_mode
from core.workflow.workflow import Workflow
from core.workflow.engine import WorkflowEngine
from core.workflow.task import Task

# Set up debug mode
setup_debug_mode()

# Create a workflow
workflow = Workflow(workflow_id="example", name="Example Workflow")

# Add tasks
task1 = Task(task_id="task1", name="Task 1", ...)
workflow.add_task(task1)

# ... add more tasks ...

# Run the workflow
engine = WorkflowEngine()
result = engine.run_workflow(workflow)

# Debug report is available in result["_debug"] if result is a dict
```

### Web Application with Debug Panel

```python
# app.py
from core.utils.debug_initializer import setup_debug_mode
from core.web.app import create_app

# Set up debug mode
setup_debug_mode()

# Create the web application
app = create_app()

if __name__ == "__main__":
    app.run(host="localhost", port=8000)
```

## Related Documentation

- [Configuration System](configuration_system.md)
- [Workflow System](workflow_system.md)
- [Web Server](web_server.md) 