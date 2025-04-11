#!/bin/bash

# Run all vector store ID validation tests

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Change to project root
cd "$PROJECT_ROOT" || { echo -e "${RED}Error: Could not change to project root directory${NC}"; exit 1; }

echo -e "${YELLOW}Running Vector Store ID validation tests...${NC}"

# Run tests
echo -e "\n${YELLOW}Running main validation test suite...${NC}"
python -m tests.test_vector_store_id_validation
RESULT1=$?

echo -e "\n${YELLOW}Running utility validation tests...${NC}"
python -m tests.openai_vs.test_vs_id_validator
RESULT2=$?

echo -e "\n${YELLOW}Running integration tests...${NC}"
python -m tests.openai_vs.test_vs_id_integration
RESULT3=$?

# Check if all tests passed
if [ $RESULT1 -eq 0 ] && [ $RESULT2 -eq 0 ] && [ $RESULT3 -eq 0 ]; then
    echo -e "\n${GREEN}All vector store validation tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}Some tests failed!${NC}"
    exit 1
fi 