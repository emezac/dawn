"""
Final Complex Conditional Workflow Example with Fallback Logic

This workflow does the following:
1. Uploads a training document.
2. Creates a vector store from the uploaded file's ID.
3. Extracts document insights via file search.
   - If the output is too short (≤ 100 characters), it branches to regenerate insights.
4. Performs a web search for AI ethics.
   - If web search fails or times out, it follows the failure branch and executes a fallback task to supply a default result.
5. Uses an LLM to generate a combined summary using the document insights and the web search (or fallback) result.
6. Writes the final summary to a Markdown file.

This updated version uses DirectHandlerTask for LLM operations and improved variable resolution.
"""

import os
import sys
import json
from typing import Dict, Any, Optional

from dotenv import load_dotenv
from openai import OpenAI

# Add parent directory to path to import framework modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import Agent
from core.engine import WorkflowEngine
from core.llm.interface import LLMInterface
from core.task import DirectHandlerTask, Task
from core.tools.registry import ToolRegistry
from core.workflow import Workflow

# Load environment variables from .env file
load_dotenv()

# Instantiate the OpenAI client for LLM tasks
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Utility function for parsing structured task outputs
def extract_task_output(task_output, field_path=None):
    """
    Extract data from task output using a field path.
    
    Args:
        task_output: The task output data to extract from
        field_path: Optional dot-notation path to extract (e.g., "result.summary")
        
    Returns:
        The extracted data or the original output if no path is provided
    """
    if not task_output:
        return None
        
    # If no specific field path is requested, try to get the most useful representation
    if not field_path:
        # For LLM tasks (which typically have a response field)
        if isinstance(task_output, dict) and "response" in task_output:
            # Try to parse it as JSON if it looks like JSON
            response = task_output.get("response", "")
            if response and isinstance(response, str) and (response.strip().startswith("{") or response.strip().startswith("[")):
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    return response
            return response
        # For tool tasks (which typically have a result field)
        elif isinstance(task_output, dict) and "result" in task_output:
            return task_output.get("result")
        # Otherwise, just return the output as is
        return task_output
    
    # If a specific field path is provided, navigate the object structure
    current = task_output
    for field in field_path.split("."):
        if isinstance(current, dict) and field in current:
            current = current[field]
        else:
            # If the field is not found, try to parse JSON if this is a string
            if isinstance(current, str) and (current.strip().startswith("{") or current.strip().startswith("[")):
                try:
                    parsed = json.loads(current)
                    if isinstance(parsed, dict) and field in parsed:
                        current = parsed[field]
                        continue
                except json.JSONDecodeError:
                    pass
            # If we couldn't find or parse the field, return None
            return None
    return current


def llm_handler(input_data):
    """
    DirectHandler function for LLM tasks.
    
    Args:
        input_data: Dictionary containing the prompt
        
    Returns:
        Dictionary with LLM response
    """
    prompt = input_data.get("prompt", "")
    if not prompt:
        return {
            "success": False,
            "error": "No prompt provided",
            "error_type": "InputValidationError"
        }
        
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
        )
        result = response.choices[0].message.content.strip()
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"LLM call failed: {str(e)}",
            "error_type": type(e).__name__
        }


def default_web_search_handler(input_data):
    """
    DirectHandler function for providing fallback web search results.
    
    Args:
        input_data: Dictionary with the query
        
    Returns:
        Dictionary with fallback search results
    """
    prompt = input_data.get("prompt", "Return a default summary of recent advancements in AI ethics research.")
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant providing information about AI ethics."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
        )
        result = response.choices[0].message.content.strip()
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Default web search failed: {str(e)}",
            "error_type": type(e).__name__
        }


def parse_json_output(input_data):
    """
    Parse JSON output from LLM task.
    
    Args:
        input_data: Dictionary containing the llm_output to parse
        
    Returns:
        Dictionary with parsed JSON result
    """
    llm_output = input_data.get("llm_output", "{}")
    
    # If the input is already a dictionary with result field, extract and return it
    if isinstance(llm_output, dict) and "result" in llm_output:
        return {
            "success": True,
            "result": llm_output.get("result", {}),
            "error": None
        }
    
    # If the input is a dictionary with response field (LLM output), extract it
    if isinstance(llm_output, dict) and "response" in llm_output:
        llm_output = llm_output.get("response", "{}")
            
    # Handle string output
    if isinstance(llm_output, str):
        try:
            # Try to parse the JSON
            result = json.loads(llm_output)
            return {
                "success": True,
                "result": result,
                "error": None
            }
        except json.JSONDecodeError as e:
            # If parsing fails, try to extract just the JSON part
            # Look for starting { and ending }
            start_idx = llm_output.find('{')
            end_idx = llm_output.rfind('}')
            
            if start_idx >= 0 and end_idx > start_idx:
                # Extract what looks like JSON
                json_str = llm_output[start_idx:end_idx+1]
                try:
                    result = json.loads(json_str)
                    return {
                        "success": True,
                        "result": result,
                        "error": None
                    }
                except json.JSONDecodeError:
                    pass
            
            # If we still can't parse it, return a default structure with the original text
            return {
                "success": False,
                "result": {
                    "text": llm_output,
                    "message": "Failed to parse as JSON"
                },
                "error": f"Failed to parse JSON: {str(e)}"
            }
    
    # If the input was neither a string nor a dict with expected fields
    return {
        "success": False,
        "result": None,
        "error": "Input was not in expected format"
    }


