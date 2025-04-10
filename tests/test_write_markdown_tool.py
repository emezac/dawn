import unittest
import os

import sys
import os
# Add parent directory to path to import framework modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.registry import ToolRegistry


class TestWriteMarkdownTool(unittest.TestCase):
    def setUp(self):
        """Set up the tool registry for testing."""
        self.registry = ToolRegistry()
        self.test_file_path = "tests/test_output.md"
        self.test_content = "# Hello, World!\nThis is a test markdown file."

    def tearDown(self):
        """Clean up the temporary file."""
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

    def test_write_markdown(self):
        """Test the Write Markdown tool."""
        input_data = {
            "file_path": self.test_file_path,
            "content": self.test_content
        }
        result = self.registry.execute_tool("write_markdown", input_data)
        self.assertTrue(result["success"], msg=f"Tool execution failed: {result.get('error')}")
        # Verify that the returned result equals the file path
        self.assertEqual(result["result"], self.test_file_path)
        # Verify the file exists and the content is correct
        with open(self.test_file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        self.assertEqual(file_content, self.test_content)

if __name__ == "__main__":
    unittest.main()
