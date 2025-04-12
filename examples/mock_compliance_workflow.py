#!/usr/bin/env python3
"""
Mock Compliance Workflow Module

This module provides a mock compliance workflow for testing purposes.
It simulates a workflow that analyzes data for compliance issues,
including tools for:
- Listing available vector stores
- Searching vector stores for documents
- Checking content for compliance issues

It also implements the recording and replaying pattern for testing workflows,
which allows capturing tool executions and replaying them in tests.
"""  # noqa: D202

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Union, Callable, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define vector store mapping
VECTOR_STORE_MAP = {
    "user_emails": "user_data",
    "medical_records": "medical_records",
    "product_catalog": "product_catalog"
}

# Storage for recording tool executions
recorded_executions = []

class MockToolRegistry:
    """Registry for mock tool executions used in testing."""  # noqa: D202
    
    def __init__(self, recordings_file: Optional[str] = None):
        """
        Initialize a mock tool registry.
        
        Args:
            recordings_file: Optional path to a JSON file containing recorded tool executions
        """
        self.tools = {}
        self.tool_executions = []
        logger.info("Initialized MockToolRegistry")
        
        if recordings_file:
            self.load_recordings(recordings_file)
    
    def load_recordings(self, file_path: str) -> None:
        """
        Load recorded tool executions from a JSON file.
        
        Args:
            file_path: Path to the JSON file containing recorded tool executions
        """
        try:
            with open(file_path, 'r') as f:
                self.tool_executions = json.load(f)
            logger.info(f"Loaded {len(self.tool_executions)} recorded executions from {file_path}")
        except Exception as e:
            logger.error(f"Error loading recordings from {file_path}: {str(e)}")
            self.tool_executions = []
    
    def register_tool(self, tool_name: str, tool_func: Callable) -> None:
        """
        Register a tool function with the registry.
        
        Args:
            tool_name: Name of the tool to register
            tool_func: Function that implements the tool
        """
        self.tools[tool_name] = tool_func
        logger.info(f"Registered tool: {tool_name}")
    
    def create_mock_tool_execution(self, 
                                 tool_name: str, 
                                 input_matcher: Union[Dict, Callable],
                                 result: Dict[str, Any]) -> None:
        """
        Create a mock tool execution for testing.
        
        Args:
            tool_name: The name of the tool
            input_matcher: Either a dict to match against input data, or a function that takes input data and returns a boolean
            result: The result to return when the tool is executed with matching input
        """
        self.tool_executions.append({
            "tool_name": tool_name,
            "input_matcher": input_matcher,
            "result": result
        })
        logger.info(f"Created mock execution for tool: {tool_name}")
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a registered tool with the given parameters.
        
        If the tool and parameters match a recorded execution, the recorded result is returned.
        Otherwise, the actual tool function is called.
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Parameters to pass to the tool
            
        Returns:
            Tool execution result
        """
        # First check for exact matches in recorded executions
        for execution in self.tool_executions:
            if execution["tool_name"] == tool_name:
                input_matcher = execution.get("input_matcher")
                
                # If it's a callable, use it to match the input
                if callable(input_matcher):
                    if input_matcher(kwargs):
                        logger.info(f"Found matching mock execution for tool '{tool_name}' using callable matcher")
                        return execution["result"]
                # If it's a dictionary or None, check for direct equality
                elif input_matcher == kwargs:
                    logger.info(f"Found exact match for tool '{tool_name}'")
                    return execution["result"]
                # If it's in the flat recorded format
                elif "input_data" in execution and execution["input_data"] == kwargs:
                    logger.info(f"Found match in flat recorded format for tool '{tool_name}'")
                    return execution["result"]
        
        # If no match found in recordings, execute the actual tool
        if tool_name not in self.tools:
            logger.error(f"Unknown tool: {tool_name}")
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "status": "error"
            }
        
        try:
            logger.info(f"Executing actual tool: {tool_name} with params: {kwargs}")
            result = self.tools[tool_name](**kwargs)
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return {
                "success": False,
                "error": f"Error executing {tool_name}: {str(e)}",
                "status": "error"
            }

# Mock tool implementations
def list_vector_stores(**kwargs) -> Dict[str, Any]:
    """
    List available vector stores.
    
    Returns:
        Dictionary with result containing list of vector stores
    """
    logger.info("Executing list_vector_stores tool")
    return {
        "success": True,
        "result": list(set(VECTOR_STORE_MAP.values())),
        "status": "success"
    }

def search_vector_store(store_name: str, query: str, **kwargs) -> Dict[str, Any]:
    """
    Search a vector store for documents matching the query.
    
    Args:
        store_name: Name of the vector store to search
        query: Search query
        
    Returns:
        Dictionary with search results
    """
    logger.info(f"Executing search_vector_store tool: {store_name}, query: {query}")
    
    # Define sample content based on store type
    content_map = {
        "user_data": [
            {
                "id": "email-1",
                "metadata": {
                    "content": "Email from user containing SSN: 123-45-6789 and credit card: 4111-1111-1111-1111",
                    "sender": "john.doe@example.com",
                    "date": "2023-05-15"
                }
            },
            {
                "id": "email-2",
                "metadata": {
                    "content": "Regular update email with project status and timeline",
                    "sender": "project.manager@example.com",
                    "date": "2023-05-16"
                }
            }
        ],
        "medical_records": [
            {
                "id": "patient-1",
                "metadata": {
                    "content": "Patient: Jane Smith, DOB: 04/12/1982, Diagnosis: Hypertension, Medication: Lisinopril 10mg",
                    "doctor": "Dr. Williams",
                    "date": "2023-03-22"
                }
            },
            {
                "id": "patient-2",
                "metadata": {
                    "content": "Patient: Robert Johnson, DOB: 11/28/1975, Allergies: Penicillin, Diagnosis: Type 2 Diabetes",
                    "doctor": "Dr. Martinez",
                    "date": "2023-04-05"
                }
            }
        ],
        "product_catalog": [
            {
                "id": "product-1",
                "metadata": {
                    "content": "Product: Laptop Pro X15, Price: $1,299.99, SKU: LP-X15-2023, Stock: 45 units",
                    "category": "Electronics",
                    "manufacturer": "TechCorp"
                }
            },
            {
                "id": "product-2",
                "metadata": {
                    "content": "Product: Ergonomic Office Chair, Price: $249.99, SKU: EOC-2023, Stock: 78 units",
                    "category": "Furniture",
                    "manufacturer": "ComfortPlus"
                }
            }
        ]
    }
    
    # Return appropriate content based on store name
    if store_name in content_map:
        # Filter results based on query if needed
        matches = content_map[store_name]
        if "sensitive" in query.lower() or "compliance" in query.lower():
            # Return only sensitive items if looking for them
            matches = [item for item in matches if any(keyword in item["metadata"]["content"].lower() 
                                                   for keyword in ["ssn", "credit card", "patient", "diagnosis"])]
        
        return {
            "success": True,
            "result": {
                "matches": matches[:2]  # Return up to 2 matches
            },
            "status": "success"
        }
    else:
        return {
            "success": False,
            "error": f"Vector store not found: {store_name}",
            "status": "error"
        }

def compliance_check(content: str, **kwargs) -> Dict[str, Any]:
    """
    Check content for compliance issues.
    
    Args:
        content: Content to check for compliance issues
        
    Returns:
        Dictionary with compliance analysis results
    """
    logger.info(f"Executing compliance_check tool on content: {content[:50]}...")
    
    # Check for different types of sensitive information
    issues = []
    recommended_actions = []
    
    content_lower = content.lower()
    
    # Detect SSN
    if "ssn" in content_lower or "social security" in content_lower:
        issues.append("Social Security Number (SSN) found")
        recommended_actions.append("Encrypt SSN data")
        recommended_actions.append("Restrict access to authorized personnel only")
        risk_level = "high"
    
    # Detect credit card information
    elif "credit card" in content_lower or any(card_type in content_lower for card_type in ["visa", "mastercard", "amex"]):
        issues.append("Credit card information found")
        recommended_actions.append("Apply PCI DSS controls")
        recommended_actions.append("Use tokenization for credit card data")
        risk_level = "high"
    
    # Detect medical information
    elif any(medical_term in content_lower for medical_term in ["patient", "diagnosis", "medication", "doctor", "medical"]):
        issues.append("Medical information found")
        recommended_actions.append("Apply HIPAA controls")
        recommended_actions.append("Ensure PHI is properly secured")
        risk_level = "high"
    
    # No sensitive information found
    else:
        risk_level = "low"
    
    return {
        "success": True,
        "result": {
            "risk_level": risk_level,
            "compliance_issues": issues,
            "recommended_actions": recommended_actions
        },
        "status": "success"
    }

def execute_and_record_tool(tool_name: str, **kwargs) -> Dict[str, Any]:
    """
    Execute a tool and record the inputs and outputs for testing.
    
    Args:
        tool_name: The name of the tool to execute
        **kwargs: Parameters to pass to the tool
        
    Returns:
        The result of the tool execution
    """
    global recorded_executions
    
    logger.info(f"Executing and recording tool '{tool_name}' with input: {kwargs}")
    
    # Get actual tool implementations
    tools = {
        "list_vector_stores": list_vector_stores,
        "search_vector_store": search_vector_store,
        "compliance_check": compliance_check,
        "compliance_workflow": compliance_workflow
    }
    
    # Execute the tool
    if tool_name not in tools:
        result = {
            "success": False,
            "error": f"Unknown tool: {tool_name}",
            "status": "error"
        }
    else:
        try:
            result = tools[tool_name](**kwargs)
        except Exception as e:
            result = {
                "success": False,
                "error": f"Error executing {tool_name}: {str(e)}",
                "status": "error"
            }
    
    # Record the execution
    recorded_executions.append({
        "tool_name": tool_name,
        "input_data": kwargs,
        "result": result
    })
    
    return result

def save_recorded_executions(file_path: str) -> None:
    """
    Save the recorded tool executions to a JSON file.
    
    Args:
        file_path: The path to save the recordings to
    """
    # Create directory if it doesn't exist
    recording_dir = os.path.dirname(file_path)
    os.makedirs(recording_dir, exist_ok=True)
    
    # Save recordings to JSON file
    with open(file_path, 'w') as f:
        json.dump(recorded_executions, f, indent=2)
    
    logger.info(f"Saved {len(recorded_executions)} recorded tool executions to {file_path}")

def compliance_workflow(data_type: str, query: str, **kwargs) -> Dict[str, Any]:
    """
    Analyze data for potential compliance issues.
    
    Args:
        data_type: Type of data to analyze (user_emails, medical_records, product_catalog)
        query: Search query to find relevant documents
        
    Returns:
        Dictionary with compliance analysis results
    """
    logger.info(f"Executing compliance_workflow for data_type: {data_type}, query: {query}")
    
    # Check if data type is valid
    if data_type not in VECTOR_STORE_MAP:
        return {
            "success": False,
            "error": f"Invalid data type: {data_type}",
            "status": "error"
        }
    
    store_name = VECTOR_STORE_MAP[data_type]
    
    try:
        # Search for relevant documents
        search_result = execute_and_record_tool("search_vector_store", 
                                             store_name=store_name, 
                                             query=query)
        
        if not search_result.get("success", False):
            return {
                "success": False,
                "error": f"Error searching vector store: {search_result.get('error', 'Unknown error')}",
                "status": "error"
            }
        
        # Process search results
        matches = search_result.get("result", {}).get("matches", [])
        
        if not matches:
            return {
                "success": True,
                "result": {
                    "risk_level": "low",
                    "compliance_issues": [],
                    "recommended_actions": ["No compliance issues found"]
                },
                "status": "success"
            }
        
        # Check each document for compliance issues
        all_issues = []
        highest_risk_level = "low"
        
        for match in matches:
            content = match.get("metadata", {}).get("content", "")
            
            compliance_result = execute_and_record_tool("compliance_check", content=content)
            
            if compliance_result.get("success", False):
                result = compliance_result.get("result", {})
                issues = result.get("compliance_issues", [])
                risk_level = result.get("risk_level", "low")
                
                if issues:
                    all_issues.extend(issues)
                    
                    # Update highest risk level
                    if risk_level == "high" and highest_risk_level != "high":
                        highest_risk_level = "high"
                    elif risk_level == "medium" and highest_risk_level == "low":
                        highest_risk_level = "medium"
        
        # Combine results
        recommended_actions = []
        if "high" == highest_risk_level:
            recommended_actions.append("Implement immediate mitigation measures")
            recommended_actions.append("Conduct a full compliance audit")
        elif "medium" == highest_risk_level:
            recommended_actions.append("Review data handling procedures")
            recommended_actions.append("Enhance monitoring for sensitive data")
        else:
            recommended_actions.append("Continue regular compliance monitoring")
        
        return {
            "success": True,
            "result": {
                "risk_level": highest_risk_level,
                "compliance_issues": all_issues,
                "recommended_actions": recommended_actions,
                "documents_analyzed": len(matches)
            },
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error in compliance workflow: {str(e)}")
        return {
            "success": False,
            "error": f"Error in compliance workflow: {str(e)}",
            "status": "error"
        }

def run_recorded_workflow(data_type: str = "user_emails", query: str = "sensitive", test_case_name: str = "default") -> Dict[str, Any]:
    """
    Run the compliance workflow and record all tool executions.
    
    Args:
        data_type: Type of data to analyze (user_emails, medical_records, product_catalog)
        query: Search query to find relevant documents
        test_case_name: Name to use for the recording file
        
    Returns:
        Result of the workflow execution
    """
    global recorded_executions
    recorded_executions = []
    
    try:
        logger.info(f"Running compliance workflow with data_type '{data_type}' and query '{query}'")
        
        # Run the workflow with recording
        result = compliance_workflow(data_type=data_type, query=query)
        
        # Create the recordings directory if it doesn't exist
        recordings_dir = os.path.join("tests", "recordings")
        os.makedirs(recordings_dir, exist_ok=True)
        
        # Save the recordings
        file_path = os.path.join(recordings_dir, f"compliance_workflow_{test_case_name}_recording.json")
        save_recorded_executions(file_path)
        
        return result
    
    except Exception as e:
        logger.error(f"Error running recorded workflow: {str(e)}")
        return {
            "success": False,
            "error": f"Error running recorded workflow: {str(e)}",
            "status": "error"
        }

if __name__ == "__main__":
    # Run the workflow with recording for different data types
    test_cases = [
        {"data_type": "user_emails", "query": "sensitive", "test_case_name": "user_emails"},
        {"data_type": "medical_records", "query": "patient", "test_case_name": "medical_records"},
        {"data_type": "product_catalog", "query": "price", "test_case_name": "product_catalog"}
    ]
    
    for test_case in test_cases:
        logger.info(f"Running test case: {test_case['test_case_name']}")
        result = run_recorded_workflow(**test_case)
        
        if result.get("success", False):
            logger.info(f"Test case {test_case['test_case_name']} completed successfully")
            result_data = result.get("result", {})
            logger.info(f"Risk level: {result_data.get('risk_level')}")
            logger.info(f"Issues: {result_data.get('compliance_issues')}")
        else:
            logger.error(f"Test case {test_case['test_case_name']} failed: {result.get('error')}") 