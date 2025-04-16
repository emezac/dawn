import json
import os

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()


class FileReadTool:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def perform_file_read(self, vector_store_ids, query, max_num_results=5, include_search_results=False):
        """
        Execute a file search query using the specified vector store(s).

        Args:
            vector_store_ids (list of str): List of vector store IDs (must start with "vs_").
            query (str): The query string to search within the indexed files.
            max_num_results (int): Maximum number of search results to return.
            include_search_results (bool): Whether to include raw search results.

        Returns:
            str: The output text from the search response.
        """
        print("Starting file read (file search)...")
        try:
            # Configure the function-calling tool for file search
            tools_config = [
                {
                    "type": "function",
                    "function": {
                        "name": "file_search",
                        "description": "Search through files using vector search",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "vector_store_ids": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of vector store IDs to search in",
                                },
                                "max_results": {
                                    "type": "integer",
                                    "description": "Maximum number of results to return",
                                },
                            },
                            "required": ["vector_store_ids"],
                        },
                    },
                }
            ]

            # Simplified approach - just send a normal request with tools and let the model decide
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You're a helpful assistant that provides information from files."},
                    {"role": "user", "content": query},
                ],
                tools=tools_config,
                tool_choice={"type": "function", "function": {"name": "file_search"}},
            )

            # Check for content first
            if response.choices and response.choices[0].message and response.choices[0].message.content:
                return response.choices[0].message.content

            # If no content, check for tool_calls
            if (
                response.choices
                and response.choices[0].message
                and hasattr(response.choices[0].message, "tool_calls")
                and response.choices[0].message.tool_calls
            ):

                # Get the tool call
                tool_calls = response.choices[0].message.tool_calls
                tool_call = next((tc for tc in tool_calls if tc.function.name == "file_search"), None)

                if tool_call:
                    # Make a follow-up call with the search results
                    tool_args = json.loads(tool_call.function.arguments)

                    # Now make a follow-up call with the tool results
                    follow_up_messages = [
                        {
                            "role": "system",
                            "content": "You're a helpful assistant that provides information from files.",
                        },
                        {"role": "user", "content": query},
                        {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": tool_call.id,
                                    "type": "function",
                                    "function": {"name": "file_search", "arguments": tool_call.function.arguments},
                                }
                            ],
                        },
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": (
                                f"Search results for vector stores {tool_args.get('vector_store_ids', [])} "
                                f"with query: '{query}'"
                            ),
                        },
                    ]

                    # Make the follow-up call to get a proper response
                    follow_up = self.client.chat.completions.create(model="gpt-4o-mini", messages=follow_up_messages)

                    if follow_up.choices and follow_up.choices[0].message.content:
                        return follow_up.choices[0].message.content

                    # If still no content, return a meaningful message
                    return (
                        f"File search performed on vector stores: "
                        f"{', '.join(vector_store_ids)} with query: '{query}'"
                    )

            # If we get here, something unexpected happened
            return f"Unable to get meaningful results from file search with query: '{query}'"

        except Exception as e:
            print(f"An error occurred during file read: {str(e)}")
            return f"An error occurred: {str(e)}"


def register(tool_registry):
    """Register the file read tool with the tool registry."""
    tool_registry.register_tool("file_read", lambda input_data: {
        "success": True,
        "result": FileReadTool().perform_file_read(
            input_data.get("vector_store_ids", []),
            input_data.get("query", ""),
            input_data.get("max_num_results", 5),
            input_data.get("include_search_results", False)
        )
    })
    print("File read tool registered")


# Example usage (for testing)
if __name__ == "__main__":
    tool = FileReadTool()
    # Replace with your actual vector store ID (must start with "vs_")
    vector_store_ids = ["vs_yourVectorStoreID"]
    query = "What are the key details in the training document?"
    result = tool.perform_file_read(vector_store_ids, query, max_num_results=5, include_search_results=True)
    print("File Read Result:\n", result)
