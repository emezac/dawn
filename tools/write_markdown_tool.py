import os


class WriteMarkdownTool:
    def write_markdown_file(self, file_path: str, content: str) -> str:
        """
        Write content to a Markdown file at the specified file_path.
        If the parent directory doesn't exist, create it.

        Args:
            file_path (str): The path where the Markdown file should be written.
            content (str): The Markdown content to write.

        Returns:
            str: The file path on success, or an error message.
        """
        try:
            dir_name = os.path.dirname(file_path)
            if not os.path.exists(dir_name):
                os.makedirs(dir_name, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return file_path
        except Exception as e:
            return f"Error: {str(e)}"
