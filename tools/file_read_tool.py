from openai import OpenAI
import os
from dotenv import load_dotenv

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
            tools_config = [{
                "type": "file_search",
                "vector_store_ids": vector_store_ids,
                "max_num_results": max_num_results
            }]
            include_param = ["file_search_call.results"] if include_search_results else []
            response = self.client.responses.create(
                model="gpt-4o-mini",
                input=query,
                tools=tools_config,
                include=include_param
            )
            # Extract the output text from the response
            output_message = next((output for output in response.output if output.type == 'message'), None)
            if output_message:
                output_text = next((content.text for content in output_message.content if content.type == 'output_text'), None)
                return output_text.strip() if output_text else "No output text found"
            return "No output text found"
        except Exception as e:
            print(f"An error occurred during file read: {str(e)}")
            return f"An error occurred: {str(e)}"

# Example usage (for testing)
if __name__ == "__main__":
    tool = FileReadTool()
    # Replace with your actual vector store ID (must start with "vs_")
    vector_store_ids = ["vs_yourVectorStoreID"]
    query = "What are the key details in the training document?"
    result = tool.perform_file_read(vector_store_ids, query, max_num_results=5, include_search_results=True)
    print("File Read Result:\n", result)
