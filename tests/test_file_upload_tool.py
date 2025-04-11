import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add parent directory to path to import framework modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.registry import ToolRegistry
from tools.basic_tools import calculate, check_length
# Import the singleton access function
from core.tools.registry_access import get_registry, reset_registry


class TestFileUploadTool(unittest.TestCase):
    def setUp(self):
        """Set up for testing."""
        # Reset the registry before each test
        reset_registry()
        # Get the singleton instance
        self.registry = get_registry()

        # For testing, create a small temporary file.
        self.test_file_path = "tests/test_file.txt"
        with open(self.test_file_path, "w") as f:
            f.write("This is a test file for file upload tool.")

    def tearDown(self):
        """Clean up the temporary file."""
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

    @patch("tools.file_upload_tool.OpenAI")
    def test_file_upload(self, mock_openai):
        """Test the file upload tool."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_file = MagicMock()
        mock_file.id = "file-test123"
        mock_client.files.create.return_value = mock_file
        
        input_data = {"file_path": self.test_file_path, "purpose": "assistants"}
        result = self.registry.execute_tool("file_upload", input_data)
        self.assertTrue(result["success"], msg=f"File upload failed: {result.get('error')}")
        self.assertTrue(result["result"].startswith("file-"), msg="Uploaded file ID does not start with 'file-'")


if __name__ == "__main__":
    unittest.main()
