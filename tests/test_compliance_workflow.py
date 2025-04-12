#!/usr/bin/env python3
"""
Test Compliance Workflow with Recordings

This module demonstrates how to test the compliance workflow using recorded tool executions.
"""  # noqa: D202

import unittest
import os
import sys
import json
from unittest.mock import patch
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the mock compliance workflow module
from examples.mock_compliance_workflow import (
    MockToolRegistry,
    compliance_workflow,
    list_vector_stores,
    search_vector_store,
    compliance_check
)


class TestComplianceWorkflow(unittest.TestCase):
    """Test the compliance workflow using recorded tool executions."""  # noqa: D202
    
    def setUp(self):
        """Set up the test environment."""
        # Create a mock registry for each test
        self.mock_registry = MockToolRegistry()
        
        # Register basic tools
        self.mock_registry.register_tool("list_vector_stores", list_vector_stores)
        self.mock_registry.register_tool("search_vector_store", search_vector_store)
        self.mock_registry.register_tool("compliance_check", compliance_check)
        
        # Create the patch for the execute_tool method
        self.registry_patch = patch(
            'examples.mock_compliance_workflow.MockToolRegistry.execute_tool',
            side_effect=self.mock_registry.execute_tool
        )
        
        # Start the patch
        self.registry_patch.start()
    
    def tearDown(self):
        """Clean up after each test."""
        # Stop all patches
        self.registry_patch.stop()
    
    def test_with_recorded_executions(self):
        """Test the compliance workflow using recorded tool executions."""
        # Create recordings directory if it doesn't exist
        recordings_dir = Path("tests/recordings")
        recordings_dir.mkdir(exist_ok=True, parents=True)
        
        # Path to the recordings file
        recording_file = recordings_dir / "compliance_workflow_test_recording.json"
        
        # Create mock recordings if they don't exist
        if not recording_file.exists():
            self._create_mock_recordings(recording_file)
        
        # Load the recordings
        with open(recording_file, 'r') as f:
            recordings = json.load(f)
        
        # Add the recorded executions to the mock registry
        for recording in recordings:
            # Create a mock execution with the recorded input and output
            self.mock_registry.create_mock_tool_execution(
                tool_name=recording["tool_name"],
                input_matcher=recording["input_data"],
                result=recording["result"]
            )
        
        # Execute the workflow with the mock registry
        result = compliance_workflow(data_type="user_emails", query="sensitive")
        
        # Verify the result
        self.assertTrue(result.get("success", False))
        self.assertIn("risk_level", result.get("result", {}))
        self.assertIn("compliance_issues", result.get("result", {}))
        self.assertIn("recommended_actions", result.get("result", {}))
    
    def test_with_specific_mocks(self):
        """Test the compliance workflow with specific mock tool executions."""
        # Create specific mock tool executions
        self.mock_registry.create_mock_tool_execution(
            tool_name="search_vector_store",
            input_matcher={"store_name": "user_data", "query": "sensitive"},
            result={
                "success": True,
                "result": {
                    "matches": [
                        {
                            "id": "email-1",
                            "metadata": {
                                "content": "Email containing SSN: 123-45-6789"
                            }
                        }
                    ]
                },
                "status": "success"
            }
        )
        
        self.mock_registry.create_mock_tool_execution(
            tool_name="compliance_check",
            input_matcher={"content": "Email containing SSN: 123-45-6789"},
            result={
                "success": True,
                "result": {
                    "risk_level": "high",
                    "compliance_issues": ["Social Security Number (SSN) found"],
                    "recommended_actions": ["Encrypt SSN data"]
                },
                "status": "success"
            }
        )
        
        # Execute the workflow with the mock registry
        result = compliance_workflow(data_type="user_emails", query="sensitive")
        
        # Verify the result
        self.assertTrue(result.get("success", False))
        self.assertEqual(result.get("result", {}).get("risk_level"), "high")
        self.assertIn("Social Security Number (SSN) found", result.get("result", {}).get("compliance_issues", []))
    
    def test_error_handling(self):
        """Test handling of errors in tool executions."""
        # Create a mock execution that returns an error
        self.mock_registry.create_mock_tool_execution(
            tool_name="search_vector_store",
            input_matcher={"store_name": "user_data", "query": "sensitive"},
            result={
                "success": False,
                "error": "Simulated error in search_vector_store",
                "status": "error"
            }
        )
        
        # Execute the workflow with the mock registry
        result = compliance_workflow(data_type="user_emails", query="sensitive")
        
        # Verify the error is properly handled
        self.assertFalse(result.get("success", True))
        self.assertIn("Error searching vector store", result.get("error", ""))
    
    def _create_mock_recordings(self, file_path: Path):
        """Create mock recordings for testing when no recordings exist."""
        recordings = [
            {
                "tool_name": "search_vector_store",
                "input_data": {"store_name": "user_data", "query": "sensitive"},
                "result": {
                    "success": True,
                    "result": {
                        "matches": [
                            {
                                "id": "email-1",
                                "metadata": {
                                    "content": "Email containing SSN: 123-45-6789"
                                }
                            }
                        ]
                    },
                    "status": "success"
                }
            },
            {
                "tool_name": "compliance_check",
                "input_data": {"content": "Email containing SSN: 123-45-6789"},
                "result": {
                    "success": True,
                    "result": {
                        "risk_level": "high",
                        "compliance_issues": ["Social Security Number (SSN) found"],
                        "recommended_actions": ["Encrypt SSN data", "Restrict access"]
                    },
                    "status": "success"
                }
            }
        ]
        
        # Save the mock recordings
        with open(file_path, 'w') as f:
            json.dump(recordings, f, indent=2)


if __name__ == "__main__":
    unittest.main() 