#!/bin/bash

# Script to run examples with the correct PYTHONPATH setup

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Make sure we're in the project root directory
cd "$(dirname "$0")" || { echo -e "${RED}Error: Could not change to script directory${NC}"; exit 1; }

# Check if an example was specified
if [ $# -lt 1 ]; then
    echo -e "${RED}Error: No example script specified${NC}"
    echo -e "Usage: ./run_example.sh <example_script_path>"
    echo -e "Example: ./run_example.sh examples/context_aware_legal_review_workflow.py"
    exit 1
fi

EXAMPLE_SCRIPT=$1

# Check if the example script exists
if [ ! -f "$EXAMPLE_SCRIPT" ]; then
    echo -e "${RED}Error: Example script not found: $EXAMPLE_SCRIPT${NC}"
    exit 1
fi

# Export PYTHONPATH to include the current directory
export PYTHONPATH="$PYTHONPATH:$(pwd)"
echo -e "${BLUE}PYTHONPATH set to: $PYTHONPATH${NC}"

# Run the example script and capture both its output and exit code
echo -e "${YELLOW}Running example: $EXAMPLE_SCRIPT${NC}"
python "$EXAMPLE_SCRIPT"
EXAMPLE_EXIT_CODE=$?

# Check if the example ran successfully
if [ $EXAMPLE_EXIT_CODE -eq 0 ]; then
    echo -e "\n${GREEN}Example completed successfully!${NC}"
    exit 0
else
    echo -e "\n${RED}Example failed with exit code $EXAMPLE_EXIT_CODE!${NC}"
    exit $EXAMPLE_EXIT_CODE
fi 