#!/usr/bin/env python
"""
Fix script for context_aware_legal_review_workflow.py
"""  # noqa: D202

import os
import re
import sys

def fix_response_reference():
    """Fix any response references in the extract_task_output function that should be current."""
    filename = "context_aware_legal_review_workflow.py"
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return False
    
    # Read the file
    with open(file_path, "r") as f:
        content = f.read()
    
    # This regex pattern tries to find the line in question within the extract_task_output function
    pattern = r'(if isinstance\(current, str\) and \(current\.strip\(\)\.startswith\("\{".*?or\s)response(\.strip\(\)\.startswith\("\["\)\))'
    
    # Check if we have a match
    match = re.search(pattern, content)
    if match:
        # Fix the reference
        fixed_content = content.replace(
            match.group(0), 
            f'{match.group(1)}current{match.group(2)}'
        )
        
        # Write the fixed content back
        with open(file_path, "w") as f:
            f.write(fixed_content)
            
        print(f"Fixed response reference in {filename}")
        return True
    else:
        print(f"No response reference issues found in {filename}")
        
        # Let's check if there's a specific pattern we can find
        extract_function_pattern = r'def extract_task_output.*?return current'
        extract_function_match = re.search(extract_function_pattern, content, re.DOTALL)
        
        if extract_function_match:
            extract_function = extract_function_match.group(0)
            print("\nExtract function found. Here's the relevant section:")
            
            # Look for any lines that might have issues
            lines = extract_function.split('\n')
            for i, line in enumerate(lines):
                if 'isinstance' in line and 'str' in line and 'strip' in line and 'startswith' in line:
                    print(f"Line {i+1}: {line}")
                if 'response' in line and 'current' in line:
                    print(f"Potential issue - Line {i+1}: {line}")
        
        return False

if __name__ == "__main__":
    print("Starting fix script for context_aware_legal_review_workflow.py")
    fix_response_reference() 