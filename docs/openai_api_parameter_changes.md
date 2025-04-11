# OpenAI API Parameter Changes

This document outlines parameter changes in the OpenAI API and how the Dawn framework handles them to maintain compatibility.

## Vector Store Operations

### Adding Files to Vector Stores

When adding files to a vector store, the OpenAI API parameter names have changed:

#### Parameter Change

| Old Parameter | New Parameter | API Endpoint |
|---------------|--------------|--------------|
| `file_ids`    | `files`      | `vector_stores.files.create()` |

#### Our Solution

Initially, we implemented a fallback mechanism to handle this change:

```python
try:
    # Try with the expected parameter name
    file_batch = client.vector_stores.files.create(
        vector_store_id=vector_store_id, 
        files=[file_id]  # Current parameter name
    )
except Exception:
    # If that fails, try the alternative
    file_batch = client.vector_stores.files.create(
        vector_store_id=vector_store_id,
        file_ids=[file_id]  # Old parameter name
    )
```

However, we discovered that both approaches failed with the current version of the OpenAI Python client. The client rejects both `file_ids` and `files` parameter names.

#### Direct API Call Solution

Due to the parameter issues with the Python client, we implemented a direct API call using HTTPX:

```python
# Get API key from the client
api_key = client.api_key

# Make direct API call using httpx
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "OpenAI-Beta": "vector_stores=v1"  # Correctly formatted beta header
}

url = f"https://api.openai.com/v1/vector_stores/{vector_store_id}/files"

# Try with file_id parameter
payload = {"file_id": file_id}

with httpx.Client(timeout=60.0) as http_client:
    response = http_client.post(url, json=payload, headers=headers)
    
    if response.status_code != 200 and response.status_code != 201:
        # Try alternative payload format
        payload = {"files": [file_id]}
        response = http_client.post(url, json=payload, headers=headers)
```

This approach allows us to:
1. Bypass the Python client's parameter validation
2. Try multiple payload formats directly with the REST API
3. Get detailed error messages from the API response

### Polling for File Processing Status

When checking the status of files added to vector stores, we encountered parameter mismatches with the OpenAI Python client:

```
Debug - Error while polling: FileBatches.retrieve() got an unexpected keyword argument 'file_batch_id'
```

#### Direct API Polling Solution

Similar to the file upload issue, we implemented a direct API call solution for polling:

```python
# Previous approach using client library (not working)
batch_status = client.vector_stores.file_batches.retrieve(
    vector_store_id=vector_store_id, 
    file_batch_id=batch_id
)

# New approach using direct API call
poll_url = f"https://api.openai.com/v1/vector_stores/{vector_store_id}/files/{file_id}"
poll_headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

with httpx.Client(timeout=30.0) as poll_client:
    poll_response = poll_client.get(poll_url, headers=poll_headers)
    if poll_response.status_code == 200:
        poll_data = poll_response.json()
        status = poll_data.get("status", "unknown")
```

This approach has several advantages:
1. Avoids parameter mismatches with the client library
2. Provides direct access to the status response data
3. Allows for more flexible status handling

Additionally, we improved error handling by returning a success status even if polling times out, since the file has been successfully added to the vector store.

### Beta API Header Format

When working with beta OpenAI APIs, the `OpenAI-Beta` header must follow a specific format:

```
OpenAI-Beta: feature_name=vX
```

Where:
- `feature_name` is the name of the beta feature (e.g., `vector_stores`)
- `vX` is the version number (e.g., `v1`)

For example, to use the vector stores beta API, the correct header is:

```
OpenAI-Beta: vector_stores=v1
```

Using an incorrect format like just `v1` will result in a 400 error with an "invalid_beta" error code.

#### Update: Vector Stores API No Longer Requires Beta Header

As of the latest API version, the vector stores API no longer requires a beta header. When using the beta header with `vector_stores` as the feature name, the API returns:

```json
{
  "error": {
    "message": "Unknown beta requested: 'vector_stores'.",
    "type": "invalid_request_error",
    "param": null,
    "code": "invalid_beta"
  }
}
```

This suggests that the vector stores API has been promoted to a standard API and no longer requires the beta header. Our current implementation makes direct API calls without the beta header:

```python
# Current approach without beta header
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
    # No OpenAI-Beta header
}
```

### File Upload Purpose

The OpenAI API restricts the values allowed for the `purpose` parameter when uploading files:

#### Valid Purpose Values

| Purpose | Description |
|---------|-------------|
| `assistants` | For files that will be used with the Assistants API, including vector stores |
| `fine-tune` | For files used in fine-tuning models |
| `batch` | For batch processing of files |
| `user_data` | For user-specific data storage |
| `vision` | For files used with vision-capable models |
| `evals` | For evaluation of model performance |

Note that `vector_store` is not a valid purpose value, even though the files will be used in a vector store.

#### Our Solution

We now always use `purpose="assistants"` when uploading files that will be used in vector stores:

```python
upload_response = client.files.create(
    file=file_obj,
    purpose="assistants"  # Valid purpose for files that will be used in vector stores
)
```

## Best Practices for Handling API Changes

1. **Implement Fallbacks**: Where possible, implement fallback mechanisms that try alternative parameter names or values.
2. **Detailed Error Handling**: Catch specific errors and provide detailed error messages.
3. **Debug Logging**: Include debug logs that help identify which API calls succeed or fail.
4. **Documentation**: Document known API changes and how they're handled.

## Related Files

- `tools/openai_vs/upload_file_to_vector_store.py`: Implementation of file uploads to vector stores
- `core/tools/registry.py`: Handles parameter validation and error handling for tool calls
- `fixes/vector_store_purpose_error.md`: Documents the purpose parameter error and fix
- `fixes/vector_store_file_parameter_error.md`: Documents the file parameter error and fix 