# OpenAI Beta Header Removal

## Issue

When making direct API calls to the OpenAI vector stores API with the `OpenAI-Beta` header, we encountered the following error:

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

This error occurred because we were using a beta feature name (`vector_stores`) that is not recognized by the OpenAI API.

## Root Cause

In our previous fix, we corrected the format of the `OpenAI-Beta` header to be `vector_stores=v1` instead of just `v1`. However, it appears that 'vector_stores' is not a valid beta feature name according to the OpenAI API.

The vector stores API might no longer be in beta, or it might use a different beta feature name than expected.

## Solution

Remove the `OpenAI-Beta` header entirely from the request:

```python
# Previous approach with invalid beta feature name
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "OpenAI-Beta": "vector_stores=v1"  # Invalid beta feature name
}

# New approach without beta header
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
    # No OpenAI-Beta header
}
```

This approach assumes that the vector stores API is now a standard part of the OpenAI API and doesn't require a beta header.

## Implementation Details

1. Removed the `OpenAI-Beta` header from the HTTPX direct API call
2. Kept the rest of the implementation (URL, payload, etc.) the same

## Testing and Validation

After implementing this fix:
1. Direct API calls to add files to vector stores should succeed without beta header errors
2. The save_to_ltm functionality should work correctly
3. The overall workflow should complete without errors related to beta headers

## Lessons Learned

1. **API Versioning**: Beta features in APIs may change over time, including being promoted to standard features
2. **Error Messages**: Always pay attention to error messages, which often provide clear guidance on what's wrong
3. **Minimal Headers**: Start with minimal required headers and add optional ones only if needed

## Related Files

- `tools/openai_vs/upload_file_to_vector_store.py`: Contains the direct API call implementation
- `fixes/openai_beta_header_format.md`: Documents the previous approach with formatted beta header
- `docs/openai_api_parameter_changes.md`: General documentation about API parameter issues and solutions 