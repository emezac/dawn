#!/bin/bash

# Run tests while skipping files that require PyYAML
# This is a temporary solution until PyYAML is properly installed

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

# Tests that are known to work without PyYAML
echo -e "${YELLOW}Running tests that don't require PyYAML...${NC}"

WORKING_TESTS=(
    "tests/core/test_direct_handler_task.py"
    "tests/core/test_data_validator.py"
    "tests/core/test_direct_handler_task_new.py"
    "tests/core/test_errors.py"
    "tests/core/test_plugin_system.py"
    "tests/core/test_registry_access.py"
    "tests/core/test_standardized_output.py"
    "tests/core/test_task_output.py"
    "tests/core/test_variable_resolver.py"
    "tests/core/test_variable_resolver_simple.py"
)

# Run each working test
for test_file in "${WORKING_TESTS[@]}"; do
    echo -e "${YELLOW}Running $test_file...${NC}"
    python -m pytest "$test_file" -v | tee -a "$TEST_OUTPUT_FILE"
    if [ ${PIPESTATUS[0]} -ne 0 ]; then
        TESTS_FAILED=1
    fi
done

# Run workflow examples tests
echo -e "${YELLOW}Running workflow example tests...${NC}"
python -m pytest examples/tests/ -v | tee -a "$TEST_OUTPUT_FILE"
if [ ${PIPESTATUS[0]} -ne 0 ]; then
    TESTS_FAILED=1
fi

# List skipped tests
SKIPPED_TESTS=(
    "tests/core/test_chat_planner_handlers.py"
    "tests/core/test_execute_dynamic_tasks.py"
    "tests/core/test_plan_validation.py"
)

echo -e "\n${YELLOW}The following tests were skipped (require PyYAML):${NC}"
for test_file in "${SKIPPED_TESTS[@]}"; do
    echo "  - $test_file"
done

# Check if all tests passed
if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}All enabled tests passed!${NC}"
    echo -e "Detailed results are available in ${BLUE}$TEST_OUTPUT_FILE${NC}"
    exit 0
else
    echo -e "\n${RED}Some tests failed!${NC}"
    echo -e "See ${BLUE}$TEST_OUTPUT_FILE${NC} for details"
    exit 1
fi 