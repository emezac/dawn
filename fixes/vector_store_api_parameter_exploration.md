# Vector Store API Parameter Exploration

## Issue

When attempting to add files to a vector store using the OpenAI API, we encountered the following errors:

```
Debug - TypeError when adding file to vector store: Files.create() got an unexpected keyword argument 'file_ids'.
Debug - Attempting alternative API call format
Debug - Alternative API call also failed: Files.create() got an unexpected keyword argument 'files'
```

This suggests that the OpenAI API doesn't accept either `file_ids` or `files` parameters for the `vector_stores.files.create()` method.

## Root Cause

The OpenAI API has changed, and the documentation may not accurately reflect the current parameter names for adding files to vector stores. Both attempted parameter names (`file_ids` and `files`) are rejected by the API.

## Solution Approach

We implemented an exploratory approach to determine the correct parameter name:

1. **Try direct `file_id` parameter:**
   ```python
   file_batch = client.vector_stores.files.create(
       vector_store_id=vector_store_id, 
       file_id=file_id  # Try with single file_id parameter
   )
   ```

2. **Try array format for `file_id`:**
   ```python
   file_batch = client.vector_stores.files.create(
       vector_store_id=vector_store_id,
       file_id=[file_id]  # Try array format for file_id
   )
   ```

3. **Inspect the API client:**
   ```python
   import inspect
   print(f"Available methods: {dir(client.vector_stores.files)}")
   print(f"Create method spec: {inspect.signature(client.vector_stores.files.create)}")
   ```

4. **Try positional arguments:**
   ```python
   file_batch = client.vector_stores.files.create(
       vector_store_id, file_id  # Try positional arguments
   )
   ```

## Implementation Details

1. Added multiple approaches to try different parameter formats
2. Enhanced error handling to capture and report on all attempted approaches
3. Added debug logging to display information about the API client's structure
4. Added inspection of the available methods and their signatures

## Expected Outcomes

1. **Best Case:** One of the approaches works, and we identify the correct parameter format
2. **Fallback:** The debug information provides insights into the correct API usage
3. **Documentation:** We document findings for future reference

## Related Files

- `tools/openai_vs/upload_file_to_vector_store.py`: Contains the implementation of file uploads to vector stores
- `docs/openai_api_parameter_changes.md`: Documentation about API parameter changes
- `fixes/vector_store_file_parameter_error.md`: Previous fix document for parameter issues 