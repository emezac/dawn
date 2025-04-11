"""
Example script demonstrating how to create and use vector stores.
"""

import os
import sys
import tempfile

# Add the project root to the Python path to allow importing from the project modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.registry import ToolRegistry


def main():
    """
    Demonstrate how to create and use an OpenAI Vector Store.
    """
    # Initialize the tool registry
    registry = ToolRegistry()

    # Step 1: Create a sample text file to upload
    print("\n=== Step 1: Creating a sample text file ===")
    sample_text = """
    This is a sample document about artificial intelligence.
    AI systems can process large amounts of data and extract insights.
    Vector stores are useful for storing and retrieving information using semantic similarity.
    """

    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt") as temp_file:
        temp_file.write(sample_text)
        sample_file_path = temp_file.name

    print(f"Created sample file at: {sample_file_path}")

    # Step 2: Upload the file to OpenAI
    print("\n=== Step 2: Uploading the file to OpenAI ===")
    upload_result = registry.execute_tool("file_upload", {"file_path": sample_file_path, "purpose": "assistants"})

    if not upload_result["success"]:
        print(f"Error uploading file: {upload_result['error']}")
        os.remove(sample_file_path)
        return

    file_id = upload_result["result"]
    print(f"File uploaded successfully with ID: {file_id}")

    # Step 3: Create a vector store with the uploaded file
    print("\n=== Step 3: Creating a vector store with the file ===")
    create_result = registry.execute_tool("create_vector_store", {"name": "Sample Vector Store", "file_ids": [file_id]})

    if not create_result["success"]:
        print(f"Error creating vector store: {create_result['error']}")
        os.remove(sample_file_path)
        return

    vector_store_id = create_result["result"]
    print(f"Vector store created successfully with ID: {vector_store_id}")

    # Step 4: Query the vector store
    print("\n=== Step 4: Querying the vector store ===")
    query_result = registry.execute_tool(
        "file_read",
        {
            "vector_store_ids": [vector_store_id],
            "query": "What is artificial intelligence?",
            "max_num_results": 3,
            "include_search_results": True,
        },
    )

    if not query_result["success"]:
        print(f"Error querying vector store: {query_result['error']}")
    else:
        print("Query results:")
        print(query_result["result"])

    # Clean up the sample file
    os.remove(sample_file_path)
    print(f"\nSample file {sample_file_path} removed.")
    print("Example completed.")


if __name__ == "__main__":
    main()
