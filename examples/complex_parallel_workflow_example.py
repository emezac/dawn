import asyncio
import os
import sys
import json
from typing import Dict, Any, List, Optional, Union, TypedDict, Literal
from datetime import datetime
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

from core.agent import Agent
from core.task import Task, DirectHandlerTask, TaskOutput
from core.tools.registry import ToolRegistry
from core.utils.visualizer import visualize_workflow
from core.utils.variable_resolver import resolve_variables
from core.utils.data_validator import validate_data, ValidationError
from core.workflow import Workflow
from core.tools.registry_access import get_registry, register_tool

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

# Define TypedDict structures for data validation
class FileUploadResult(TypedDict):
    """TypedDict for file upload results."""
    file_id: str
    filename: str
    status: str


class VectorStoreResult(TypedDict):
    """TypedDict for vector store results."""
    id: str
    name: str
    document_count: int


class SearchResult(TypedDict):
    """TypedDict for search results."""
    content: str
    relevance: float
    source: str


class FileSearchResults(TypedDict):
    """TypedDict for file search results."""
    matches: List[SearchResult]
    query: str
    total_results: int


class WebSearchResults(TypedDict):
    """TypedDict for web search results."""
    snippets: List[Dict[str, Any]]
    query: str
    status: str


# Define handler functions for direct handler tasks
def regenerate_insights_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate insights when file search fails.
    
    Args:
        input_data: Dictionary containing VS ID and other details
        
    Returns:
        Dictionary with generated insights
    """
    # Extract vector store id from input
    vs_id = input_data.get("vector_store_id", "")
    
    # Generate insights as fallback
    insights = (
        "# AI Ethics Key Insights\n\n"
        "## Fairness and Bias\n"
        "- AI systems should be designed to avoid unfair bias\n"
        "- Rigorous testing for biases across different demographic groups\n\n"
        "## Transparency\n"
        "- AI decision-making processes should be explainable\n"
        "- Users should understand when they are interacting with AI\n\n"
        "## Privacy\n"
        "- AI systems should respect user privacy\n"
        "- Data collection should be minimized to what's necessary\n\n"
        "## Safety and Security\n"
        "- AI systems should be robust against attacks\n"
        "- Regular security auditing and testing\n\n"
        "## Accountability\n"
        "- Clear responsibility for AI actions\n"
        "- Mechanisms for redress when AI causes harm\n\n"
        f"*Note: These are fallback insights as vector store {vs_id} retrieval failed.*"
    )
    
    return {
        "success": True,
        "result": {
            "insights": insights,
            "source": "fallback_generation",
            "is_regenerated": True
        }
    }


def default_web_search_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Provide default web search results when search fails.
    
    Args:
        input_data: Dictionary containing context information
        
    Returns:
        Dictionary with default search results
    """
    # Generate default search results as fallback
    search_results = (
        "# Recent Advancements in AI Ethics\n\n"
        "## New Regulatory Frameworks\n"
        "- EU AI Act introduces risk-based regulations\n"
        "- US Executive Order on Trustworthy AI establishes guidelines\n\n"
        "## Auditing Tools\n"
        "- New open-source tools for algorithmic auditing\n"
        "- Standardized benchmarks for fairness evaluations\n\n"
        "## Educational Initiatives\n"
        "- Increased focus on ethics in AI curricula\n"
        "- Professional certification programs for responsible AI\n\n"
        "## Governance Models\n"
        "- Multi-stakeholder oversight boards\n"
        "- Participatory design approaches involving affected communities\n\n"
        "*Note: These are default results as web search failed.*"
    )
    
    return {
        "success": True,
        "result": {
            "search_results": search_results,
            "source": "default_generation",
            "topics": ["regulation", "auditing", "education", "governance"]
        }
    }


