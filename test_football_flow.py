#!/usr/bin/env python3
"""
Test script for football match analysis handlers
"""  # noqa: D202

import os
import logging
from datetime import datetime
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_football_flow")

# Add parent directory to path to find modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    # Import handlers from the football_match_analysis_flow.py
    from examples.football_match_analysis_flow import (
        get_user_input_handler,
        search_team_form_handler,
        search_head_to_head_handler
    )
except ImportError as e:
    logger.error(f"Error importing handlers: {e}")
    sys.exit(1)

def main():
    """Test the handlers directly"""
    # Create a mock task object with required attributes
    mock_task = type('MockTask', (), {
        'id': 'test_task',
        'name': 'Test Task',
        'status': 'running',
        'input_data': {},
        'output_data': {},
        'set_output': lambda self, data: setattr(self, 'output_data', data)
    })()
    
    # Test input data
    test_input = {
        "home_team": "Barcelona",
        "away_team": "Real Madrid",
        "match_date": datetime.now().strftime("%Y-%m-%d"),
        "league": "La Liga",
        "analysis_depth": "comprehensive"
    }
    
    # Test get_user_input_handler
    logger.info("Testing get_user_input_handler...")
    result = get_user_input_handler(mock_task, test_input)
    logger.info(f"get_user_input_handler result: {result}")
    
    # Test search_team_form_handler
    logger.info("Testing search_team_form_handler...")
    result = search_team_form_handler(mock_task, test_input)
    logger.info(f"search_team_form_handler result: {result}")
    
    # Test search_head_to_head_handler
    logger.info("Testing search_head_to_head_handler...")
    result = search_head_to_head_handler(mock_task, test_input)
    logger.info(f"search_head_to_head_handler result: {result}")
    
    logger.info("All tests completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 