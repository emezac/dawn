import os
import sys
import logging
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.registry import ToolRegistry
from core.tools.registry_access import get_registry

# --- Setup ---
logging.basicConfig(level=logging.INFO)
load_dotenv()

# Get the singleton registry
registry = get_registry()

def main():
    # Initialize the tool registry
    registry = ToolRegistry()

    # --- File Upload Example ---
    upload_input = {
        "file_path": os.path.join(os.path.dirname(__file__), "pdfs", "training.pdf"),
        "purpose": "assistants",
    }
    upload_result = registry.execute_tool("file_upload", upload_input)
    print("File Upload Result:")
    print(upload_result)

    # --- File Read (RAG) Example ---
    # NOTE: For file read, you must have a vector store already created and indexed with your file(s).
    # Replace the vector_store_id below with your actual vector store ID (format "vs_*").
    vector_store_id = "vs_yourVectorStoreID"
    read_input = {
        "vector_store_ids": [vector_store_id],
        "query": "What are the key details in the training document?",
        "max_num_results": 5,
        "include_search_results": True,
    }
    read_result = registry.execute_tool("file_read", read_input)
    print("File Read (RAG) Result:")
    print(read_result)


if __name__ == "__main__":
    main()
