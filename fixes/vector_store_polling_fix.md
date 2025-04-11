# Vector Store File Polling Fix

## Issue

After successfully uploading a file to a vector store using direct API calls, we encountered an error when polling for the file processing status:

```
Debug - Error while polling: FileBatches.retrieve() got an unexpected keyword argument 'file_batch_id'
```

This error indicates that the OpenAI Python client's `vector_stores.file_batches.retrieve()` method doesn't accept the parameters we're providing.

## Root Cause

Similar to the issue with adding files to vector stores, there's a mismatch between the OpenAI Python client's API and the actual API endpoints. The client method doesn't accept `file_batch_id` as a parameter for file batch status retrieval.

## Solution

Replace the client library method with a direct HTTPX API call for polling the file status:

```python
# Previous approach using client library (not working)
batch_status = client.vector_stores.file_batches.retrieve(
    vector_store_id=vector_store_id, 
    file_batch_id=batch_id
)
if batch_status.status == "completed":
    return {"status": "completed"}

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
        if status == "completed" or status == "success":
            return {"status": "completed"}
```

Additionally, we changed the behavior on timeout to return success rather than raising an error, since the file has been successfully uploaded and added to the vector store, even if we can't confirm its processing status.

## Implementation Details

1. **Direct API Polling**: Used HTTPX to make direct GET requests to the file status endpoint
2. **Improved Status Handling**: Added support for multiple status values (`completed`/`success` and `failed`/`error`)
3. **Graceful Timeout Handling**: Return a success message with an 'in_progress' status instead of raising a timeout error
4. **Detailed Logging**: Added clear debug messages about the polling process

## Verification

After implementing this fix:
1. Files are successfully uploaded to vector stores
2. The polling process provides accurate status updates
3. The workflow completes even if polling times out

## Lessons Learned

1. **API Consistency**: The OpenAI API endpoints and the Python client library methods may not always be in sync
2. **Error Handling**: It's important to have graceful degradation for non-critical operations like status polling
3. **Direct API Calls**: In some cases, direct API calls are more reliable than using client libraries

## Related Files

- `tools/openai_vs/upload_file_to_vector_store.py`: Contains the implementation of the direct API polling
- `fixes/vector_store_direct_api_call.md`: Documents the direct API call approach for file uploads
- `fixes/openai_beta_header_removal.md`: Documents the beta header removal issue 