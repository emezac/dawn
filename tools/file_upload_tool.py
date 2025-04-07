from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class FileUploadTool:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def upload_file(self, file_path, purpose='assistants'):
        """
        Upload a file using the OpenAI API and return the file ID.
        
        Args:
            file_path (str): Path to the file to upload.
            purpose (str): The purpose for the file upload. Defaults to 'assistants'.
            
        Returns:
            str: The uploaded file's ID (e.g., "file-xxx") or an error message.
        """
        print("Starting file upload...")
        try:
            with open(file_path, 'rb') as file:
                response = self.client.files.create(file=file, purpose=purpose)
                print("Received response:", response)
                return response.id
        except Exception as e:
            print(f"An error occurred during file upload: {str(e)}")
            return f"An error occurred: {str(e)}"

# Example usage (can be run directly for testing)
if __name__ == "__main__":
    tool = FileUploadTool()
    test_path = "path/to/your/file.pdf"  # Replace with an actual file path
    file_id = tool.upload_file(test_path)
    print("Uploaded file ID:", file_id)
