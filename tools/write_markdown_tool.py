import os


class WriteMarkdownTool:
    """
    Tool for writing markdown content to files.
    """

    def write_markdown_file(self, file_path: str, content: str) -> str:
        """
        Write content to a Markdown file at the specified file_path.
        If the parent directory doesn't exist, create it.

        Args:
            file_path (str): The path where the Markdown file should be written.
            content (str): The Markdown content to write.

        Returns:
            str: The absolute file path of the written file.

        Raises:
            ValueError: If file_path is empty or not a string.
            OSError: If there's an issue creating directories or writing the file.
            TypeError: If content is not a string.
        """
        # Input validation
        if not file_path or not isinstance(file_path, str):
            raise ValueError("File path must be a non-empty string")

        if not isinstance(content, str):
            raise TypeError("Content must be a string")

        # Create directory if it doesn't exist
        dir_name = os.path.dirname(file_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

        # Write content to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Return absolute path for consistency
        return os.path.abspath(file_path)
