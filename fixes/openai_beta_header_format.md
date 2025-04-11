# OpenAI Beta Header Format Error

## Issue

When making direct API calls to the OpenAI vector stores API, we encountered the following error:

```json
{
  "error": {
    "message": "Invalid beta header provided: 'v1'. The header should be in the format 'OpenAI-Beta: example_beta=v1'.",
    "type": "invalid_request_error",
    "param": null,
    "code": "invalid_beta"
  }
}
```

This error occurred because we were using an incorrect format for the `OpenAI-Beta` header in our direct API calls via HTTPX.

## Root Cause

When making API calls to beta OpenAI endpoints, the `OpenAI-Beta` header must include both the beta feature name and the version in the format `feature_name=vX`. We were incorrectly sending just the version number `v1`.

## Solution

Update the header format to include the specific beta feature name:

```python
# Incorrect header format
headers = {
    "OpenAI-Beta": "v1"  # Missing the feature name
}

# Correct header format
headers = {
    "OpenAI-Beta": "vector_stores=v1"  # Includes the feature name and version
}
```

This matches the required format described in the error message: `OpenAI-Beta: example_beta=v1`.

## Implementation Details

1. Changed the `OpenAI-Beta` header value in the HTTPX direct API call
2. Used `vector_stores=v1` as the value to specify the vector stores beta feature and its version

## Testing and Validation

After implementing this fix:
1. The direct API calls to add files to vector stores succeeded
2. The save_to_ltm functionality worked correctly
3. The overall workflow completed without errors related to beta headers

## Lessons Learned

1. **Read Error Messages Carefully**: The error message provided the exact format required for the header
2. **API Documentation**: When working with beta features, refer to the API documentation for the correct header format
3. **Beta Feature Naming**: Different beta features may have different names that need to be specified in the header

## Related Files

- `tools/openai_vs/upload_file_to_vector_store.py`: Contains the direct API call implementation
- `fixes/vector_store_direct_api_call.md`: Documents the direct API call approach
- `docs/openai_api_parameter_changes.md`: General documentation about API parameter issues and solutions 