#!/bin/bash

# Run workflow testing examples
# This script runs the workflow testing examples to demonstrate the testing utilities

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running workflow testing examples...${NC}"

# Make sure we're in the project root directory
cd "$(dirname "$0")" || { echo -e "${RED}Error: Could not change to script directory${NC}"; exit 1; }

# Export PYTHONPATH to include the current directory
export PYTHONPATH="$PYTHONPATH:$(pwd)"
echo -e "${BLUE}PYTHONPATH set to: $PYTHONPATH${NC}"

# Create output directories if they don't exist
echo -e "${YELLOW}Setting up output directories...${NC}"
mkdir -p tests/output
mkdir -p tests/recordings

# Define the output file
TEST_OUTPUT_FILE="workflow_test_results.log"

# Make our example script executable if it isn't already
chmod +x examples/run_workflow_tests.py

# Run the workflow examples directly
echo -e "${YELLOW}Running workflow examples...${NC}"
/usr/bin/env python3 examples/run_workflow_tests.py | tee "$TEST_OUTPUT_FILE"

# Check if all tests passed
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}All workflow tests passed!${NC}"
    echo -e "Detailed results are available in ${BLUE}$TEST_OUTPUT_FILE${NC}"
    exit 0
else
    echo -e "\n${RED}Some workflow tests failed!${NC}"
    echo -e "See ${BLUE}$TEST_OUTPUT_FILE${NC} for details"
    exit 1
fi 