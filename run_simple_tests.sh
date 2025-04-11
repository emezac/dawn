#!/bin/bash

# Set the PYTHONPATH to include the current directory
export PYTHONPATH="$PYTHONPATH:$(pwd)"
echo "PYTHONPATH set to: $PYTHONPATH"

# Run the specific test we're interested in
echo "Running DirectHandlerTask tests..."
/usr/bin/env python3 -m pytest tests/core/test_direct_handler_task.py -v

# Check if it worked
if [ $? -eq 0 ]; then
    echo "Test passed!"
    exit 0
else
    echo "Test failed, trying different approach..."
    echo "Running python unittest directly..."
    /usr/bin/env python3 tests/core/test_direct_handler_task.py
    exit $?
fi 