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
    # Define the input data for the web search tool
    input_data = {
        "query": "What are the latest advancements in AI technology?",
        "context_size": "medium",
        "user_location": {
            "type": "approximate",
            "country": "US",
            "city": "San Francisco",
            "region": "CA",
        },
    }

    # Execute the web search tool
    result = registry.execute_tool("web_search", input_data)

    # Print the result
    if result["success"]:
        print("Web Search Result:\n", result["result"])
    else:
        print("Error:", result["error"])


if __name__ == "__main__":
    main()
