#!/usr/bin/env python3
"""
Integration Tests for Parallel Execution in Workflows

This module tests the parallel execution capabilities of the Dawn workflow engine,
verifying that tasks can run concurrently and synchronize properly.
"""  # noqa: D202

import unittest
import os
import sys
import logging
import time
import threading
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import workflow components
from core.workflow import Workflow
from core.task import Task, ParallelTask, JoinTask
from core.engine import WorkflowEngine
from core.tools.registry import ToolRegistry
from core.tools.registry_access import reset_registry, get_registry
from core.services import get_services, reset_services
from core.utils.testing import MockToolRegistry, WorkflowTestHarness

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestParallelExecution(unittest.TestCase):
    """Test suite for parallel execution in workflows."""  # noqa: D202

    def setUp(self):
        """Set up the test environment."""
        # Reset singletons
        reset_registry()
        reset_services()
        
        # Create a clean test harness
        self.harness = WorkflowTestHarness()
        
        # Track execution order and timing
        self.execution_log = []
        self.execution_times = {}
        self.mutex = threading.Lock()
        
        # Register a slow tool that simulates processing time
        def slow_tool(input_data):
            tool_name = f"slow_tool_{input_data.get('task_id', 'unknown')}"
            
            with self.mutex:
                start_time = time.time()
                self.execution_log.append(tool_name)
            
            # Simulate work with sleep
            sleep_time = input_data.get("sleep_time", 0.5)
            time.sleep(sleep_time)
            
            with self.mutex:
                end_time = time.time()
                self.execution_times[tool_name] = {
                    "start": start_time,
                    "end": end_time,
                    "duration": end_time - start_time
                }
            
            return {
                "success": True,
                "result": f"Completed {tool_name} in {end_time - start_time:.2f}s"
            }
        
        self.harness.register_mock_tool("slow_tool", slow_tool)
        
        # Register a tool that combines results
        def combine_results(input_data):
            tool_name = "combine_results"
            
            with self.mutex:
                self.execution_log.append(tool_name)
            
            results = input_data.get("results", [])
            combined = ", ".join(results)
            
            return {
                "success": True,
                "result": f"Combined results: {combined}"
            }
        
        self.harness.register_mock_tool("combine_results", combine_results)

    def test_parallel_vs_sequential_execution(self):
        """Test that parallel execution is faster than sequential for independent tasks."""
        # Create a sequential workflow
        seq_workflow = Workflow(workflow_id="sequential", name="Sequential Workflow")
        
        # Add sequential tasks that take time
        for i in range(3):
            task = Task(
                task_id=f"seq_task_{i}",
                name=f"Sequential Task {i}",
                tool_name="slow_tool",
                input_data={
                    "task_id": f"seq_task_{i}",
                    "sleep_time": 0.3  # Each task takes 0.3s
                },
                next_task_id_on_success=f"seq_task_{i+1}" if i < 2 else None
            )
            seq_workflow.add_task(task)
        
        # Run the sequential workflow and measure time
        seq_start = time.time()
        seq_result = self.harness.run_workflow(seq_workflow)
        seq_duration = time.time() - seq_start
        
        # Reset tracking
        self.execution_log = []
        self.execution_times = {}
        self.harness = WorkflowTestHarness()
        self.harness.register_mock_tool("slow_tool", self.setUp.__get_attr__("slow_tool"))
        
        # Create a parallel workflow
        parallel_workflow = Workflow(workflow_id="parallel", name="Parallel Workflow")
        
        # Create a parallel task that spawns multiple tasks
        parallel_task = ParallelTask(
            task_id="parallel_root",
            name="Parallel Root",
            parallel_tasks=[]
        )
        
        # Add child tasks to the parallel task
        for i in range(3):
            child_task = Task(
                task_id=f"parallel_task_{i}",
                name=f"Parallel Task {i}",
                tool_name="slow_tool",
                input_data={
                    "task_id": f"parallel_task_{i}",
                    "sleep_time": 0.3  # Each task takes 0.3s
                }
            )
            parallel_task.add_parallel_task(child_task)
        
        parallel_workflow.add_task(parallel_task)
        
        # Run the parallel workflow and measure time
        parallel_start = time.time()
        parallel_result = self.harness.run_workflow(parallel_workflow)
        parallel_duration = time.time() - parallel_start
        
        # Verify both workflows succeeded
        self.assertTrue(seq_result.get("success", False))
        self.assertTrue(parallel_result.get("success", False))
        
        # Parallel should be significantly faster (not exact due to overhead)
        # If running truly in parallel, it should be about 3x faster
        self.assertLess(parallel_duration, seq_duration * 0.8)
        
        # Verify all tasks executed
        seq_executed = self.harness.get_executed_tasks(seq_workflow.workflow_id)
        parallel_executed = self.harness.get_executed_tasks(parallel_workflow.workflow_id)
        
        self.assertEqual(len(seq_executed), 3)
        self.assertEqual(len(parallel_executed), 4)  # 3 child tasks + 1 parallel task

    def test_parallel_with_join(self):
        """Test parallel execution with a join task that collects results."""
        workflow = Workflow(workflow_id="parallel_join", name="Parallel with Join")
        
        # Task 1: A parallel task that spawns multiple tasks
        parallel_task = ParallelTask(
            task_id="parallel_root",
            name="Parallel Root",
            parallel_tasks=[],
            next_task_id_on_success="join_results"
        )
        
        # Add child tasks to the parallel task
        for i in range(3):
            child_task = Task(
                task_id=f"parallel_task_{i}",
                name=f"Parallel Task {i}",
                tool_name="slow_tool",
                input_data={
                    "task_id": f"parallel_task_{i}",
                    "sleep_time": 0.2,
                    "index": i
                }
            )
            parallel_task.add_parallel_task(child_task)
        
        workflow.add_task(parallel_task)
        
        # Task 2: A join task that collects results from parallel tasks
        join_task = JoinTask(
            task_id="join_results",
            name="Join Results",
            join_tasks=[f"parallel_task_{i}" for i in range(3)],
            output_mapping={
                "results": [f"${{{f'parallel_task_{i}.output_data.result'}}}" for i in range(3)]
            },
            next_task_id_on_success="process_results"
        )
        workflow.add_task(join_task)
        
        # Task 3: Process the joined results
        process_task = Task(
            task_id="process_results",
            name="Process Results",
            tool_name="combine_results",
            input_data={
                "results": "${join_results.output_data.results}"
            }
        )
        workflow.add_task(process_task)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify workflow succeeded
        self.assertTrue(result.get("success", False))
        
        # Verify all tasks executed
        executed_tasks = self.harness.get_executed_tasks()
        for task_id in ["parallel_root"] + [f"parallel_task_{i}" for i in range(3)] + ["join_results", "process_results"]:
            self.assertIn(task_id, executed_tasks)
        
        # Verify the results were correctly joined and processed
        process_task_obj = self.harness.get_task("process_results")
        combined_results = process_task_obj.output_data.get("result", "")
        
        # The combined result should contain all three parallel tasks
        for i in range(3):
            self.assertIn(f"parallel_task_{i}", combined_results)

    def test_parallel_execution_timing(self):
        """Test that tasks in a parallel group execute concurrently."""
        workflow = Workflow(workflow_id="timing_test", name="Timing Test")
        
        # Create a parallel task with varying execution times
        parallel_task = ParallelTask(
            task_id="parallel_root",
            name="Parallel Root",
            parallel_tasks=[]
        )
        
        # Add tasks with different execution times
        execution_times = [0.3, 0.5, 0.2]
        for i, exec_time in enumerate(execution_times):
            child_task = Task(
                task_id=f"parallel_task_{i}",
                name=f"Parallel Task {i}",
                tool_name="slow_tool",
                input_data={
                    "task_id": f"parallel_task_{i}",
                    "sleep_time": exec_time
                }
            )
            parallel_task.add_parallel_task(child_task)
        
        workflow.add_task(parallel_task)
        
        # Run the workflow
        start_time = time.time()
        result = self.harness.run_workflow(workflow)
        total_duration = time.time() - start_time
        
        # Verify workflow succeeded
        self.assertTrue(result.get("success", False))
        
        # Check execution times
        task_times = {}
        for i in range(3):
            task_id = f"slow_tool_parallel_task_{i}"
            task_times[task_id] = self.execution_times.get(task_id, {}).get("duration", 0)
        
        # If tasks ran in parallel, the total duration should be approximately 
        # equal to the longest task duration plus some overhead
        max_task_time = max(execution_times)
        
        # Add a bit of buffer for execution overhead
        self.assertLess(total_duration, sum(execution_times) * 0.8)
        self.assertGreaterEqual(total_duration, max_task_time)
        
        # Check that tasks with shorter durations completed before the longest task
        longest_index = execution_times.index(max_task_time)
        longest_task_id = f"slow_tool_parallel_task_{longest_index}"
        longest_end_time = self.execution_times.get(longest_task_id, {}).get("end", 0)
        
        # All other tasks should have finished before or around the same time
        for i, exec_time in enumerate(execution_times):
            if i != longest_index:
                task_id = f"slow_tool_parallel_task_{i}"
                task_end_time = self.execution_times.get(task_id, {}).get("end", 0)
                # Allow a small buffer for task completion timing
                self.assertLessEqual(task_end_time, longest_end_time + 0.1)

    def test_parallel_error_handling(self):
        """Test error handling in parallel execution."""
        workflow = Workflow(workflow_id="parallel_errors", name="Parallel Error Handling")
        
        # Register a tool that can be configured to fail
        def failing_tool(input_data):
            tool_name = f"failing_tool_{input_data.get('task_id', 'unknown')}"
            should_fail = input_data.get("should_fail", False)
            
            with self.mutex:
                self.execution_log.append(tool_name)
            
            if should_fail:
                return {
                    "success": False,
                    "error": f"Tool {tool_name} failed as requested",
                    "error_code": "REQUESTED_FAILURE"
                }
            
            return {
                "success": True,
                "result": f"Tool {tool_name} succeeded"
            }
        
        self.harness.register_mock_tool("failing_tool", failing_tool)
        
        # Create a parallel task with one failing task
        parallel_task = ParallelTask(
            task_id="parallel_root",
            name="Parallel Root with Error",
            parallel_tasks=[],
            next_task_id_on_success="success_handler",
            next_task_id_on_failure="error_handler"
        )
        
        # Add tasks, one of which will fail
        for i in range(3):
            child_task = Task(
                task_id=f"parallel_task_{i}",
                name=f"Parallel Task {i}",
                tool_name="failing_tool",
                input_data={
                    "task_id": f"parallel_task_{i}",
                    "should_fail": (i == 1)  # Middle task will fail
                }
            )
            parallel_task.add_parallel_task(child_task)
        
        workflow.add_task(parallel_task)
        
        # Add success handler that should not be reached
        success_task = Task(
            task_id="success_handler",
            name="Success Handler",
            tool_name="slow_tool",
            input_data={
                "task_id": "success_handler",
                "sleep_time": 0.1
            }
        )
        workflow.add_task(success_task)
        
        # Add error handler
        error_task = Task(
            task_id="error_handler",
            name="Error Handler",
            tool_name="slow_tool",
            input_data={
                "task_id": "error_handler",
                "sleep_time": 0.1,
                "error": "${error.parallel_root}",
                "error_code": "${error_code.parallel_root}",
                "failed_task": "${error_task_id.parallel_root}"
            }
        )
        workflow.add_task(error_task)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify workflow completed (but with failure in the parallel task)
        self.assertTrue(result.get("success", False))
        
        # Verify the error handler was executed, not the success handler
        executed_tasks = self.harness.get_executed_tasks()
        self.assertIn("error_handler", executed_tasks)
        self.assertNotIn("success_handler", executed_tasks)
        
        # Check that the error handler received the correct error information
        error_handler = self.harness.get_task("error_handler")
        self.assertIn("failed as requested", error_handler.input_data.get("error", ""))
        self.assertEqual(error_handler.input_data.get("error_code"), "REQUESTED_FAILURE")
        self.assertEqual(error_handler.input_data.get("failed_task"), "parallel_task_1")

    def test_parallel_task_dependencies(self):
        """Test parallel tasks with dependencies between them."""
        workflow = Workflow(workflow_id="parallel_deps", name="Parallel Dependencies")
        
        # Create a registry to track dependencies between tasks
        dependency_registry = {"completed": set()}
        
        # Create a tool that checks dependencies
        def dependency_tool(input_data):
            task_id = input_data.get("task_id", "unknown")
            tool_name = f"dependency_tool_{task_id}"
            dependencies = input_data.get("dependencies", [])
            
            with self.mutex:
                # Check that all dependencies have been completed
                for dep in dependencies:
                    if dep not in dependency_registry["completed"]:
                        return {
                            "success": False,
                            "error": f"Dependency {dep} not completed before {task_id}",
                            "error_code": "DEPENDENCY_ERROR"
                        }
                
                # Mark this task as completed
                dependency_registry["completed"].add(task_id)
            
            return {
                "success": True,
                "result": f"Task {task_id} completed successfully"
            }
        
        self.harness.register_mock_tool("dependency_tool", dependency_tool)
        
        # Create a complex workflow with dependencies
        # Task A: No dependencies
        task_a = Task(
            task_id="task_a",
            name="Task A",
            tool_name="dependency_tool",
            input_data={
                "task_id": "task_a",
                "dependencies": []
            }
        )
        workflow.add_task(task_a)
        
        # Task B: Depends on A
        task_b = Task(
            task_id="task_b",
            name="Task B",
            tool_name="dependency_tool",
            input_data={
                "task_id": "task_b",
                "dependencies": ["task_a"]
            }
        )
        workflow.add_task(task_b)
        
        # Create parallel tasks with dependencies
        parallel_task = ParallelTask(
            task_id="parallel_group",
            name="Parallel Group",
            parallel_tasks=[],
            next_task_id_on_success="final_task"
        )
        
        # Task C: Depends on A
        task_c = Task(
            task_id="task_c",
            name="Task C",
            tool_name="dependency_tool",
            input_data={
                "task_id": "task_c",
                "dependencies": ["task_a"]
            }
        )
        parallel_task.add_parallel_task(task_c)
        
        # Task D: Depends on B
        task_d = Task(
            task_id="task_d",
            name="Task D",
            tool_name="dependency_tool",
            input_data={
                "task_id": "task_d",
                "dependencies": ["task_b"]
            }
        )
        parallel_task.add_parallel_task(task_d)
        
        # Task E: Depends on C
        task_e = Task(
            task_id="task_e",
            name="Task E",
            tool_name="dependency_tool",
            input_data={
                "task_id": "task_e",
                "dependencies": ["task_c"]
            }
        )
        parallel_task.add_parallel_task(task_e)
        
        workflow.add_task(parallel_task)
        
        # Final task: Depends on all
        final_task = Task(
            task_id="final_task",
            name="Final Task",
            tool_name="dependency_tool",
            input_data={
                "task_id": "final_task",
                "dependencies": ["task_a", "task_b", "task_c", "task_d", "task_e"]
            }
        )
        workflow.add_task(final_task)
        
        # Run the workflow with proper task ordering
        # Configure the engine to respect dependencies
        engine = WorkflowEngine()
        
        # First run task A
        task_a_result = engine.execute_task(workflow, task_a)
        self.assertTrue(task_a_result.get("success", False))
        
        # Then run task B
        task_b_result = engine.execute_task(workflow, task_b)
        self.assertTrue(task_b_result.get("success", False))
        
        # Now run the parallel tasks
        parallel_result = engine.execute_task(workflow, parallel_task)
        self.assertTrue(parallel_result.get("success", False))
        
        # Finally run the final task
        final_result = engine.execute_task(workflow, final_task)
        self.assertTrue(final_result.get("success", False))
        
        # Verify all tasks were completed
        self.assertEqual(len(dependency_registry["completed"]), 6)  # 5 named tasks + 1 parallel group


if __name__ == "__main__":
    unittest.main() 