# Vector Store Purpose Parameter Error

## Issue

When saving text to a vector store using `upload_and_add_file_to_vector_store`, the following error occurs:

```
Error in upload_and_add_file_to_vector_store (BadRequestError): Error code: 400 - {'error': {'message': "'vector_store' is not one of ['fine-tune', 'assistants', 'batch', 'user_data', 'vision', 'evals'] - 'purpose'", 'type': 'invalid_request_error', 'param': 'purpose', 'code': None}}
```

The OpenAI API is reporting that `'vector_store'` is not a valid value for the `purpose` parameter when uploading a file. The allowed values are:
- 'fine-tune'
- 'assistants'
- 'batch'
- 'user_data'
- 'vision'
- 'evals'

## Solution

Update the `upload_and_add_file_to_vector_store` method in `tools/openai_vs/upload_file_to_vector_store.py` to use 'assistants' as the purpose parameter value instead of 'vector_store'. The file will still be used for the vector store, but the upload purpose needs to be one of the allowed values.

```python
# Before:
upload_response = self.client.files.create(
    file=file_obj,
    purpose="vector_store"  # Invalid purpose
)

# After:
upload_response = self.client.files.create(
    file=file_obj,
    purpose="assistants"  # Valid purpose
)
```

## Implementation Details

1. Updated the upload_file_to_vector_store.py file to use 'assistants' as the purpose.
2. Made the purpose configurable with a default of 'assistants'.
3. Added this to the documentation to prevent future issues.

## Verification

After making the change, we verified that:
1. The file upload works correctly.
2. The uploaded file can be successfully added to a vector store.
3. The vector store ID validation works as expected.

## Related Changes

Also updated the vector_store_example.py file and any other examples that might be affected by this change to ensure they use the correct purpose parameter value. 