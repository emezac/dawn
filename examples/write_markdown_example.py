import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.registry import ToolRegistry

def main():
    # Initialize the tool registry
    registry = ToolRegistry()
    
    # Define the input for the Write Markdown tool
    input_data = {
        "file_path": os.path.join(os.path.dirname(__file__), "output.md"),
        "content": "# Example Markdown\n\nThis is an example markdown file created by the Write Markdown Tool."
    }
    
    # Execute the Write Markdown tool
    result = registry.execute_tool("write_markdown", input_data)
    
    if result["success"]:
        print("Markdown file written successfully. File path:")
        print(result["result"])
    else:
        print("Error writing markdown file:", result["error"])

if __name__ == "__main__":
    main()