def generate_summary_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a comprehensive summary from all sources.
    
    Args:
        input_data: Dictionary containing insights from different sources
        
    Returns:
        Dictionary with generated summary
    """
    # Extract inputs with proper validation
    doc_insights = input_data.get("doc_insights", "No document insights available")
    regenerated_insights = input_data.get("regenerated_insights", "")
    web_results = input_data.get("web_results", "No web results available")
    default_web_results = input_data.get("default_web_results", "")
    
    # Check which sources were used
    used_primary_doc = len(doc_insights) > 50 and "No document insights available" not in doc_insights
    used_regenerated_doc = len(regenerated_insights) > 50
    used_primary_web = len(web_results) > 50 and "No web results available" not in web_results
    used_default_web = len(default_web_results) > 50
    
    # Build source list for citation
    sources = []
    if used_primary_doc:
        sources.append("Primary Document Analysis")
    if used_regenerated_doc:
        sources.append("Regenerated Document Analysis")
    if used_primary_web:
        sources.append("Web Search Results")
    if used_default_web:
        sources.append("Default Web Knowledge")
    
    # Generate summary
    summary = "# Comprehensive AI Ethics Summary\n\n"
    
    # Add source explanation
    summary += "## Sources Used\n"
    for source in sources:
        summary += f"- {source}\n"
    summary += "\n"
    
    # Add document insights section
    summary += "## Document Analysis\n"
    if used_primary_doc:
        summary += doc_insights[:500] + "...\n\n"
    elif used_regenerated_doc:
        summary += "*Primary document analysis failed. Using regenerated insights:*\n\n"
        summary += regenerated_insights[:500] + "...\n\n"
    else:
        summary += "*No document insights available*\n\n"
    
    # Add web search section
    summary += "## Web Research\n"
    if used_primary_web:
        summary += web_results[:500] + "...\n\n"
    elif used_default_web:
        summary += "*Web search failed. Using default knowledge:*\n\n"
        summary += default_web_results[:500] + "...\n\n"
    else:
        summary += "*No web research available*\n\n"
    
    # Add recommendations section based on combined insights
    summary += "## Key Recommendations\n"
    
    # Generate some basic recommendations based on available data
    recommendations = [
        "1. **Implement Robust Fairness Testing**: Regularly test AI systems for bias and fairness issues.",
        "2. **Ensure Transparency**: Document AI decision-making processes and make them explainable to users.",
        "3. **Data Minimization**: Collect only necessary data and implement strong privacy protections.",
        "4. **Ongoing Monitoring**: Continuously monitor AI systems in production for emerging issues."
    ]
    
    for rec in recommendations:
        summary += f"{rec}\n"
        
    # Add timestamp
    summary += f"\n\n*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
    
    return {
        "success": True,
        "result": summary,
        "metadata": {
            "sources_used": sources,
            "timestamp": datetime.now().isoformat()
        }
    }


def parse_llm_json_output(input_data):
    """Parse JSON output from LLM task"""
    llm_output = input_data.get("llm_output", "{}")
    
    # If the input is already a dictionary, use it directly
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
            
            # If we still can't parse it, return the error
            return {
                "success": False,
                "result": None,
                "error": f"Failed to parse JSON: {str(e)}"
            }
    
    # If the input was neither a string nor a dict with 'response'
    return {
        "success": False,
        "result": None,
        "error": "Input was not in expected format"
    }


def main():
    """Run the complex parallel workflow example."""
    # Set timestamp for unique workflow ID
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    print("Starting Complex Parallel Workflow Example")
    print("==========================================")
    
    # --- Setup ---
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    # Get the singleton registry
    registry = get_registry()
    
    # --- Create Vector Stores ---
    print("\nCreating vector stores...")
    try:
        # Create AI Ethics vector store
        vs_create_result = registry.execute_tool("create_vector_store", {"name": f"AI Ethics Resources {timestamp}"})
        if vs_create_result and vs_create_result.get("success"):
            ai_ethics_vs_id = vs_create_result.get("result")
            print(f"AI Ethics vector store created with ID: {ai_ethics_vs_id}")
        else:
            print(f"Failed to create vector store: {vs_create_result.get('error', 'Unknown error')}")
            ai_ethics_vs_id = None
    except Exception as e:
        print(f"Error creating vector store: {e}")
        ai_ethics_vs_id = None
    
    # --- Create and Configure Workflow ---
    print("\nCreating workflow...")
    workflow = Workflow(
        workflow_id=f"complex_parallel_workflow_{timestamp}",
        name="Complex Parallel Workflow with Error Handling"
    )
    
    # Task 1: Upload Document to VectorDB
    task1 = Task(
        task_id="upload_document_task",
        name="Upload AI Ethics Document",
        tool_name="file_upload",
        input_data={
            # Create the content inline if the file doesn't exist
            "file_content": """# Principles of AI Ethics

