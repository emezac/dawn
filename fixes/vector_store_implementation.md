# Vector Store Implementation

This document describes the implementation of OpenAI Vector Stores in the Dawn AI Framework, including available tools and usage examples.

## Overview

Vector stores are an essential component for implementing RAG (Retrieval-Augmented Generation) and long-term memory capabilities in AI systems. The Dawn AI Framework provides a suite of tools for creating and managing OpenAI Vector Stores, uploading files and text, and retrieving information from these stores.

## Available Tools

The framework includes the following OpenAI Vector Store tools:

1. **CreateVectorStoreTool** - Creates a new vector store with optional file attachments
   - Accessible via `create_vector_store` in the tool registry
   - Also available via `vector_store_create` alias for backward compatibility
2. **ListVectorStoresTool** - Lists all available vector stores
3. **DeleteVectorStoreTool** - Deletes an existing vector store
4. **UploadFileToVectorStoreTool** - Uploads a file to an existing vector store
5. **SaveTextToVectorStoreTool** - Saves text content to a vector store (useful for long-term memory)
6. **FileReadTool** - Queries vector stores for information retrieval

## Implementation Details

### Tool Structure

Each vector store tool follows a consistent pattern:

1. A dedicated class in the `tools/openai_vs/` directory
2. A handler method in the `ToolRegistry` class to execute the tool
3. Registration in the `ToolRegistry.__init__` method

### Error Handling

The tools implement robust error handling:

1. Input validation before making API calls
2. Try/except blocks to catch API errors
3. Return of structured error information
4. Consistent error reporting through the `ToolRegistry.execute_tool` method

## Usage Examples

### Creating a Vector Store

```python
from core.tools.registry import ToolRegistry

# Initialize the registry
registry = ToolRegistry()

# Create an empty vector store
result = registry.execute_tool("create_vector_store", {
    "name": "My Knowledge Base"
})

if result["success"]:
    vector_store_id = result["result"]
    print(f"Vector store created: {vector_store_id}")
else:
    print(f"Error: {result['error']}")
```

### Creating a Vector Store with Files

```python
# Upload a file first
upload_result = registry.execute_tool("file_upload", {
    "file_path": "path/to/document.pdf",
    "purpose": "assistants"
})

if not upload_result["success"]:
    print(f"Error: {upload_result['error']}")
    exit()

file_id = upload_result["result"]

# Create a vector store with the file
create_result = registry.execute_tool("create_vector_store", {
    "name": "My Knowledge Base",
    "file_ids": [file_id]
})

if create_result["success"]:
    vector_store_id = create_result["result"]
    print(f"Vector store created: {vector_store_id}")
else:
    print(f"Error: {create_result['error']}")
```

### Uploading Files to an Existing Vector Store

```python
# Add a file to an existing vector store
result = registry.execute_tool("upload_file_to_vector_store", {
    "vector_store_id": "vs_abc123",
    "file_path": "path/to/document.pdf"
})

if result["success"]:
    print("File added to vector store")
else:
    print(f"Error: {result['error']}")
```

### Saving Text to a Vector Store (LTM)

```python
# Save text to a vector store (for long-term memory)
result = registry.execute_tool("save_to_ltm", {
    "vector_store_id": "vs_abc123",
    "text_content": "The customer prefers email communication over phone calls."
})

if result["success"]:
    print("Memory saved to vector store")
else:
    print(f"Error: {result['error']}")
```

### Querying a Vector Store

```python
# Query a vector store for information
result = registry.execute_tool("file_read", {
    "vector_store_ids": ["vs_abc123"],
    "query": "What are the main points in the document?",
    "max_num_results": 3,
    "include_search_results": True
})

if result["success"]:
    print(f"Query results: {result['result']}")
else:
    print(f"Error: {result['error']}")
```

### Managing Vector Stores

```python
# List all vector stores
list_result = registry.execute_tool("list_vector_stores", {})

if list_result["success"]:
    for store in list_result["result"]:
        print(f"Vector Store: {store['name']} (ID: {store['id']})")
else:
    print(f"Error: {list_result['error']}")

# Delete a vector store
delete_result = registry.execute_tool("delete_vector_store", {
    "vector_store_id": "vs_abc123"
})

if delete_result["success"]:
    print("Vector store deleted")
else:
    print(f"Error: {delete_result['error']}")
```

## Best Practices

1. Use descriptive names for vector stores to make them easier to identify.
2. Include error handling for all tool calls.
3. Clean up temporary files after uploading them to vector stores.
4. Consider the OpenAI rate limits when making multiple API calls.
5. Use multiple vector stores to organize information (e.g., one for general knowledge, one for long-term memory).

## Example Applications

1. **Context-Aware Legal Review**: Store legal guidelines in a vector store and use them for automated contract review.
2. **Long-Term Memory**: Store conversation history and agent observations in a vector store for future reference.
3. **Knowledge Base**: Store domain-specific information for retrieval during complex tasks.
4. **Document Analysis**: Upload documents for analysis and extract insights using vector search.

## Troubleshooting

Common issues and solutions:

1. **API Key Issues**: Ensure the OPENAI_API_KEY environment variable is properly set.
2. **Rate Limits**: Implement exponential backoff for retries on rate limit errors.
3. **File Size**: OpenAI has a 512MB file size limit per file.
4. **Unsupported File Types**: Check that you're using supported file formats (PDF, DOCX, TXT, etc.).

For detailed implementation examples, refer to the example scripts in the `examples/` directory. 