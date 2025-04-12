#!/bin/bash

# Run a specific test and save output to a file

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running specific test with output capture...${NC}"

# Make sure we're in the project root directory
cd "$(dirname "$0")" || { echo -e "${RED}Error: Could not change to script directory${NC}"; exit 1; }

# Export PYTHONPATH to include the current directory
export PYTHONPATH="$PYTHONPATH:$(pwd)"
echo -e "${BLUE}PYTHONPATH set to: $PYTHONPATH${NC}"

# Define the output file
TEST_OUTPUT_FILE="specific_test_results.log"

# Run the workflow example tests
echo -e "${YELLOW}Running workflow example tests...${NC}"
python tests/workflows/examples/test_workflow_examples.py -v > "$TEST_OUTPUT_FILE" 2>&1

# Check the exit code
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}Test passed!${NC}"
else
    echo -e "\n${RED}Test failed!${NC}"
fi

echo -e "Detailed results are available in ${BLUE}$TEST_OUTPUT_FILE${NC}"

# Show the first few lines of the output
echo -e "\n${YELLOW}Showing the first few lines of test output:${NC}"
head -n 20 "$TEST_OUTPUT_FILE"

# Show the last few lines of the output
echo -e "\n${YELLOW}Showing the last few lines of test output:${NC}"
tail -n 20 "$TEST_OUTPUT_FILE" 