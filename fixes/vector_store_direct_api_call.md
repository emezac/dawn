# Vector Store Direct API Call Approach

## Issue

After trying multiple parameter formats (`file_ids`, `files`, `file_id`), we discovered that the OpenAI Python client's method for adding files to vector stores was not working with any standard parameter format:

```
Debug - Direct file_id parameter failed: Files.create() got an unexpected keyword argument 'file_id'
Debug - Array file_id parameter failed: Files.create() got an unexpected keyword argument 'file_id'
```

This suggests that the OpenAI API client might be out of sync with the current REST API requirements.

## Root Cause

The OpenAI Python client version we're using doesn't correctly implement the vector store file addition functionality, or the API has changed in a way that is not reflected in the current client version. Multiple parameter formats were rejected by the client, indicating a mismatch between the client implementation and the REST API requirements.

## Solution

Instead of using the Python client's built-in methods, we implemented a direct API call using the HTTPX library:

```python
# Get API key from the client
api_key = client.api_key

# Make direct API call using httpx
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "OpenAI-Beta": "v1"
}

url = f"https://api.openai.com/v1/vector_stores/{vector_store_id}/files"

# Try with file_id parameter
payload = {"file_id": file_id}

with httpx.Client(timeout=60.0) as http_client:
    response = http_client.post(url, json=payload, headers=headers)
    
    if response.status_code == 200 or response.status_code == 201:
        response_data = response.json()
        batch_id = response_data.get("id", "unknown")
    else:
        # Try alternative payload format if first attempt failed
        payload = {"files": [file_id]}
        response = http_client.post(url, json=payload, headers=headers)
```

This approach allows us to:
1. Bypass the Python client's parameter validation
2. Try multiple payload formats directly with the REST API
3. Get detailed error messages from the API response

## Implementation Details

1. **Direct API Call**: Used HTTPX to make a direct POST request to the OpenAI API
2. **Multiple Payload Formats**: Tried both `{"file_id": file_id}` and `{"files": [file_id]}` formats
3. **Enhanced Error Handling**: Captured HTTP status codes and response bodies for better debugging
4. **Flexible Approach**: Designed to adapt to API changes without requiring client updates

## Testing and Validation

After implementing this fix, we tested the solution with the context-aware legal review workflow:
1. The direct API call successfully added files to vector stores
2. The save_to_ltm functionality worked correctly
3. The workflow completed successfully

## Lessons Learned

1. **Direct API Calls**: When official client libraries don't work as expected, making direct API calls can be a reliable fallback
2. **Multiple Format Testing**: When working with evolving APIs, trying multiple parameter formats is a good strategy
3. **Detailed Logging**: Including detailed debugging information helps troubleshoot issues with third-party APIs

## Related Files

- `tools/openai_vs/upload_file_to_vector_store.py`: Contains the implementation of the direct API call approach
- `fixes/vector_store_api_parameter_exploration.md`: Documents our exploration process 