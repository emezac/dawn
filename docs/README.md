## Parallel Workflows

Parallel workflows allow tasks to be executed concurrently, improving efficiency and reducing execution time for independent tasks.

### Usage Example

```python
workflow = [
    {"id": "task_1", "tool": "web_search", "dependencies": []},
    {"id": "task_2", "tool": "calculate", "dependencies": []},
    {"id": "task_3", "tool": "summarize_results", "dependencies": ["task_1", "task_2"]},
]
```

In this example, `task_1` and `task_2` can run in parallel, while `task_3` waits for both to complete. 