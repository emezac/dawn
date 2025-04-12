#!/usr/bin/env python3
"""
Tests for compliance workflows.

This file demonstrates how to use testing utilities with compliance workflow implementations.
It includes comprehensive tests for:
1. Smart Compliance Workflow
2. Context Aware Legal Review Workflow
"""  # noqa: D202

import unittest
import json
from unittest.mock import patch, MagicMock

from core.utils.testing import WorkflowTestHarness, TaskTestHarness, create_mock_tool_execution
from core.workflows.smart_compliance_workflow import (
    SmartComplianceWorkflow,
    parse_llm_json_output,
    check_alert_needed
)
from core.workflows.context_aware_legal_review_workflow import (
    ContextAwareLegalReviewWorkflow,
    parse_clauses_json,
    format_error_report_handler,
    format_final_report_handler
)


class TestSmartComplianceWorkflow(unittest.TestCase):
    """Test cases for the Smart Compliance Workflow."""  # noqa: D202

    def test_parse_llm_json_output(self):
        """Test the JSON parsing function for LLM outputs."""
        # Test valid JSON output
        valid_json = """
        {
            "compliance_analysis": {
                "risk_level": "low",
                "findings": ["No significant issues found"],
                "recommendations": ["Continue monitoring regularly"]
            }
        }
        """
        result = parse_llm_json_output(valid_json)
        self.assertEqual(result["risk_level"], "low")
        self.assertEqual(len(result["findings"]), 1)

        # Test markdown-embedded JSON
        markdown_json = """
        Here's my analysis:

        ```json
        {
            "compliance_analysis": {
                "risk_level": "medium",
                "findings": ["Potential issue with data retention"],
                "recommendations": ["Review data retention policies"]
            }
        }
        ```
        """
        result = parse_llm_json_output(markdown_json)
        self.assertEqual(result["risk_level"], "medium")
        self.assertEqual(len(result["findings"]), 1)

        # Test results from file search format
        file_search_json = """
        Results from file search:
        {
            "compliance_analysis": {
                "risk_level": "high",
                "findings": ["Critical issue identified"],
                "recommendations": ["Immediate action required"]
            }
        }
        """
        result = parse_llm_json_output(file_search_json)
        self.assertEqual(result["risk_level"], "high")
        self.assertEqual(len(result["findings"]), 1)

    def test_check_alert_needed(self):
        """Test the alert decision function."""
        # Test with dictionary input
        high_risk = {"risk_level": "high", "findings": ["Critical issue"]}
        self.assertTrue(check_alert_needed(high_risk))

        # Test with medium risk
        medium_risk = {"risk_level": "medium", "findings": ["Potential issue"]}
        self.assertFalse(check_alert_needed(medium_risk))

        # Test with string input (handling unresolved template variables)
        self.assertFalse(check_alert_needed("${analysis_result}"))

    def test_workflow_execution_success_path(self):
        """Test the entire workflow execution for the success path."""
        workflow = SmartComplianceWorkflow()
        
        # Set up mock executions for the workflow
        mock_executions = {
            "llm": [
                create_mock_tool_execution(
                    {"prompt": "Analyze this document for compliance risks"}, 
                    {"response": json.dumps({
                        "compliance_analysis": {
                            "risk_level": "low",
                            "findings": ["No significant issues found"],
                            "recommendations": ["Continue monitoring regularly"]
                        }
                    })}
                )
            ],
            "s3": [
                create_mock_tool_execution(
                    {"action": "upload", "key": "compliance_reports/report.json"},
                    {"url": "https://example.com/report.json"}
                )
            ]
        }
        
        # Initialize test harness with workflow and mocks
        harness = WorkflowTestHarness(workflow, mock_executions, {
            "document_path": "contracts/agreement.pdf",
        })
        
        # Execute workflow and assert it completes
        result = harness.execute()
        harness.assert_workflow_completed()
        
        # Assert specific tasks were executed
        harness.assert_task_executed("extract_document_text")
        harness.assert_task_executed("analyze_compliance_risks")
        harness.assert_task_executed("parse_analysis_result")
        harness.assert_task_executed("generate_report")
        
        # Assert alert task was NOT executed (low risk)
        harness.assert_task_not_executed("send_alert_notification")
        
        # Verify outputs from tasks
        analysis_result = harness.get_task_output("parse_analysis_result")
        self.assertEqual(analysis_result["risk_level"], "low")
        
        # Verify workflow result contains report URL
        self.assertIn("report_url", result)
        self.assertEqual(result["report_url"], "https://example.com/report.json")

    def test_workflow_execution_alert_path(self):
        """Test the entire workflow execution for the alert path."""
        workflow = SmartComplianceWorkflow()
        
        # Set up mock executions for high-risk scenario
        mock_executions = {
            "llm": [
                create_mock_tool_execution(
                    {"prompt": "Analyze this document for compliance risks"}, 
                    {"response": json.dumps({
                        "compliance_analysis": {
                            "risk_level": "high",
                            "findings": ["Critical issue identified"],
                            "recommendations": ["Immediate action required"]
                        }
                    })}
                )
            ],
            "s3": [
                create_mock_tool_execution(
                    {"action": "upload", "key": "compliance_reports/report.json"},
                    {"url": "https://example.com/high_risk_report.json"}
                )
            ],
            "email": [
                create_mock_tool_execution(
                    {"to": "compliance@example.com", "subject": "ALERT: High Risk Compliance Issue"},
                    {"status": "sent"}
                )
            ]
        }
        
        # Initialize test harness with workflow and mocks
        harness = WorkflowTestHarness(workflow, mock_executions, {
            "document_path": "contracts/risky_agreement.pdf",
        })
        
        # Execute workflow and assert it completes
        result = harness.execute()
        harness.assert_workflow_completed()
        
        # Assert alert task WAS executed (high risk)
        harness.assert_task_executed("send_alert_notification")
        
        # Verify workflow result contains both report URL and alert status
        self.assertIn("report_url", result)
        self.assertIn("alert_sent", result)
        self.assertTrue(result["alert_sent"])


