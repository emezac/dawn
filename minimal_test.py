#!/usr/bin/env python3
"""
Minimal test for variable substitution in execute_dynamic_tasks_handler.
"""  # noqa: D202

import re
from unittest.mock import MagicMock

def test_variable_substitution():
    """Test variable substitution logic from execute_dynamic_tasks_handler."""
    print("Testing variable substitution...")
    
    # Mock data
    task_id = "test_task"
    input_data = {
        "user_prompt": "Test user prompt",
        "tasks": []
    }
    all_step_outputs = {
        "previous_task": {
            "success": True,
            "result": {
                "value": "test result",
                "nested": {
                    "deep": "nested value"
                }
            }
        }
    }
    
    # Variable pattern to match ${...}
    var_pattern = re.compile(r'\${(.*?)}')
    
    # Test cases
    test_cases = [
        {
            "desc": "Simple user prompt reference",
            "input": "${user_prompt}",
            "expected": "Test user prompt"
        },
        {
            "desc": "Task output reference",
            "input": "${previous_task.output.result.value}",
            "expected": "test result"
        },
        {
            "desc": "Nested task output reference",
            "input": "${previous_task.output.result.nested.deep}",
            "expected": "nested value"
        },
        {
            "desc": "Non-existent task reference",
            "input": "${nonexistent_task.output.result}",
            "expected": None
        },
        {
            "desc": "Invalid path reference",
            "input": "${previous_task.output.result.nonexistent}",
            "expected": None
        },
        {
            "desc": "Non-variable string",
            "input": "Just a regular string",
            "expected": "Just a regular string"
        }
    ]
    
    # Run tests
    for test_case in test_cases:
        print(f"\nTest: {test_case['desc']}")
        value = test_case["input"]
        expected = test_case["expected"]
        
        resolved_value = value  # Default to original value
        
        if isinstance(value, str):
            match = var_pattern.fullmatch(value)
            if match:
                var_name = match.group(1)
                print(f"Found variable: {var_name}")
                
                # Check for user_prompt
                if var_name == "user_prompt":
                    resolved_value = input_data.get("user_prompt", "")
                    print(f"Resolved to user_prompt: {resolved_value}")
                
                # Check for task output reference
                elif '.output.' in var_name:
                    try:
                        parts = var_name.split('.output.', 1)
                        source_task_id = parts[0]
                        field_path = parts[1]
                        print(f"Task: {source_task_id}, Path: {field_path}")
                        
                        if source_task_id in all_step_outputs:
                            source_output_dict = all_step_outputs[source_task_id]
                            # Navigate the dictionary using the field path
                            current_val = source_output_dict
                            path_valid = True
                            
                            for field in field_path.split('.'):
                                if isinstance(current_val, dict):
                                    current_val = current_val.get(field)
                                    if current_val is None:
                                        path_valid = False
                                        break
                                else:
                                    path_valid = False
                                    break
                            
                            if path_valid:
                                resolved_value = current_val
                                print(f"Resolved to: {resolved_value}")
                            else:
                                print(f"Path not valid in output dictionary")
                                resolved_value = None
                        else:
                            print(f"Source task not found: {source_task_id}")
                            resolved_value = None
                    except Exception as e:
                        print(f"Error during variable resolution: {e}")
                        resolved_value = None
                else:
                    print(f"Variable format not recognized")
        
        print(f"Original: {value}")
        print(f"Resolved: {resolved_value}")
        print(f"Expected: {expected}")
        print(f"Result: {'PASS' if resolved_value == expected else 'FAIL'}")

if __name__ == "__main__":
    test_variable_substitution() 