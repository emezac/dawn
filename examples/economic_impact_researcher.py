#!/usr/bin/env python3
"""
Economic Impact Researcher Workflow

This workflow takes a research question about economic impacts, processes it through 
a Chat Planner Workflow, and generates a comprehensive Markdown report. It specifically
focuses on analyzing the global economic impact of tariffs imposed by the Trump administration.
"""
# noqa: D202

import sys
import os
import logging
import json
import re
import traceback
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Core imports
from core.workflow import Workflow
from core.task import Task, DirectHandlerTask
from core.services import get_services, reset_services, ServicesContainer  # Note: Services class doesn't exist
from core.llm.interface import LLMInterface
from core.tools.registry_access import execute_tool, tool_exists, register_tool, get_registry
from core.handlers.registry_access import get_handler, handler_exists, register_handler, get_handler_registry
from core.tools.registry import ToolRegistry
from core.handlers.registry import HandlerRegistry
from core.utils.visualizer import visualize_workflow
from core.utils.registration_manager import ensure_all_registrations

# Try to import from chat_planner_workflow
try:
    from examples.chat_planner_workflow import (
        plan_user_request_handler,
        validate_plan_handler,
        plan_to_tasks_handler,
        execute_dynamic_tasks_handler,
        summarize_results_handler
    )
