import os
import sys
import logging

from dotenv import load_dotenv
from openai import OpenAI

# Ensure that the tools directory is added to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.registry import ToolRegistry
# Import the singleton access function
from core.tools.registry_access import get_registry

# Load environment variables from the .env file
load_dotenv()

# Get the singleton registry
registry = get_registry()

# --- Setup ---
logging.basicConfig(level=logging.INFO)

def main():
    # Define the input data for the file upload tool
    input_data = {
        "file_path": os.path.join(os.path.dirname(__file__), "pdfs", "training.pdf"),  # Update with a valid file path
        "purpose": "assistants",
    }

    # Execute the file upload tool
    result = registry.execute_tool("file_upload", input_data)

    # Print the result
    if result["success"]:
        print("File Upload Result:\n", result["result"])
    else:
        print("Error:", result["error"])


if __name__ == "__main__":
    main()
