#!/usr/bin/env python
"""
Test script for context_aware_legal_review_workflow.py
"""  # noqa: D202

import os
import sys
import traceback

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Setting up output directories...")
    os.makedirs("examples/output", exist_ok=True)
    os.makedirs("examples/output/ltm_storage", exist_ok=True)
    
    print("Importing context_aware_legal_review_workflow...")
    from examples.context_aware_legal_review_workflow import main
    
    print("Running the workflow main function...")
    main()
    print("Workflow completed successfully.")
except Exception as e:
    print(f"Error: {str(e)}")
    traceback.print_exc()
    sys.exit(1) 