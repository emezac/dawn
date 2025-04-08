import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.registry import ToolRegistry

def main():
    # Initialize the tool registry
    registry = ToolRegistry()
    
    # --- Step 1: File Upload ---
    upload_input = {
        "file_path": os.path.join(os.path.dirname(__file__), "pdfs", "training.pdf"),
        "purpose": "assistants"
    }
    upload_result = registry.execute_tool("file_upload", upload_input)
    print("File Upload Result:")
    print(upload_result)
    
    if not upload_result["success"]:
        print("File upload failed; cannot continue.")
        return
    file_id = upload_result["result"]
    
    # --- Step 2: Create Vector Store ---
    # Create a vector store with the uploaded file.
    vector_store_create_input = {
        "name": "Training Documents Store",
        "file_ids": [file_id]
    }
    vector_store_result = registry.execute_tool("vector_store_create", vector_store_create_input)
    print("Vector Store Creation Result:")
    print(vector_store_result)
    
    if not vector_store_result["success"]:
        print("Vector store creation failed; cannot continue.")
        return
    vector_store_id = vector_store_result["result"]
    
    # --- Step 3: File Read (RAG) ---
    # NOTE: The file read tool (file_search) uses the vector store ID, which must start with "vs_".
    file_read_input = {
        "vector_store_ids": [vector_store_id],
        "query": "What are the key details in the training document?",
        "max_num_results": 5,
        "include_search_results": True
    }
    file_read_result = registry.execute_tool("file_read", file_read_input)
    print("File Read (RAG) Result:")
    print(file_read_result)

if __name__ == "__main__":
    main()
