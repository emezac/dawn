import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

# Ensure that the tools directory is added to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.registry import ToolRegistry

# Load environment variables from the .env file
load_dotenv()

def main():
    # Initialize the tool registry
    registry = ToolRegistry()
    
    # Define the input data for the file upload tool
    input_data = {
        "file_path": os.path.join(os.path.dirname(__file__), 'pdfs', 'training.pdf'),  # Update with a valid file path
        "purpose": "assistants"
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