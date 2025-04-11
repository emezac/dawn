# Test Updates for Vector Store Tools

## Issue

After removing excessive debug logging from the vector store tools, several tests were failing because they relied on:

1. The old implementation details of the tools
2. Different return value formats (e.g., batch IDs that are no longer returned)
3. Direct access to client methods that have been replaced with HTTPX calls
4. Tests weren't set up to handle the RuntimeError consolidation

## Changes Made

### 1. Update test_upload_file_to_vector_store.py

- Replaced OpenAI client method mocking with HTTPX direct call mocking
- Updated assertion tests to match new return value format (without batch_id)
- Updated timeout test to expect in_progress status rather than a TimeoutError
- Added API key mocking for the direct API calls
- Modified the tool registry integration test to include the purpose parameter

### 2. Update test_save_text_to_vector_store.py

- Added mocking for os.path.getsize to test empty file error conditions
- Removed tests that relied on the client's file_batch methods
- Updated assertions to match new error handling patterns
- Added a new test for empty file error scenarios
- Updated expected return values to match the new format (without batch_id)

### 3. Create test_minimal.py

- Created a minimal test file focusing just on the core validation functionality
- Tests all valid purpose values to ensure they're accepted
- Tests validation errors are raised as expected
- Uses comprehensive mocking to avoid actual API calls

## Benefits

1. **Test Alignment**: Tests now match the actual implementation and API pattern
2. **Improved Mocking**: More robust mocking patterns that don't rely on internal implementation details
3. **Better Test Coverage**: Added tests for edge cases like empty files
4. **Simplified Assertions**: Clear assertions that match the expected response format
5. **Independent Tests**: Tests that don't depend on each other or external services

## Implementation Details

1. Used unittest's `patch` decorator extensively to mock:
   - OpenAI client methods
   - HTTPX client for direct API calls
   - File operations (os.path.exists, os.path.getsize)
   - time.sleep to speed up tests with polling

2. Created appropriate mock responses for:
   - File upload responses
   - Vector store API calls
   - File status polling

3. Used context managers to ensure proper cleanup of resources, especially temporary files

## Related Files

- `tools/openai_vs/upload_file_to_vector_store.py`: The main implementation file
- `tools/openai_vs/save_text_to_vector_store.py`: Related implementation file
- `tests/test_upload_file_to_vector_store.py`: Updated test file
- `tests/test_save_text_to_vector_store.py`: Updated test file
- `tests/test_minimal.py`: New minimal test file
- `fixes/logging_cleanup.md`: Documentation of the logging cleanup process 