class TestContextAwareLegalReviewWorkflow(unittest.TestCase):
    """Test cases for the Context Aware Legal Review Workflow."""  # noqa: D202

    def test_parse_clauses_json(self):
        """Test the JSON parsing function for clauses."""
        # Test valid JSON
        valid_json = """
        {
            "clauses": [
                {
                    "id": "clause-1",
                    "text": "The party shall indemnify...",
                    "risk_score": 0.8,
                    "issues": ["Overly broad indemnification"]
                },
                {
                    "id": "clause-2",
                    "text": "Termination requires 90 days notice...",
                    "risk_score": 0.3,
                    "issues": []
                }
            ]
        }
        """
        result = parse_clauses_json(valid_json)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "clause-1")
        self.assertEqual(result[0]["risk_score"], 0.8)
        
        # Test markdown-embedded JSON
        markdown_json = """
        Here are the extracted clauses:

        ```json
        {
            "clauses": [
                {
                    "id": "clause-3",
                    "text": "Payment terms are net-30...",
                    "risk_score": 0.5,
                    "issues": ["Ambiguous payment terms"]
                }
            ]
        }
        ```
        """
        result = parse_clauses_json(markdown_json)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "clause-3")

    def test_format_error_report_handler(self):
        """Test the error report formatting function."""
        error_message = "Failed to extract clauses: Invalid JSON structure"
        document_path = "contracts/broken_agreement.pdf"
        raw_text = "This is the raw document text..."
        
        result = format_error_report_handler(
            error_message=error_message,
            document_path=document_path,
            document_text=raw_text
        )
        
        self.assertIn("error_report", result)
        self.assertIn(error_message, result["error_report"])
        self.assertIn(document_path, result["error_report"])

    def test_format_final_report_handler(self):
        """Test the final report formatting function."""
        clauses = [
            {
                "id": "clause-1",
                "text": "The party shall indemnify...",
                "risk_score": 0.8,
                "issues": ["Overly broad indemnification"]
            },
            {
                "id": "clause-2",
                "text": "Termination requires 90 days notice...",
                "risk_score": 0.3,
                "issues": []
            }
        ]
        overall_risk_score = 0.65
        
        result = format_final_report_handler(
            clauses=clauses,
            overall_risk_score=overall_risk_score
        )
        
        self.assertIn("legal_review_report", result)
        self.assertIn("overall_risk_score", result["legal_review_report"])
        self.assertEqual(result["legal_review_report"]["overall_risk_score"], 0.65)
        self.assertEqual(len(result["legal_review_report"]["risky_clauses"]), 1)  # Only clause-1 is risky

    def test_workflow_execution_success_path(self):
        """Test the entire workflow execution for the success path."""
        workflow = ContextAwareLegalReviewWorkflow()
        
        # Set up mock executions
        mock_executions = {
            "document_processor": [
                create_mock_tool_execution(
                    {"path": "contracts/agreement.pdf"},
                    {"text": "This is the extracted document text..."}
                )
            ],
            "llm": [
                create_mock_tool_execution(
                    {"prompt": "Extract and analyze legal clauses"},
                    {"response": json.dumps({
                        "clauses": [
                            {
                                "id": "clause-1",
                                "text": "The party shall indemnify...",
                                "risk_score": 0.8,
                                "issues": ["Overly broad indemnification"]
                            },
                            {
                                "id": "clause-2",
                                "text": "Termination requires 90 days notice...",
                                "risk_score": 0.3,
                                "issues": []
                            }
                        ]
                    })}
                ),
                create_mock_tool_execution(
                    {"prompt": "Calculate overall risk score"},
                    {"response": "0.65"}
                )
            ],
            "s3": [
                create_mock_tool_execution(
                    {"action": "upload", "key": "legal_reports/report.json"},
                    {"url": "https://example.com/legal_report.json"}
                )
            ]
        }
        
        # Initialize test harness
        harness = WorkflowTestHarness(workflow, mock_executions, {
            "document_path": "contracts/agreement.pdf",
        })
        
        # Execute workflow
        result = harness.execute()
        harness.assert_workflow_completed()
        
        # Assert tasks were executed in the success path
        harness.assert_task_executed("extract_document_text")
        harness.assert_task_executed("extract_legal_clauses")
        harness.assert_task_executed("parse_clauses")
        harness.assert_task_executed("calculate_risk_score")
        harness.assert_task_executed("format_final_report")
        harness.assert_task_executed("store_report")
        
        # Assert error path tasks were NOT executed
        harness.assert_task_not_executed("format_error_report")
        
        # Verify outputs
        self.assertIn("report_url", result)
        self.assertEqual(result["report_url"], "https://example.com/legal_report.json")

    def test_workflow_execution_error_path(self):
        """Test the workflow execution when clause extraction fails."""
        workflow = ContextAwareLegalReviewWorkflow()
        
        # Set up mock executions with failed clause extraction
        mock_executions = {
            "document_processor": [
                create_mock_tool_execution(
                    {"path": "contracts/agreement.pdf"},
                    {"text": "This is the extracted document text..."}
                )
            ],
            "llm": [
                create_mock_tool_execution(
                    {"prompt": "Extract and analyze legal clauses"},
                    {"response": "I'm sorry, I couldn't extract the clauses because the format is unexpected."}
                )
            ],
            "s3": [
                create_mock_tool_execution(
                    {"action": "upload", "key": "legal_reports/error_report.json"},
                    {"url": "https://example.com/error_report.json"}
                )
            ]
        }
        
        # Initialize test harness
        harness = WorkflowTestHarness(workflow, mock_executions, {
            "document_path": "contracts/agreement.pdf",
        })
        
        # Execute workflow
        result = harness.execute()
        harness.assert_workflow_completed()
        
        # Assert error path tasks WERE executed
        harness.assert_task_executed("format_error_report")
        harness.assert_task_executed("store_error_report")
        
        # Assert success path tasks were NOT executed
        harness.assert_task_not_executed("calculate_risk_score")
        harness.assert_task_not_executed("format_final_report")
        
        # Verify error report was generated
        self.assertIn("error_report_url", result)
        self.assertEqual(result["error_report_url"], "https://example.com/error_report.json")


if __name__ == "__main__":
    unittest.main() 