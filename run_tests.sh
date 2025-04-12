#!/bin/bash

# Run all tests with proper configuration
# This script fixes issues with pytest path configuration

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Initialize test failure tracker
TESTS_FAILED=0

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

# Create output directories for test runs
echo -e "${YELLOW}Setting up output directories...${NC}"
mkdir -p tests/output
mkdir -p tests/recordings

# Run specific test files directly instead of using discovery
echo -e "${YELLOW}Running core tests...${NC}"
/usr/bin/env python3 tests/core/test_direct_handler_task.py | tee "$TEST_OUTPUT_FILE"
if [ ${PIPESTATUS[0]} -ne 0 ]; then
    TESTS_FAILED=1
fi

# Run any other core test files if they exist
if [ -d "tests/core" ]; then
    for test_file in tests/core/test_*.py; do
        if [ -f "$test_file" ] && [ "$test_file" != "tests/core/test_direct_handler_task.py" ]; then
            echo -e "${YELLOW}Running $test_file...${NC}"
            /usr/bin/env python3 "$test_file" | tee -a "$TEST_OUTPUT_FILE"
            if [ ${PIPESTATUS[0]} -ne 0 ]; then
                TESTS_FAILED=1
            fi
        fi
    done
fi

# Run workflow examples tests separately (without discovery)
echo -e "${YELLOW}Running workflow example tests...${NC}"
/usr/bin/env python3 examples/run_workflow_tests.py | tee -a "$TEST_OUTPUT_FILE"
if [ ${PIPESTATUS[0]} -ne 0 ]; then
    TESTS_FAILED=1
fi

# Check if all tests passed
if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed!${NC}"
    echo -e "Detailed results are available in ${BLUE}$TEST_OUTPUT_FILE${NC}"
    exit 0
else
    echo -e "\n${RED}Some tests failed!${NC}"
    echo -e "See ${BLUE}$TEST_OUTPUT_FILE${NC} for details"
    exit 1
fi