except ImportError as e:
    logging.error(f"Failed to import handlers from chat_planner_workflow: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("economic_impact_researcher")

# Define a local Step class for clarity in workflow construction
class Step:
    def __init__(self, name, task_type="handler", **kwargs):
        self.name = name
        self.task_type = task_type
        self.kwargs = kwargs
        
    def __str__(self):
        return f"Step({self.name}, {self.task_type})"

# Initial research prompt
INITIAL_RESEARCH_PROMPT = """
I need a comprehensive research report on the global economic impact of tariffs imposed by the Trump administration. 
Please investigate:

1. Which countries were most affected and how?
2. What was the impact on trade volumes between the US and those countries?
3. What retaliatory measures were taken by those countries?
4. How did these tariffs impact US manufacturing and agriculture sectors?
5. What were the effects on global supply chains?
6. What are the long-term geopolitical implications of these trade policies?

Tools available for your use:
- web_search: search for relevant information
- analyze_text: analyze and extract insights from text
- write_markdown: format findings into a well-structured document

Please return a well-organized Markdown report with:
- Executive summary
- Detailed findings for each aspect
- Economic data and statistics
- Geopolitical analysis
- Conclusions and long-term outlook
"""  # noqa: D202

# Function to fix JSON from LLM output
def fix_json_from_llm(llm_output: str) -> Optional[str]:
    """Extract and fix JSON from LLM output."""
    logger.debug(f"Attempting to fix JSON from LLM output: {llm_output[:100]}...")
    
    # Try to extract JSON using regex patterns
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', llm_output)
    if json_match:
        json_str = json_match.group(1)
    else:
        # Try to find JSON without code blocks, looking for array pattern
        json_match = re.search(r'\[\s*\{[\s\S]*\}\s*\]', llm_output)
        if json_match:
            json_str = json_match.group(0)
        else:
            logger.warning("Could not find JSON pattern in LLM output")
            return None
    
    # Try to clean common JSON formatting issues
    try:
        # Replace unquoted property names
        json_str = re.sub(r'(\s*)(\w+)(\s*):', r'\1"\2"\3:', json_str)
        
        # Fix missing commas between objects
        json_str = re.sub(r'(\})\s*(\{)', r'\1,\2', json_str)
        
        # Fix trailing commas
        json_str = re.sub(r',(\s*[\]}])', r'\1', json_str)
        
        # Fix missing brackets
        if not json_str.strip().startswith('['):
            json_str = '[' + json_str
        if not json_str.strip().endswith(']'):
            json_str = json_str + ']'
        
        # Parse and re-encode to ensure valid JSON
        parsed = json.loads(json_str)
        return json.dumps(parsed, indent=2)
    
    except Exception as e:
        logger.error(f"Error fixing JSON: {e}")
        # Save debug info
        debug_file = f"debug_json_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(debug_file, "w") as f:
            f.write(f"Original LLM output:\n{llm_output}\n\nExtracted JSON:\n{json_str}\n\nError: {e}")
        logger.info(f"Debug info saved to {debug_file}")
        return None

# Create fallback plan if JSON parsing fails
def create_fallback_plan() -> List[Dict[str, Any]]:
    """Create a fallback plan with basic steps if JSON parsing fails."""
    logger.info("Creating fallback plan...")
    return [
        {
            "step_id": "search_step",
            "description": "Search for information about the economic impact of Trump tariffs",
            "type": "tool",
            "name": "web_search",
            "inputs": {
                "query": "economic impact tariffs Trump countries affected"
            },
            "outputs": ["search_results"],
            "depends_on": []
        },
        {
            "step_id": "analyze_step",
            "description": "Analyze search results and extract key insights",
            "type": "handler",
            "name": "analyze_text_handler",
            "inputs": {
                "text": "${search_step.result}",
                "analysis_type": "economic_impact"
            },
            "outputs": ["analysis_results"],
            "depends_on": ["search_step"]
        },
        {
            "step_id": "report_step",
            "description": "Write a final report based on the analysis",
            "type": "tool",
            "name": "write_markdown",
            "inputs": {
                "content": "${analyze_step.result}",
                "title": "Economic Impact of Trump Tariffs"
            },
            "outputs": ["final_report"],
            "depends_on": ["analyze_step"]
        }
    ]

# Custom handler wrappers to ensure correct inputs/outputs
def get_available_capabilities_tool(input_data: dict = None) -> dict:
    """Tool to retrieve available tools and handlers in the system.
    
    Returns information about tools, handlers, and system info.
    """
    tools_registry = get_registry()
    handlers_registry = get_handler_registry()
    
    available_tools = list(tools_registry.tools.keys())
    available_handlers = handlers_registry.list_handlers()
    
    # Include system information
    system_info = {
        "python_version": sys.version,
        "timestamp": datetime.now().isoformat(),
        "framework_version": "dawn-0.1"
    }
    
    return {
        "available_tools": available_tools,
        "available_handlers": available_handlers,
        "system_info": system_info
    }

def register_required_planner_handlers():
    """Register all required handlers for the Chat Planner Workflow."""
    # Ensure handlers exist
    if not handler_exists("plan_user_request"):
        logger.info("Registering plan_user_request handler")
        register_handler("plan_user_request", plan_user_request_handler)
    
    if not handler_exists("validate_plan"):
        logger.info("Registering validate_plan handler")
        register_handler("validate_plan", validate_plan_handler)
    
    if not handler_exists("plan_to_tasks"):
        logger.info("Registering plan_to_tasks handler")
        register_handler("plan_to_tasks", plan_to_tasks_handler)
    
    if not handler_exists("execute_dynamic_tasks"):
        logger.info("Registering execute_dynamic_tasks handler")
        register_handler("execute_dynamic_tasks", execute_dynamic_tasks_handler)
    
    if not handler_exists("summarize_results"):
        logger.info("Registering summarize_results handler")
        register_handler("summarize_results", summarize_results_handler)
    
    # Register necessary tools
    if not tool_exists("get_available_capabilities"):
        logger.info("Registering get_available_capabilities tool")
        register_tool("get_available_capabilities", get_available_capabilities_tool)

def summarize_results_task(task: Task, input_data: dict) -> dict:
    """Summarize the results of the research workflow."""
    research_results = input_data.get("research_results", "No results available")
    summary = f"# Economic Impact Research Report\n\n{research_results}"
    
    # Save the report to a file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("reports", exist_ok=True)
    report_path = f"reports/economic_impact_report_{timestamp}.md"
    
    with open(report_path, "w") as f:
        f.write(summary)
    
    return {
        "success": True,
        "result": summary,
        "report_path": report_path
    }

def main():
    """Main entry point for the Economic Impact Researcher workflow."""
    try:
        # Get request from command line if provided
        import sys
        user_request = INITIAL_RESEARCH_PROMPT
        if len(sys.argv) > 1:
            user_request = sys.argv[1]
            print(f"Using provided request: {user_request}")
        
        # Reset services for a clean start
        reset_services()
        
        # Initialize services and LLM interface
        services = get_services()
        llm_interface = LLMInterface(
            model="gpt-4o-mini"
        )
        
        # Register LLM interface with the services container
        services.register_llm_interface(llm_interface, "default_llm")
        
        # Set up the request
        user_request = INITIAL_RESEARCH_PROMPT
        
        # Register standard tools
        ensure_all_registrations()
        
        # Register Chat Planner handlers
        register_required_planner_handlers()
        
        # Log registered tools and handlers
        tools_registry = get_registry()
        handlers_registry = get_handler_registry()
        
        logger.info(f"Registered tools: {list(tools_registry.tools.keys())}")
        logger.info(f"Registered handlers: {list(handlers_registry.list_handlers())}")
        
        # Check if planner handlers are available
        for handler_name in ["plan_user_request", "validate_plan", "plan_to_tasks", 
                           "execute_dynamic_tasks", "summarize_results"]:
            if handler_exists(handler_name):
                logger.info(f"Handler '{handler_name}' is available")
            else:
                logger.error(f"Handler '{handler_name}' is NOT available")
        
        # Check if planner tools are available
        if tool_exists("get_available_capabilities"):
            logger.info("Tool 'get_available_capabilities' is available")
        else:
            logger.error("Tool 'get_available_capabilities' is NOT available")
            
        # Build Chat Planner Workflow
        workflow = Workflow(workflow_id="economic_impact_workflow", name="Economic Impact Research Workflow")
        
        # Create and add tasks to the workflow
        plan_task = DirectHandlerTask(
            task_id="plan_step",
            name="Plan User Request",
            handler_name="plan_user_request",
            input_data={
                "user_request": user_request,
                "available_tools_context": "web_search, analyze_text, write_markdown",
                "available_handlers_context": "analyze_text_handler"
            }
        )
        workflow.add_task(plan_task)

        validate_task = DirectHandlerTask(
            task_id="validate_step",
            name="Validate Plan",
            handler_name="validate_plan",
            input_data={
                "plan_json": "${plan_step.result.plan_json}",
                "user_request": user_request
            },
            depends_on=["plan_step"]
        )
        workflow.add_task(validate_task)

        tasks_task = DirectHandlerTask(
            task_id="tasks_step",
            name="Plan to Tasks",
            handler_name="plan_to_tasks",
            input_data={
                "plan_json": "${validate_step.result.valid_plan_json}",
                "user_request": user_request
            },
            depends_on=["validate_step"]
        )
        workflow.add_task(tasks_task)

        execute_task = DirectHandlerTask(
            task_id="execute_step",
            name="Execute Dynamic Tasks",
            handler_name="execute_dynamic_tasks",
            input_data={
                "tasks": "${tasks_step.result.tasks}",
                "user_request": user_request
            },
            depends_on=["tasks_step"]
        )
        workflow.add_task(execute_task)

        summary_task = DirectHandlerTask(
            task_id="summary_step",
            name="Summarize Results",
            handler_name="summarize_results",
            input_data={
                "results": "${execute_step.result.results}",
                "user_request": user_request
            },
            depends_on=["execute_step"]
        )
        workflow.add_task(summary_task)
        
        # Visualize workflow
        visualize_workflow(workflow, filename="economic_impact_workflow", view=False)
        
        # Initialize workflow engine
        workflow_engine = services.create_workflow_engine(
            workflow=workflow
        )
        
        # Initial input for the workflow
        initial_input = {"user_request": user_request}
        
        # Run the workflow
        logger.info(f"Running workflow with input: {initial_input}")
        result = workflow_engine.execute(initial_input=initial_input)
        
        if result.get("success", False):
            logger.info("Workflow executed successfully")
            report_path = result.get("summary_step", {}).get("result", {}).get("report_path", "")
            if report_path and os.path.exists(report_path):
                logger.info(f"Report generated at: {report_path}")
                print(f"\nReport generated at: {report_path}\n")
            else:
                logger.warning(f"Report path not found: {report_path}")
        else:
            logger.error(f"Workflow execution failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        logger.error(traceback.format_exc())
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 