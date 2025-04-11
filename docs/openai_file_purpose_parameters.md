# OpenAI File Purpose Parameters

When uploading files to OpenAI's API, the `purpose` parameter indicates how the file will be used. This document outlines the valid purpose values and their uses in the Dawn framework, particularly for vector store operations.

## Valid Purpose Values

The OpenAI API accepts the following values for the `purpose` parameter when uploading files:

| Purpose | Description |
|---------|-------------|
| `assistants` | For files that will be used with the Assistants API, including vector stores |
| `fine-tune` | For files used in fine-tuning models |
| `batch` | For batch processing of files |
| `user_data` | For user-specific data storage |
| `vision` | For files used with vision-capable models |
| `evals` | For evaluation of model performance |

## Important Note for Vector Store Operations

When uploading files to be used with vector stores:

- **Always use `purpose="assistants"`** when uploading files that will be added to a vector store.
- Do not use `purpose="vector_store"` as this is not a valid value and will result in an API error.

## Error Example

Using an invalid purpose like `"vector_store"` will result in this error:

```
Error code: 400 - {'error': {'message': "'vector_store' is not one of ['fine-tune', 'assistants', 'batch', 'user_data', 'vision', 'evals'] - 'purpose'", 'type': 'invalid_request_error', 'param': 'purpose', 'code': None}}
```

## Correct Usage in Code

When using the `upload_file_to_vector_store` tool, you can explicitly set the purpose:

```python
upload_result = registry.execute_tool(
    "upload_file_to_vector_store", 
    {
        "vector_store_id": vector_store_id, 
        "file_path": file_path,
        "purpose": "assistants"  # Always use "assistants" for vector store files
    }
)
```

If the purpose parameter is omitted, the framework will default to using `"assistants"`:

```python
upload_result = registry.execute_tool(
    "upload_file_to_vector_store", 
    {
        "vector_store_id": vector_store_id, 
        "file_path": file_path
        # purpose defaults to "assistants"
    }
)
```

## Implementation Details

The `upload_file_to_vector_store_tool_handler` method in `core/tools/registry.py` handles validation of the purpose parameter:

```python
def upload_file_to_vector_store_tool_handler(self, **data) -> Any:
    # ...
    purpose = data.get("purpose", "assistants")  # Default to 'assistants' if not specified
    
    # Validate purpose parameter
    valid_purposes = ['assistants', 'fine-tune', 'batch', 'user_data', 'vision', 'evals']
    if purpose not in valid_purposes:
        raise ValueError(f"Invalid purpose: '{purpose}'. Must be one of: {', '.join(valid_purposes)}")
    
    return upload_tool.upload_and_add_file_to_vector_store(vector_store_id, file_path, purpose=purpose)
```

## Related Files

- `tools/openai_vs/upload_file_to_vector_store.py`: Implements the file upload functionality
- `core/tools/registry.py`: Contains the handler for file uploads to vector stores
- `fixes/vector_store_purpose_error.md`: Documents the issue and fix for the purpose parameter 