## Fairness
AI systems should treat all people fairly and not discriminate based on race, gender, age, or other protected characteristics.

## Transparency
AI systems should operate in a transparent manner. Users should be informed when they are interacting with AI.

## Privacy and Security
AI systems should respect user privacy and be secure. Personal data should be protected.

## Human Oversight
AI systems should be designed to enable human oversight and control.

## Accountability
Organizations developing and deploying AI should be accountable for their systems' impacts.

## Reliability and Safety
AI systems should operate reliably and safely.

## Social and Environmental Well-being
The broader societal and environmental impacts of AI should be considered throughout the system's lifecycle.
""",
            "file_name": "ai_ethics_example.txt",
            "purpose": "vector_db"
        },
        next_task_id_on_success="create_vector_store_task",
        next_task_id_on_failure=None,  # End workflow on failure
    )
    workflow.add_task(task1)
    
    # Task 2: Create Vector Store with Uploaded Document
    task2 = Task(
        task_id="create_vector_store_task",
        name="Create AI Ethics Vector Store",
        tool_name="add_file_to_vector_store",
        input_data={
            "vector_store_id": ai_ethics_vs_id,
            "file_id": "${upload_document_task.output_data.result}",
        },
        next_task_id_on_success="file_search_task",
        next_task_id_on_failure=None,  # End workflow on failure
    )
    workflow.add_task(task2)
    
    # --- Branch 1 (starts with Task 3) ---
    
    # Task 3: File Search (Main Path)
    task3 = Task(
        task_id="file_search_task",
        name="Search AI Ethics Document",
        tool_name="file_read",
        input_data={
            "vector_store_ids": [ai_ethics_vs_id],
            "query": "Key principles of AI ethics and fairness",
            "max_num_results": 5,
        },
        next_task_id_on_success="web_search_task",  # Continue to web search
        next_task_id_on_failure="regenerate_insights_task",  # Fallback path on failure
        parallel=True,  # Start branch 1
        condition="output_data.get('result', '') != '' and len(output_data.get('result', '')) > 100",
    )
    workflow.add_task(task3)
    
    # Task 3b: Regenerate Insights (Fallback for File Search)
    task3b = DirectHandlerTask(
        task_id="regenerate_insights_task",
        name="Regenerate AI Ethics Insights",
        handler=regenerate_insights_handler,
        input_data={
            "vector_store_id": ai_ethics_vs_id,
        },
        next_task_id_on_success="web_search_task",  # Continue to web search after regeneration
    )
    workflow.add_task(task3b)
    
    # --- Branch 2 (Task 4 runs in parallel with Branch 1) ---
    
    # Task 4: Web Search (Main Path)
    task4 = Task(
        task_id="web_search_task",
        name="Search Web for AI Ethics Updates",
        tool_name="web_search",
        input_data={
            "query": "Latest developments in AI ethics guidelines",
        },
        next_task_id_on_success="wait_for_searches",  # Wait for both branches
        next_task_id_on_failure="default_web_search_task",  # Fallback path on failure
        parallel=True,  # Run in parallel with Branch 1
    )
    workflow.add_task(task4)
    
    # Task 4b: Default Web Search (Fallback for Web Search)
    task4b = DirectHandlerTask(
        task_id="default_web_search_task",
        name="Generate Default AI Ethics Updates",
        handler=default_web_search_handler,
        input_data={
            "context": "AI ethics guidelines and regulations",
        },
        next_task_id_on_success="wait_for_searches",  # Wait for both branches
    )
    workflow.add_task(task4b)
    
    # Task 5: Wait and Collect Results from Both Branches
    task5 = Task(
        task_id="wait_for_searches",
        name="Wait for All Search Results",
        tool_name="noop",  # No operation, just a synchronization point
        input_data={},
        next_task_id_on_success="generate_summary_task",  # Continue to summary generation
    )
    workflow.add_task(task5)
    
    # Task 6: Generate Summary
    task6 = DirectHandlerTask(
        task_id="generate_summary_task",
        name="Generate Comprehensive Summary",
        handler=generate_summary_handler,
        input_data={
            # Check both main and fallback paths for document insights
            "doc_insights": "${file_search_task.output_data.result | ''}",
            "regenerated_insights": "${regenerate_insights_task.output_data.result.insights | ''}",
            
            # Check both main and fallback paths for web search results
            "web_results": "${web_search_task.output_data.result | ''}",
            "default_web_results": "${default_web_search_task.output_data.result.search_results | ''}",
        },
        next_task_id_on_success="parse_summary_task",
    )
    workflow.add_task(task6)
    
    # NEW Task: Parse Summary Output
    task6b = DirectHandlerTask(
        task_id="parse_summary_task",
        name="Parse Summary Output",
        handler=parse_llm_json_output,
        input_data={
            "llm_output": "${generate_summary_task.output_data}"
        },
        next_task_id_on_success="write_report_task",
    )
    workflow.add_task(task6b)
    
    # Task 7: Write Final Report
    task7 = Task(
        task_id="write_report_task",
        name="Write Final Report to File",
        tool_name="file_write",
        input_data={
            "file_path": f"ai_ethics_report_{timestamp}.md",
            "content": "${parse_summary_task.output_data.result | ${generate_summary_task.output_data.result}}",
        },
    )
    workflow.add_task(task7)
    
    # --- Create Agent and Load Workflow ---
    print("\nCreating agent and loading workflow...")
    agent = Agent(
        agent_id=f"complex_parallel_agent_{timestamp}",
        name="Complex Parallel Workflow Agent",
        tool_registry=registry
    )
    
    # Check for DirectHandlerTask dependencies attribute issues
    for task_id, task in workflow.tasks.items():
        if hasattr(task, 'is_direct_handler') and task.is_direct_handler:
            # Verify no 'dependencies' attribute is mistakenly set
            if hasattr(task, 'dependencies'):
                print(f"WARNING: Task {task_id} is a DirectHandlerTask but has a 'dependencies' attribute. This is unsupported and will be removed.")
                # Remove the dependencies attribute to prevent errors
                delattr(task, 'dependencies')
    
    agent.load_workflow(workflow)
    
    # --- Execute Workflow ---
    print("\nExecuting workflow...")
    print("=====================")
    result = agent.run()
    
    # --- Display Results ---
    print("\nWorkflow execution completed.")
    print(f"Success: {result}")
    
    # Display task results
    print("\nTask Results:")
    for task_id, task in workflow.tasks.items():
        status = task.status
        print(f"  - {task.name} ({task_id}): {status}")
        
        if status == "completed":
            # Use extract_task_output to get meaningful output
            output = extract_task_output(task.output_data)
            if output:
                # Limit output size for display
                if isinstance(output, str):
                    print(f"    Output: {output[:100]}...")
                else:
                    print(f"    Output: {str(output)[:100]}...")
    
    # Find the report file path
    report_task = workflow.tasks.get("write_report_task")
    if report_task and report_task.status == "completed":
        report_path = extract_task_output(report_task.output_data, "result")
        print(f"\nFinal report written to: {report_path}")
        
        # Optionally, display report content
        try:
            with open(report_path, 'r') as f:
                content = f.read()
                print("\nReport Preview:")
                print("---------------")
                print(f"{content[:500]}...")
                print("---------------")
        except Exception as e:
            print(f"Error reading report: {e}")
    
    print("\nWorkflow execution complete!")


# --- Script Entry Point ---
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print(f"ERROR: An exception occurred while running the script: {e}")
        print(traceback.format_exc())
