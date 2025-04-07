import unittest
from core.tools.registry import ToolRegistry
import os

class TestFileUploadTool(unittest.TestCase):
    def setUp(self):
        """Set up the tool registry for testing."""
        self.registry = ToolRegistry()
        # For testing, create a small temporary file.
        self.test_file_path = "tests/test_file.txt"
        with open(self.test_file_path, "w") as f:
            f.write("This is a test file for file upload tool.")

    def tearDown(self):
        """Clean up the temporary file."""
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

    def test_file_upload(self):
        """Test the file upload tool."""
        input_data = {
            "file_path": self.test_file_path,
            "purpose": "assistants"
        }
        result = self.registry.execute_tool("file_upload", input_data)
        self.assertTrue(result["success"], msg=f"File upload failed: {result.get('error')}")
        self.assertTrue(result["result"].startswith("file-"), msg="Uploaded file ID does not start with 'file-'")

if __name__ == "__main__":
    unittest.main()
