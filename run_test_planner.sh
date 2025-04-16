#!/bin/bash

# Run test for just the planner test files

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

cd "$(dirname "$0")" || { echo -e "${RED}Error: Could not change to script directory${NC}"; exit 1; }

# Export PYTHONPATH to include the current directory
export PYTHONPATH="$PYTHONPATH:$(pwd)"
echo -e "${BLUE}PYTHONPATH set to: $PYTHONPATH${NC}"

echo -e "${YELLOW}Running Chat Planner tests with modified config...${NC}"

# Run just the chat planner handler tests
python -m pytest tests/core/test_chat_planner_handlers.py::TestChatPlannerHandlers::test_plan_user_request_handler_success -v

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}Test passed!${NC}"
    exit 0
else
    echo -e "\n${RED}Test failed!${NC}"
    exit 1
fi 