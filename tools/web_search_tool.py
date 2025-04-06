from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class WebSearchTool:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def perform_search(self, query, context_size="medium", user_location=None):
        """Perform a web search using the OpenAI API."""
        print("Starting web search...")
        tools_config = [{"type": "web_search_preview", "search_context_size": context_size}]
        
        if user_location:
            tools_config[0]["user_location"] = user_location

        try:
            response = self.client.responses.create(
                model="gpt-4o",
                tools=tools_config,
                input=query
            )
            print("Received response:", response)
            # Extract the text from the response
            output_message = next((output for output in response.output if output.type == 'message'), None)
            if output_message:
                output_text = next((content.text for content in output_message.content if content.type == 'output_text'), None)
                return output_text.strip() if output_text else "No output text found"
            
            return "No output text found"
        
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return f"An error occurred: {str(e)}"

# Example usage
if __name__ == "__main__":
    web_search_tool = WebSearchTool()
    result = web_search_tool.perform_search("What was a positive news story from today?")
    print(result) 