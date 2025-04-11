# Vector Store File Parameter Error

## Issue

When adding files to a vector store using the OpenAI API, the following error occurs:

```
TypeError when adding file to vector store: Files.create() got an unexpected keyword argument 'file_ids'. Check file_id format: file-...
```

This error happens in the `upload_and_add_file_to_vector_store` method in `tools/openai_vs/upload_file_to_vector_store.py` when trying to add a file to a vector store. The OpenAI API is rejecting the `file_ids` parameter.

## Root Cause

The OpenAI API client expects a different parameter name for adding files to a vector store. The current implementation uses:

```python
file_batch = self.client.vector_stores.files.create(
    vector_store_id=vector_store_id, 
    file_ids=[file_id]  # This parameter name is incorrect
)
```

But the API expects `files` instead of `file_ids`.

## Solution

Update the API call to use the correct parameter name:

```python
file_batch = self.client.vector_stores.files.create(
    vector_store_id=vector_store_id, 
    files=[file_id]  # Use 'files' instead of 'file_ids'
)
```

Additionally, we implemented a fallback mechanism that tries both parameter names in case the API changes again in the future:

```python
try:
    file_batch = self.client.vector_stores.files.create(
        vector_store_id=vector_store_id, 
        file_ids=[file_id]  # Try the original parameter first
    )
except TypeError as te:
    if "file_ids" in str(te):
        # If that fails with a specific error about file_ids, try the alternative
        file_batch = self.client.vector_stores.files.create(
            vector_store_id=vector_store_id,
            files=[file_id]  # Try 'files' instead
        )
```

## Implementation Details

1. Modified the `upload_and_add_file_to_vector_store` method to attempt the API call with the correct parameter name if the original call fails.
2. Added detailed error handling to provide more information about failures.
3. Added debugging output to track which method succeeded.

## Verification

After making the change, we verified that:
1. Files can be successfully uploaded to vector stores.
2. The context-aware legal review workflow completes successfully.
3. The save-to-LTM functionality works correctly.

## Related Files

- `tools/openai_vs/upload_file_to_vector_store.py`: Contains the file upload and vector store integration logic.
- `tools/openai_vs/save_text_to_vector_store.py`: Uses the upload functionality to save text to vector stores.
- `examples/context_aware_legal_review_workflow.py`: Example workflow that uses the vector store functionality. 