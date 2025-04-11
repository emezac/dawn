import os
import sys
import tempfile
from unittest.mock import mock_open, patch

import pytest

# Add parent directory to path to import framework modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.write_markdown_tool import WriteMarkdownTool


class TestWriteMarkdownTool:
    """Test suite for the WriteMarkdownTool."""

    @pytest.fixture
    def tool(self):
        """Fixture to create an instance of the WriteMarkdownTool."""
        return WriteMarkdownTool()

    def test_write_markdown_file_success(self, tool):
        """Test successful writing of a markdown file."""
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Define test file path and content
            test_file_path = os.path.join(temp_dir, "test.md")
            test_content = "# Test Markdown\n\nThis is a test."

            # Write the file
            result = tool.write_markdown_file(test_file_path, test_content)

            # Verify the result is the absolute path
            assert result == os.path.abspath(test_file_path)

            # Verify the file was created with the correct content
            assert os.path.exists(test_file_path)
            with open(test_file_path, "r", encoding="utf-8") as f:
                assert f.read() == test_content

    def test_write_markdown_file_subdirectory(self, tool):
        """Test writing to a subdirectory that doesn't exist yet."""
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Define test file path in a non-existent subdirectory
            subdir = os.path.join(temp_dir, "subdir")
            test_file_path = os.path.join(subdir, "test.md")
            test_content = "# Test in Subdirectory"

            # Write the file
            result = tool.write_markdown_file(test_file_path, test_content)

            # Verify the result is the absolute path
            assert result == os.path.abspath(test_file_path)

            # Verify the subdirectory and file were created
            assert os.path.exists(subdir)
            assert os.path.exists(test_file_path)
            with open(test_file_path, "r", encoding="utf-8") as f:
                assert f.read() == test_content

    def test_write_markdown_file_invalid_path(self, tool):
        """Test handling of invalid file paths."""
        invalid_paths = ["", None, 123, []]

        for path in invalid_paths:
            with pytest.raises(ValueError):
                tool.write_markdown_file(path, "test content")

    def test_write_markdown_file_invalid_content(self, tool):
        """Test handling of invalid content."""
        invalid_contents = [None, 123, [], {}]

        for content in invalid_contents:
            with pytest.raises(TypeError):
                tool.write_markdown_file("test.md", content)

    @patch("os.makedirs")
    def test_write_markdown_file_permission_error(self, mock_makedirs, tool):
        """Test handling of permission errors."""
        mock_makedirs.side_effect = PermissionError("Permission denied")

        with pytest.raises(PermissionError):
            tool.write_markdown_file("/forbidden/test.md", "test content")

    @patch("builtins.open")
    def test_write_markdown_file_io_error(self, mock_open_func, tool):
        """Test handling of I/O errors."""
        mock_open_func.side_effect = IOError("I/O error")

        with pytest.raises(IOError):
            tool.write_markdown_file("test.md", "test content")


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