def main():
    print("Starting Final Complex Conditional Workflow Example with Fallback Logic")

    # ------------------
    # Create tasks with DirectHandlerTask for LLM tasks
    # ------------------

    # Task 1: Upload Training Document
    task1 = Task(
        task_id="upload_file_task",
        name="Upload Training Document",
        tool_name="file_upload",
        input_data={
            "file_path": os.path.join(os.path.dirname(__file__), "pdfs", "training.txt"),
            "purpose": "assistants",
        },
        next_task_id_on_success="create_vector_store_task",
    )

    # Task 2: Create Vector Store
    task2 = Task(
        task_id="create_vector_store_task",
        name="Create Vector Store",
        tool_name="vector_store_create",
        input_data={
            "name": "Training Document Store",
            "file_ids": ["${upload_file_task.output_data.result | ''}"],
        },
        next_task_id_on_success="file_search_task",
    )

    # Task 3: Extract Document Insights (File Search)
    task3 = Task(
        task_id="file_search_task",
        name="Extract Document Insights",
        tool_name="file_read",
        input_data={
            "vector_store_ids": ["${create_vector_store_task.output_data.result | ''}"],
            "query": "Extract key insights regarding AI ethics from the training document.",
            "max_num_results": 5,
            "include_search_results": True,
        },
        next_task_id_on_success="web_search_task",
        next_task_id_on_failure="regenerate_insights_task",
        condition="len(output_data.get('result', '')) > 100",
    )

    # Task 3B: Regenerate Document Insights if Task 3 output is too short
    task3b = DirectHandlerTask(
        task_id="regenerate_insights_task",
        name="Regenerate Document Insights",
        handler=llm_handler,
        input_data={
            "prompt": "The extracted insights are too short. Regenerate a more detailed summary of key insights on AI ethics from the training document."
        },
        max_retries=1,
        next_task_id_on_success="parse_regenerate_insights_task",
    )
    
    # NEW Task 3C: Parse Regenerated Insights
    task3c = DirectHandlerTask(
        task_id="parse_regenerate_insights_task",
        name="Parse Regenerated Insights",
        handler=parse_json_output,
        input_data={
            "llm_output": "${regenerate_insights_task.output_data}"
        },
        next_task_id_on_success="web_search_task",
    )

    # Task 4: Web Search for AI Ethics
    # If web search fails (e.g., times out), fallback to Task 4B.
    task4 = Task(
        task_id="web_search_task",
        name="Web Search for AI Ethics",
        tool_name="web_search",
        input_data={
            "query": "What are the latest advancements in AI ethics research?",
            "context_size": "medium",
            "user_location": {
                "type": "approximate",
                "country": "US",
                "city": "San Francisco",
                "region": "CA",
            },
        },
        next_task_id_on_success="create_summary_task",
        next_task_id_on_failure="default_web_search_task",
    )

    # Task 4B: Fallback Web Search (Default result) if Task 4 fails
    task4b = DirectHandlerTask(
        task_id="default_web_search_task",
        name="Default Web Search Result",
        handler=default_web_search_handler,
        input_data={
            "prompt": "Return a default summary of recent advancements in AI ethics research. Include key areas like auditing, education, and governance."
        },
        next_task_id_on_success="parse_default_web_search_task",
    )
    
    # NEW Task 4C: Parse Default Web Search Results
    task4c = DirectHandlerTask(
        task_id="parse_default_web_search_task",
        name="Parse Default Web Search Results",
        handler=parse_json_output,
        input_data={
            "llm_output": "${default_web_search_task.output_data}"
        },
        next_task_id_on_success="create_summary_task",
    )

    # Task 5: Generate Summary (using DirectHandlerTask)
    task5 = DirectHandlerTask(
        task_id="create_summary_task",
        name="Generate Combined Summary",
        handler=llm_handler,
        input_data={
            "prompt": """
            Create a comprehensive summary on AI ethics by combining these sources:
            
            FILE SEARCH RESULTS:
            ${file_search_task.output_data.result | 'No direct file search results available.'}
            
            REGENERATED INSIGHTS (if available):
            ${parse_regenerate_insights_task.output_data.result.text | ''}
            
            WEB SEARCH RESULTS:
            ${web_search_task.output_data.result | 'No direct web search results available.'}
            
            DEFAULT WEB SEARCH (if available):
            ${parse_default_web_search_task.output_data.result.text | ''}
            
            Synthesize these sources into a comprehensive markdown summary on the current state and future of AI ethics. Include:
            1. Key principles
            2. Recent developments
            3. Future trends
            4. Practical implications
            
            Format the output using markdown with clear headings, bullet points, and structure.
            """
        },
        next_task_id_on_success="parse_summary_task",
    )
    
    # NEW Task 5B: Parse Summary
    task5b = DirectHandlerTask(
        task_id="parse_summary_task",
        name="Parse Summary",
        handler=parse_json_output,
        input_data={
            "llm_output": "${create_summary_task.output_data}"
        },
        next_task_id_on_success="write_markdown_task",
    )

    # Task 6: Write Markdown Report
    task6 = Task(
        task_id="write_markdown_task",
        name="Write Final Markdown Report",
        tool_name="file_write",
        input_data={
            "file_path": os.path.join(os.path.dirname(__file__), "output", "ai_ethics_summary.md"),
            "content": "${parse_summary_task.output_data.result.text | ${create_summary_task.output_data.result}}",
        },
        next_task_id_on_success=None,  # End workflow
    )

    # ------------------
    # Create and Run Workflow
    # ------------------

    # Create workflow and add tasks
    workflow = Workflow(
        workflow_id="complex_conditional_workflow",
        name="Complex Conditional Workflow with Fallback Logic"
    )
    
    workflow.add_task(task1)  # Upload File
    workflow.add_task(task2)  # Create Vector Store
    workflow.add_task(task3)  # File Search
    workflow.add_task(task3b)  # Regenerate Insights (Fallback)
    workflow.add_task(task3c)  # Parse Regenerated Insights
    workflow.add_task(task4)  # Web Search
    workflow.add_task(task4b)  # Default Web Search (Fallback)
    workflow.add_task(task4c)  # Parse Default Web Search Results
    workflow.add_task(task5)  # Create Summary
    workflow.add_task(task5b)  # Parse Summary
    workflow.add_task(task6)  # Write Markdown
    
    # Check for DirectHandlerTask dependencies attribute issues
    for task_id, task in workflow.tasks.items():
        if hasattr(task, 'is_direct_handler') and task.is_direct_handler:
            # Verify no 'dependencies' attribute is mistakenly set
            if hasattr(task, 'dependencies'):
                print(f"WARNING: Task {task_id} is a DirectHandlerTask but has a 'dependencies' attribute. This is unsupported and will be removed.")
                # Remove the dependencies attribute to prevent errors
                delattr(task, 'dependencies')

    # Create agent with workflow
    agent = Agent(
        agent_id="complex_conditional_agent",
        name="Complex Conditional Workflow Agent"
    )
    agent.load_workflow(workflow)

    # Run the workflow
    print("\nExecuting workflow...")
    result = agent.run()

    # Display results
    print("\nWorkflow Execution Results:")
    print(f"Success: {result}")

    # Find the summary file
    output_file_path = os.path.join(os.path.dirname(__file__), "output", "ai_ethics_summary.md")
    if os.path.exists(output_file_path):
        print(f"\nSummary created at: {output_file_path}")
        try:
            with open(output_file_path, "r") as f:
                content = f.read()
                print("\nSummary Preview:")
                print("---------------")
                print(content[:500] + "..." if len(content) > 500 else content)
                print("---------------")
        except Exception as e:
            print(f"Error reading summary file: {e}")
    else:
        print("\nSummary file was not created.")
        
        # Display task status to debug
        failed_tasks = []
        for task_id, task in workflow.tasks.items():
            if task.status == "failed":
                failed_tasks.append(task_id)
                # Get error information
                if hasattr(task, "output_data") and task.output_data:
                    error_msg = task.output_data.get("error", "Unknown error")
                    print(f"Task {task_id} failed with error: {error_msg}")
        
        if failed_tasks:
            print(f"Failed tasks: {', '.join(failed_tasks)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error executing complex conditional workflow: {e}")
