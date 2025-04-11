"""
Basic example demonstrating the core error handling functionality in Dawn framework.
"""

import os
import sys
import logging
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.errors import (
    ErrorCode,
    create_error_response,
    create_success_response,
    create_warning_response
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """
    Test the basic error handling functions.
    """
    logger.info("Testing basic error handling...")
    
    # Test success response
    success_response = create_success_response(
        result={"value": 42},
        message="Operation completed successfully",
        metadata={"operation": "test"}
    )
    logger.info(f"Success response: {success_response}")
    
    # Test error response
    error_response = create_error_response(
        message="Something went wrong",
        error_code=ErrorCode.EXECUTION_TOOL_FAILED,
        details={"source": "test"}
    )
    logger.info(f"Error response: {error_response}")
    
    # Test warning response
    warning_response = create_warning_response(
        result={"partial_data": [1, 2, 3]},
        warning="Partial data returned",
        warning_code="PARTIAL_RESULTS",
        details={"expected": 5, "received": 3}
    )
    logger.info(f"Warning response: {warning_response}")
    
    logger.info("All tests completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 