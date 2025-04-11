#!/bin/bash

# Run all tests with proper configuration
# This script fixes issues with pytest path configuration

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running tests for the dawn project...${NC}"

# Make sure we're in the project root directory
cd "$(dirname "$0")" || { echo -e "${RED}Error: Could not change to script directory${NC}"; exit 1; }

# Export PYTHONPATH to include the current directory
export PYTHONPATH="$PYTHONPATH:$(pwd)"
echo -e "${BLUE}PYTHONPATH set to: $PYTHONPATH${NC}"

# Clean up any cached files to avoid stale test results
echo -e "${YELLOW}Cleaning up pytest cache...${NC}"
find . -name "*.pyc" -delete
find . -name "__pycache__" -exec rm -rf {} +
find . -name ".pytest_cache" -exec rm -rf {} +

# Define the output file
TEST_OUTPUT_FILE="test_results.log"

# Run the tests and save output to a file
echo -e "${YELLOW}Running tests with pytest...${NC}"
python -m pytest -v | tee "$TEST_OUTPUT_FILE"

# Check if all tests passed
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed!${NC}"
    echo -e "Detailed results are available in ${BLUE}$TEST_OUTPUT_FILE${NC}"
    exit 0
else
    echo -e "\n${RED}Some tests failed!${NC}"
    echo -e "See ${BLUE}$TEST_OUTPUT_FILE${NC} for details"
    exit 1
fi 