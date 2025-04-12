#!/usr/bin/env python3
"""
Integration Tests for Vector Store Workflows

This module tests how workflows interact with vector stores,
including error handling and graceful degradation when vector stores are unavailable.
"""  # noqa: D202

import unittest
import os
import sys
import logging
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import workflow components
from core.workflow import Workflow
from core.task import Task, DirectHandlerTask
from core.engine import WorkflowEngine
from core.tools.registry import ToolRegistry
from core.tools.registry_access import reset_registry, get_registry
from core.services import get_services, reset_services
from core.utils.testing import MockToolRegistry, WorkflowTestHarness

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestVectorStoreWorkflows(unittest.TestCase):
    """Test workflows interacting with vector stores."""  # noqa: D202

    def setUp(self):
        """Set up the test environment."""
        # Reset singletons
        reset_registry()
        reset_services()
        
        # Create a clean test harness
        self.harness = WorkflowTestHarness()
        
        # Register mock vector store tools
        self.harness.register_mock_tool(
            "list_vector_stores",
            lambda input_data: {
                "success": True,
                "result": [
                    {"id": "vs_docs_123", "name": "Documentation Store"},
                    {"id": "vs_code_456", "name": "Code Examples Store"}
                ]
            }
        )
        
        self.harness.register_mock_tool(
            "search_vector_store",
            lambda input_data: {
                "success": True,
                "result": [
                    {
                        "id": "doc_1",
                        "content": "This is a document about vector stores and embeddings.",
                        "metadata": {"type": "documentation", "author": "AI Team"},
                        "similarity": 0.92
                    },
                    {
                        "id": "doc_2",
                        "content": "Vector databases are optimized for similarity search.",
                        "metadata": {"type": "guide", "author": "Search Team"},
                        "similarity": 0.87
                    }
                ]
            }
        )
        
        self.harness.register_mock_tool(
            "create_vector_store",
            lambda input_data: {
                "success": True,
                "result": "vs_new_789"
            }
        )
        
        # For error condition testing
        self.harness.register_mock_tool(
            "failing_search",
            lambda input_data: {
                "success": False,
                "error": "Vector store not found or access denied",
                "error_code": "VS_NOT_FOUND"
            }
        )

    def test_basic_vector_store_workflow(self):
        """Test a basic workflow that uses vector stores."""
        workflow = Workflow(workflow_id="vs_search_workflow", name="Vector Store Search Workflow")
        
        # Task 1: List available vector stores
        task1 = Task(
            task_id="list_stores",
            name="List Available Vector Stores",
            tool_name="list_vector_stores",
            input_data={},
            next_task_id_on_success="extract_store_id"
        )
        workflow.add_task(task1)
        
        # Task 2: Extract the documentation store ID
        def extract_store_id(input_data):
            stores = input_data.get("stores", [])
            docs_store = next((store for store in stores if "documentation" in store.get("name", "").lower()), None)
            
            if not docs_store:
                return {
                    "success": False,
                    "error": "Documentation store not found"
                }
            
            return {
                "success": True,
                "result": docs_store.get("id")
            }
        
        task2 = DirectHandlerTask(
            task_id="extract_store_id",
            name="Extract Documentation Store ID",
            handler=extract_store_id,
            input_data={"stores": "${list_stores.output_data.result}"},
            next_task_id_on_success="search_docs",
            next_task_id_on_failure="handle_missing_store"
        )
        workflow.add_task(task2)
        
        # Task 3: Handle missing store (error path)
        task3 = Task(
            task_id="handle_missing_store",
            name="Handle Missing Store",
            tool_name="create_vector_store",
            input_data={
                "name": "Documentation Store",
                "description": "Store for documentation and guides"
            },
            next_task_id_on_success="search_docs"
        )
        workflow.add_task(task3)
        
        # Task 4: Search the documentation store
        task4 = Task(
            task_id="search_docs",
            name="Search Documentation Store",
            tool_name="search_vector_store",
            input_data={
                "vector_store_id": "${extract_store_id.output_data.result || handle_missing_store.output_data.result}",
                "query": "vector store embeddings",
                "top_k": 5
            },
            next_task_id_on_success="process_results"
        )
        workflow.add_task(task4)
        
        # Task 5: Process search results
        def process_results(input_data):
            search_results = input_data.get("search_results", [])
            
            if not search_results:
                return {
                    "success": True,
                    "result": {
                        "found_count": 0,
                        "summary": "No relevant documents found"
                    }
                }
            
            # Count by type
            types_count = {}
            for result in search_results:
                doc_type = result.get("metadata", {}).get("type", "unknown")
                types_count[doc_type] = types_count.get(doc_type, 0) + 1
            
            # Generate summary
            summary = f"Found {len(search_results)} documents: " + \
                      ", ".join([f"{count} {doc_type}" for doc_type, count in types_count.items()])
            
            return {
                "success": True,
                "result": {
                    "found_count": len(search_results),
                    "types_count": types_count,
                    "summary": summary,
                    "top_result_content": search_results[0].get("content") if search_results else ""
                }
            }
        
        task5 = DirectHandlerTask(
            task_id="process_results",
            name="Process Search Results",
            handler=process_results,
            input_data={"search_results": "${search_docs.output_data.result}"}
        )
        workflow.add_task(task5)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify results
        self.assertTrue(result.get("success", False))
        
        # Check that all expected tasks were executed
        executed_tasks = self.harness.get_executed_tasks()
        self.assertIn("list_stores", executed_tasks)
        self.assertIn("extract_store_id", executed_tasks)
        self.assertIn("search_docs", executed_tasks)
        self.assertIn("process_results", executed_tasks)
        
        # Verify the store ID was properly extracted
        extract_task = self.harness.get_task("extract_store_id")
        self.assertEqual(extract_task.output_data.get("result"), "vs_docs_123")
        
        # Verify we got search results
        process_task = self.harness.get_task("process_results")
        self.assertEqual(process_task.output_data.get("result").get("found_count"), 2)
        
        # Verify the top result contains expected content
        self.assertIn("vector stores", process_task.output_data.get("result").get("top_result_content").lower())

    def test_error_handling_in_vector_store_workflow(self):
        """Test error handling when vector store operations fail."""
        workflow = Workflow(workflow_id="error_handling_vs", name="Error Handling Vector Store Workflow")
        
        # Task 1: Attempt to search a non-existent store
        task1 = Task(
            task_id="failing_search_task",
            name="Failing Search Task",
            tool_name="failing_search",
            input_data={
                "vector_store_id": "vs_nonexistent_999",
                "query": "important document"
            },
            next_task_id_on_success="process_success",
            next_task_id_on_failure="handle_search_error"
        )
        workflow.add_task(task1)
        
        # Task 2: Success path (should be skipped)
        task2 = Task(
            task_id="process_success",
            name="Process Success",
            tool_name="echo",
            input_data={"message": "Search successful"}
        )
        workflow.add_task(task2)
        
        # Task 3: Error handler for search failure
        def handle_search_error(input_data):
            error = input_data.get("error", "Unknown error")
            error_code = input_data.get("error_code", "UNKNOWN")
            
            recovery_action = "none"
            
            # Determine recovery action based on error
            if "not found" in error.lower():
                recovery_action = "create_store"
            elif "access denied" in error.lower():
                recovery_action = "request_access"
            elif "timeout" in error.lower():
                recovery_action = "retry_later"
            
            return {
                "success": True,
                "result": {
                    "original_error": error,
                    "error_code": error_code,
                    "recovery_action": recovery_action,
                    "fallback_response": "Used cached results due to search failure"
                }
            }
        
        task3 = DirectHandlerTask(
            task_id="handle_search_error",
            name="Handle Search Error",
            handler=handle_search_error,
            input_data={
                "error": "${error.failing_search_task}",
                "error_code": "${error_code.failing_search_task}"
            },
            next_task_id_on_success="generate_response"
        )
        workflow.add_task(task3)
        
        # Task 4: Generate final response based on error handling
        task4 = Task(
            task_id="generate_response",
            name="Generate Response",
            tool_name="echo",
            input_data={
                "message": "Search encountered an error: ${handle_search_error.output_data.result.original_error}. " +
                          "Recommended action: ${handle_search_error.output_data.result.recovery_action}. " +
                          "Fallback: ${handle_search_error.output_data.result.fallback_response}"
            }
        )
        workflow.add_task(task4)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify the workflow completed, though with errors in some tasks
        self.assertTrue(result.get("success", False))
        
        # Check execution path - should have gone through error handling
        executed_tasks = self.harness.get_executed_tasks()
        self.assertIn("failing_search_task", executed_tasks)
        self.assertNotIn("process_success", executed_tasks)
        self.assertIn("handle_search_error", executed_tasks)
        self.assertIn("generate_response", executed_tasks)
        
        # Check that the error handler properly extracted the error
        error_handler_task = self.harness.get_task("handle_search_error")
        self.assertEqual(
            error_handler_task.output_data.get("result").get("recovery_action"),
            "create_store"  # Based on "not found" in error message
        )
        
        # Check the final response includes proper error information
        response_task = self.harness.get_task("generate_response")
        response_message = response_task.output_data.get("result")
        self.assertIn("Search encountered an error", response_message)
        self.assertIn("create_store", response_message)

    def test_graceful_degradation(self):
        """Test workflow gracefully degrades when vector stores are unavailable."""
        workflow = Workflow(workflow_id="graceful_degradation", name="Graceful Degradation Workflow")
        
        # Setup default fallback content
        fallback_content = [
            {"id": "fallback_1", "content": "Basic information about vector stores (fallback)"},
            {"id": "fallback_2", "content": "Default response when search is unavailable"}
        ]
        
        # Task 1: Try the primary vector store search 
        task1 = Task(
            task_id="primary_search",
            name="Primary Vector Store Search",
            tool_name="failing_search",  # Intentionally use failing search
            input_data={
                "vector_store_id": "vs_primary_123",
                "query": "vector store information"
            },
            next_task_id_on_success="process_results",
            next_task_id_on_failure="attempt_backup_search"
        )
        workflow.add_task(task1)
        
        # Task 2: Try backup vector store search
        task2 = Task(
            task_id="attempt_backup_search",
            name="Attempt Backup Search",
            tool_name="search_vector_store",  # This one should succeed
            input_data={
                "vector_store_id": "vs_backup_456",
                "query": "vector store information",
                "primary_error": "${error.primary_search}"
            },
            next_task_id_on_success="process_results",
            next_task_id_on_failure="use_fallback"
        )
        workflow.add_task(task2)
        
        # Task 3: Use fallback content if both searches fail
        def use_fallback(input_data):
            primary_error = input_data.get("primary_error", "Unknown primary error")
            backup_error = input_data.get("backup_error", "Unknown backup error")
            
            return {
                "success": True,
                "result": {
                    "is_fallback": True,
                    "fallback_content": fallback_content,
                    "errors": {
                        "primary": primary_error,
                        "backup": backup_error
                    },
                    "message": "Using fallback content due to search failures"
                }
            }
        
        task3 = DirectHandlerTask(
            task_id="use_fallback",
            name="Use Fallback Content",
            handler=use_fallback,
            input_data={
                "primary_error": "${error.primary_search}",
                "backup_error": "${error.attempt_backup_search}"
            },
            next_task_id_on_success="process_results"
        )
        workflow.add_task(task3)
        
        # Task 4: Process results from any of the sources
        def process_results(input_data):
            # Get results from whichever path succeeded
            results = input_data.get("search_results") or input_data.get("fallback_content")
            is_fallback = input_data.get("is_fallback", False)
            
            source = "primary" if input_data.get("search_results") and not input_data.get("primary_error") else \
                    "backup" if input_data.get("search_results") else "fallback"
            
            # Process the results
            summary = f"Found {len(results) if results else 0} results from {source} source"
            if is_fallback:
                summary += " (fallback content)"
            
            return {
                "success": True,
                "result": {
                    "count": len(results) if results else 0,
                    "source": source,
                    "summary": summary,
                    "content": [item.get("content") for item in results] if results else []
                }
            }
        
        task4 = DirectHandlerTask(
            task_id="process_results",
            name="Process Results",
            handler=process_results,
            input_data={
                "search_results": "${attempt_backup_search.output_data.result}",
                "fallback_content": "${use_fallback.output_data.result.fallback_content}",
                "is_fallback": "${use_fallback.output_data.result.is_fallback}",
                "primary_error": "${error.primary_search}"
            }
        )
        workflow.add_task(task4)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify the workflow completed successfully
        self.assertTrue(result.get("success", False))
        
        # Check execution path - should go through primary failure, backup success
        executed_tasks = self.harness.get_executed_tasks()
        self.assertIn("primary_search", executed_tasks)
        self.assertIn("attempt_backup_search", executed_tasks)
        self.assertNotIn("use_fallback", executed_tasks)  # Backup succeeded, so fallback shouldn't be used
        self.assertIn("process_results", executed_tasks)
        
        # Check the final results
        process_task = self.harness.get_task("process_results")
        self.assertEqual(process_task.output_data.get("result").get("source"), "backup")
        self.assertEqual(process_task.output_data.get("result").get("count"), 2)

    def test_chained_vector_store_operations(self):
        """Test a workflow with multiple chained vector store operations."""
        workflow = Workflow(workflow_id="chained_vs_ops", name="Chained Vector Store Operations")
        
        # Task 1: Get available vector stores
        task1 = Task(
            task_id="get_stores",
            name="Get Available Vector Stores",
            tool_name="list_vector_stores",
            input_data={},
            next_task_id_on_success="search_first_store"
        )
        workflow.add_task(task1)
        
        # Task 2: Search first store
        task2 = Task(
            task_id="search_first_store",
            name="Search First Store",
            tool_name="search_vector_store",
            input_data={
                "vector_store_id": "${get_stores.output_data.result[0].id}",
                "query": "vector database comparison"
            },
            next_task_id_on_success="search_second_store"
        )
        workflow.add_task(task2)
        
        # Task 3: Search second store with context from first search
        def get_refined_query(input_data):
            first_results = input_data.get("first_results", [])
            
            # Create a refined query based on first results
            if first_results and len(first_results) > 0:
                top_result = first_results[0]
                # Extract keywords from top result to refine the query
                content = top_result.get("content", "")
                # Simple approach: just take the first 5 words
                words = content.split()[:5]
                refined_query = " ".join(words)
                return {
                    "success": True,
                    "result": {
                        "refined_query": refined_query,
                        "original_top_match": top_result.get("id")
                    }
                }
            
            # No useful results from first search
            return {
                "success": True,
                "result": {
                    "refined_query": "vector database implementations",  # Default fallback
                    "original_top_match": None
                }
            }
        
        # Add a task to create a refined query
        task_refine = DirectHandlerTask(
            task_id="refine_query",
            name="Refine Query Based on First Results",
            handler=get_refined_query,
            input_data={"first_results": "${search_first_store.output_data.result}"},
            next_task_id_on_success="search_second_store"
        )
        workflow.add_task(task_refine)
        
        # Search second store
        task3 = Task(
            task_id="search_second_store",
            name="Search Second Store",
            tool_name="search_vector_store",
            input_data={
                "vector_store_id": "${get_stores.output_data.result[1].id}",
                "query": "${refine_query.output_data.result.refined_query}"
            },
            next_task_id_on_success="combine_results"
        )
        workflow.add_task(task3)
        
        # Task 4: Combine results from both searches
        def combine_results(input_data):
            first_results = input_data.get("first_results", [])
            second_results = input_data.get("second_results", [])
            refined_query = input_data.get("refined_query", {})
            
            combined = []
            
            # Add results from the first search
            for result in first_results:
                result["source"] = "first_store"
                combined.append(result)
            
            # Add results from the second search
            for result in second_results:
                result["source"] = "second_store"
                combined.append(result)
            
            # Sort by similarity (descending)
            combined.sort(key=lambda x: x.get("similarity", 0), reverse=True)
            
            return {
                "success": True,
                "result": {
                    "combined_results": combined[:5],  # Return top 5
                    "first_store_count": len(first_results),
                    "second_store_count": len(second_results),
                    "refined_query": refined_query.get("refined_query")
                }
            }
        
        task4 = DirectHandlerTask(
            task_id="combine_results",
            name="Combine Search Results",
            handler=combine_results,
            input_data={
                "first_results": "${search_first_store.output_data.result}",
                "second_results": "${search_second_store.output_data.result}",
                "refined_query": "${refine_query.output_data.result}"
            }
        )
        workflow.add_task(task4)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify the workflow completed successfully
        self.assertTrue(result.get("success", False))
        
        # Check that all tasks executed
        executed_tasks = self.harness.get_executed_tasks()
        self.assertIn("get_stores", executed_tasks)
        self.assertIn("search_first_store", executed_tasks)
        self.assertIn("refine_query", executed_tasks)
        self.assertIn("search_second_store", executed_tasks)
        self.assertIn("combine_results", executed_tasks)
        
        # Check the refined query was created
        refine_task = self.harness.get_task("refine_query")
        self.assertIsNotNone(refine_task.output_data.get("result").get("refined_query"))
        
        # Check final combined results
        combine_task = self.harness.get_task("combine_results")
        self.assertEqual(combine_task.output_data.get("result").get("first_store_count"), 2)
        self.assertEqual(combine_task.output_data.get("result").get("second_store_count"), 2)
        self.assertGreaterEqual(
            len(combine_task.output_data.get("result").get("combined_results")),
            1
        )


if __name__ == "__main__":
    unittest.main() 