import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add parent directory to path to import framework modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.registry import ToolRegistry


class TestWebSearchTool(unittest.TestCase):
    def setUp(self):
        """Set up the tool registry for testing."""
        self.registry = ToolRegistry()

    @patch("tools.web_search_tool.OpenAI")
    def test_web_search(self, mock_openai):
        """Test the web search tool."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = "Today, scientists announced a breakthrough in renewable energy technology, " \
                       "celebrating a major success in the fight against climate change."
        
        # Define the input data for the web search tool
        input_data = {
            "query": "What was a positive news story from today?",
            "context_size": "medium",
            "user_location": {
                "type": "approximate",
                "country": "US",
                "city": "New York",
                "region": "NY",
            },
        }

        with patch("tools.web_search_tool.WebSearchTool.perform_search", return_value=mock_response):
            # Execute the web search tool
            result = self.registry.execute_tool("web_search", input_data)

            # Assert the result
            self.assertTrue(result["success"], msg=f"Error: {result.get('error', 'Unknown error')}")
            
            # Modified positive indicators to be more flexible.
            positive_indicators = [
                "uplifting",
                "positive",
                "good news",
                "celebrat",
                "success",
                "achievement",
            ]
            content = result["result"].lower()
            self.assertTrue(
                any(indicator in content for indicator in positive_indicators),
                msg="No positive indicators found in the result.",
            )


if __name__ == "__main__":
    unittest.main()
