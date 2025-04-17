#!/usr/bin/env python3
"""
Dynamic Input Query Workflow.

This workflow accepts a user-defined query topic, performs a search for relevant information,
analyzes the findings, and generates a comprehensive executive report.
"""  # noqa: D202

import sys
import os
import logging
import json
import re
import jsonschema
from typing import Dict, Any, List
import argparse
from datetime import datetime

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Core imports
from core.workflow import Workflow
from core.task import Task, DirectHandlerTask
from core.services import get_services, reset_services
from core.llm.interface import LLMInterface
from core.tools.registry_access import execute_tool, tool_exists, register_tool
from core.handlers.registry_access import get_handler, handler_exists, register_handler
from core.tools.registry import ToolRegistry
from core.handlers.registry import HandlerRegistry
from core.tools.framework_tools import get_available_capabilities
from core.utils.visualizer import visualize_workflow
from core.utils.registration_manager import ensure_all_registrations
from tools.web_search_tool import WebSearchTool

# Define ToolInvocation class directly
class ToolInvocation:
    """Placeholder for ToolInvocation."""
    def __init__(self, **kwargs):
        self.parameters = kwargs.get("parameters", {})
        for key, value in kwargs.items():
            setattr(self, key, value)

# Example-specific imports
from examples.chat_planner_config import ChatPlannerConfig  # Reusing the config structure

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("dynamic_input_query_flow")

# Define WorkflowStatus enum
class WorkflowStatus:
    """Enum for workflow status values."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

# Import handlers from chat_planner_workflow
from examples.chat_planner_workflow import (
    plan_user_request_handler,
    validate_plan_handler,
    plan_to_tasks_handler,
    execute_dynamic_tasks_handler,
    summarize_results_handler,
    process_clarification_handler,
    await_input_handler,
    check_clarification_needed_default_handler
)

# --- JSON Schema for the Plan ---
PLAN_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "step_id": {"type": "string", "minLength": 1},
            "description": {"type": "string"},
            "type": {"type": "string", "enum": ["tool", "handler"]},
            "name": {"type": "string", "minLength": 1},
            "inputs": {"type": "object", "additionalProperties": True},
            "outputs": {"type": "array", "items": {"type": "string"}},
            "depends_on": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["step_id", "description", "type", "name", "inputs", "depends_on"],
        "additionalProperties": False
    },
    "description": "A list of steps defining the execution plan."
}

# --- Dynamic Query Specific Tools and Handlers ---
def dynamic_topic_search_tool(task: ToolInvocation) -> dict:
    """
    Performs targeted search for information about any user-defined topic.
    
    Args:
        task: The task object containing search parameters
    
    Returns:
        Dictionary with search results focusing on the requested topic
    """
    try:
        # Extract parameters
        query = task.parameters.get("query", "")
        focus_areas = task.parameters.get("focus_areas", ["key facts", "trends", "statistics"])
        
        if not query:
            return {
                "success": False,
                "error": "No query provided for search"
            }
        
        # Enhance query with focus areas
        enhanced_query = query
        if "key facts" in focus_areas:
            enhanced_query += " key facts important information"
        if "trends" in focus_areas:
            enhanced_query += " latest trends developments"
        if "statistics" in focus_areas:
            enhanced_query += " statistics data numbers"
        
        logger.info(f"Performing dynamic topic search with query: {enhanced_query}")
        
        # Use web search tool
        try:
            web_search_tool = WebSearchTool()
            result_text = web_search_tool.perform_search(enhanced_query)
            
            # Parse and structure the results
            search_results = {
                "query": enhanced_query,
                "timestamp": datetime.now().isoformat(),
                "results": [{
                    "content": result_text,
                    "title": f"Search Results: {query}",
                    "url": "https://search-results.com/dynamic-query"
                }],
                "focus_areas": focus_areas
            }
            
            return {
                "success": True,
                "result": search_results
            }
        except Exception as e:
            logger.warning(f"Web search failed: {e}, using fallback data")
            # Fallback to simple message
            return {
                "success": False,
                "error": f"Search failed: {str(e)}. Please try a different query."
            }
    except Exception as e:
        logger.error(f"Error in dynamic_topic_search_tool: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to perform search: {str(e)}"
        }

def analyze_search_results_handler(task: DirectHandlerTask, input_data: dict) -> dict:
    """
    Analyzes search results on any topic and extracts key insights.
    
    Args:
        task: The task object
        input_data: Dictionary containing search results
    
    Returns:
        Dictionary with analysis of the search results
    """
    search_data = input_data.get("search_data", {})
    search_results = []
    
    # Extract search results
    if isinstance(search_data, dict) and "results" in search_data:
        for result in search_data["results"]:
            if "content" in result:
                search_results.append(result["content"])
    elif isinstance(search_data, list):
        search_results = search_data
    
    if not search_results:
        return {
            "success": False,
            "error": "No search results found to analyze"
        }
    
    logger.info(f"Analyzing search data from {len(search_results)} results")
    
    # Extract the main query
    query = ""
    if isinstance(search_data, dict) and "query" in search_data:
        query = search_data["query"]
    
    # Extract key insights
    key_insights = []
    main_topics = []
    statistics = []
    trends = []
    
    # Analyze the search results
    all_content = " ".join(search_results)
    
    # Extract potential statistics (numbers with context)
    stat_matches = re.findall(r'(\d+(?:\.\d+)?%|\d+(?:,\d+)+|\d+\s+(?:million|billion|trillion))', all_content)
    if stat_matches:
        for stat in stat_matches[:5]:  # Limit to 5 statistics
            # Find the context around this statistic
            context_pattern = r'[^.!?]*' + re.escape(stat) + r'[^.!?]*[.!?]'
            context_matches = re.findall(context_pattern, all_content)
            if context_matches:
                statistics.append(context_matches[0].strip())
    
    # Identify main topics by looking for repeated phrases or capitalized terms
    capitalized_phrases = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})', all_content)
    if capitalized_phrases:
        # Count occurrences
        from collections import Counter
        phrase_counter = Counter(capitalized_phrases)
        main_topics = [topic for topic, count in phrase_counter.most_common(5)]
    
    # For trends, look for phrases like "increasing", "growing", "declining", etc.
    trend_indicators = ["increase", "decrease", "grow", "decline", "rise", "fall", "trend", "shift", "change"]
    for indicator in trend_indicators:
        pattern = r'[^.!?]*\b' + indicator + r'[a-z]*\b[^.!?]*[.!?]'
        trend_matches = re.findall(pattern, all_content, re.IGNORECASE)
        if trend_matches:
            trends.extend(trend_matches[:2])  # Limit to 2 trends per indicator
    
    # Limit the number of trends
    trends = trends[:5]
    
    # Compile key insights from the most relevant sentences
    from collections import Counter
    words = re.findall(r'\b[a-zA-Z]{3,}\b', query.lower())
    word_counter = Counter(words)
    query_keywords = [word for word, _ in word_counter.most_common(5)]
    
    # Find sentences containing query keywords
    sentences = re.split(r'(?<=[.!?])\s+', all_content)
    for sentence in sentences:
        if any(keyword in sentence.lower() for keyword in query_keywords):
            key_insights.append(sentence.strip())
    
    # Limit key insights
    key_insights = key_insights[:7]
    
    return {
        "success": True,
        "result": {
            "query": query,
            "key_insights": key_insights,
            "main_topics": main_topics,
            "statistics": statistics,
            "trends": trends,
            "analysis_timestamp": datetime.now().isoformat()
        }
    }

def generate_executive_report_handler(task: DirectHandlerTask, input_data: dict) -> dict:
    """
    Generates a comprehensive executive report based on the analysis results.
    
    Args:
        task: The task object
        input_data: Dictionary containing analysis results
    
    Returns:
        Dictionary with formatted executive report
    """
    analysis_data = input_data.get("analysis_data", {})
    query = input_data.get("query", "Topic Analysis")
    
    if not analysis_data or not isinstance(analysis_data, dict):
        return {
            "success": False,
            "error": "No valid analysis data provided for report generation"
        }
    
    # Format the current date
    today = datetime.now().strftime("%B %d, %Y")
    
    # Extract data from the analysis
    key_insights = analysis_data.get("key_insights", [])
    main_topics = analysis_data.get("main_topics", [])
    statistics = analysis_data.get("statistics", [])
    trends = analysis_data.get("trends", [])
    
    # Generate the report
    report = []
    
    # Title and introduction
    report.append(f"# Executive Report: {query}")
    report.append(f"\nPrepared: {today}")
    report.append(f"\n## Executive Summary")
    
    # Add a brief summary
    summary = "This report provides an analysis of information gathered on the topic: "
    summary += f"**{query}**. "
    summary += "It includes key insights, main topics, relevant statistics, and emerging trends."
    report.append(f"\n{summary}")
    
    # Key Insights Section
    if key_insights:
        report.append("\n## Key Insights")
        for insight in key_insights:
            report.append(f"\n- {insight}")
    
    # Main Topics Section
    if main_topics:
        report.append("\n## Main Topics Identified")
        for topic in main_topics:
            report.append(f"\n- {topic}")
    
    # Statistics Section
    if statistics:
        report.append("\n## Notable Statistics")
        for stat in statistics:
            report.append(f"\n- {stat}")
    
    # Trends Section
    if trends:
        report.append("\n## Emerging Trends")
        for trend in trends:
            report.append(f"\n- {trend}")
    
    # Recommendations Section
    report.append("\n## Recommendations")
    report.append("\nBased on the analysis, we recommend:")
    report.append("\n1. Further in-depth research on the main topics identified")
    report.append("\n2. Monitoring emerging trends to understand future developments")
    report.append("\n3. Validating statistics from additional sources for accuracy")
    report.append("\n4. Developing action plans to address key insights")
    
    # Conclusion
    report.append("\n## Conclusion")
    report.append("\nThis report provides a preliminary analysis based on available information.")
    report.append("For more detailed insights, additional focused research may be necessary.")
    
    # Convert list to string
    report_text = "\n".join(report)
    
    # Determine output path for saving report
    output_path = f"executive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    logger.info(f"Generated executive report on: {query}")
    
    return {
        "success": True,
        "result": {
            "report": report_text,
            "summary": f"Executive Report on: {query}",
            "output_path": output_path
        }
    }

# --- Dynamic Input and Query Workflow ---
def build_dynamic_input_query_workflow():
    """
    Builds the dynamic input query workflow.
    """
    workflow = Workflow(
        workflow_id="dynamic_input_query",
        name="Dynamic Input Query Analyzer"
    )

    # Step 1: Await User Input
    await_input_task = DirectHandlerTask(
        task_id="get_user_query",
        name="Get User Query Input",
        handler_name="await_input_handler",
        input_data={
            "prompt_context": "Please enter a topic or question you would like to research:",
            "input_type": "text"
        },
        next_task_id_on_success="search_topic",
        description="Gets the user's query input."
    )
    workflow.add_task(await_input_task)

    # Step 2: Search for Information
    search_task = Task(
        task_id="search_topic",
        name="Search for Topic Information",
        tool_name="dynamic_topic_search",
        input_data={
            "query": "${get_user_query.result.user_input}",
            "focus_areas": ["key facts", "trends", "statistics"]
        },
        next_task_id_on_success="analyze_results",
        description="Searches for information on the user's topic."
    )
    workflow.add_task(search_task)

    # Step 3: Analyze Search Results
    analyze_task = DirectHandlerTask(
        task_id="analyze_results",
        name="Analyze Search Results",
        handler_name="analyze_search_results_handler",
        input_data={
            "search_data": "${search_topic.result}",
            "query": "${get_user_query.result.user_input}"
        },
        next_task_id_on_success="generate_report",
        description="Analyzes the search results."
    )
    workflow.add_task(analyze_task)

    # Step 4: Generate Executive Report
    report_task = DirectHandlerTask(
        task_id="generate_report",
        name="Generate Executive Report",
        handler_name="generate_executive_report_handler",
        input_data={
            "analysis_data": "${analyze_results.result}",
            "query": "${get_user_query.result.user_input}"
        },
        next_task_id_on_success=None,
        description="Generates an executive report based on the analysis."
    )
    workflow.add_task(report_task)

    return workflow

def register_dynamic_query_components():
    """Registers all tools and handlers needed for the dynamic input query workflow."""  # noqa: D202
    
    # Register framework tools
    register_tool("get_available_capabilities", get_available_capabilities)
    
    # Register dynamic query specific tools
    register_tool("dynamic_topic_search", dynamic_topic_search_tool)
    
    # Register dynamic query specific handlers
    register_handler("analyze_search_results_handler", analyze_search_results_handler)
    register_handler("generate_executive_report_handler", generate_executive_report_handler)
    
    # Register handlers from chat_planner_workflow
    register_handler("await_input_handler", await_input_handler)
    
    logger.info("Registered dynamic query components")

def main():
    """Entry point for the dynamic input query workflow."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("--- Initializing Dynamic Input Query Workflow ---")
    
    # Reset services
    reset_services()
    services = get_services()
    
    # Set up registries
    tool_registry = ToolRegistry()
    handler_registry = HandlerRegistry()
    services.register_tool_registry(tool_registry)
    services.register_handler_registry(handler_registry)
    
    # Register components
    register_dynamic_query_components()
    ensure_all_registrations()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run Dynamic Input Query workflow")
    parser.add_argument("--save_report", action="store_true", default=True,
                        help="Save the generated report to a file")
    parser.add_argument("--visualize", action="store_true", 
                        help="Generate a visualization of the workflow")
    parser.add_argument("--output", default="workflow_visualization.png",
                        help="Output path for the workflow visualization (when --visualize is used)")
    
    args = parser.parse_args()
    
    # Build workflow
    workflow = build_dynamic_input_query_workflow()
    logger.info(f"Workflow '{workflow.name}' built")
    
    # Generate visualization if requested
    if args.visualize:
        try:
            # Check if graphviz is available
            try:
                import graphviz
                import networkx as nx
                graphviz_available = True
            except ImportError:
                graphviz_available = False
                logger.warning("Graphviz or NetworkX modules not installed. Please install with 'pip install graphviz networkx'")
                print("\nVisualization requires graphviz and networkx packages.")
                print("Please install with 'pip install graphviz networkx'")
                return
            
            if not graphviz_available:
                return
                
            visualization_path = args.output
            logger.info(f"Generating workflow visualization at: {visualization_path}")
            # Extract the filename without extension and the format from the output path
            filename, format_ext = os.path.splitext(visualization_path)
            format_ext = format_ext.lstrip('.')  # Remove the leading dot
            if not format_ext:
                format_ext = "png"  # Default format
            
            visualize_workflow(workflow, filename=filename, format=format_ext, view=False)
            print(f"\nWorkflow visualization saved to: {filename}.{format_ext}")
            
            # If visualization is the only thing requested, exit
            if len(sys.argv) == 2 and "--visualize" in sys.argv:
                return
        except Exception as e:
            logger.error(f"Error generating workflow visualization: {e}")
            print(f"\nError generating visualization: {e}")
    
    print("\n--- Dynamic Input Query Analysis ---")
    print("This tool will generate an executive report based on your query.")
    
    # Execute the workflow steps directly
    try:
        # 1. Get user input
        print("\nPlease enter a topic or question you would like to research:")
        user_query = input("> ")
        
        if not user_query.strip():
            print("Error: No query provided. Please run again with a valid query.")
            return
        
        print(f"\nResearching: {user_query}")
        print("Please wait while we gather information...")
        
        # 2. Search for information
        search_result = dynamic_topic_search_tool(ToolInvocation(
            parameters={
                "query": user_query,
                "focus_areas": ["key facts", "trends", "statistics"]
            }
        ))
        
        if not search_result.get("success", False):
            print(f"\nError during search: {search_result.get('error', 'Unknown error')}")
            return
        
        # 3. Analyze search results
        analysis_task = DirectHandlerTask(
            task_id="analyze_results",
            name="Analyze Search Results",
            handler_name="analyze_search_results_handler"
        )
        analysis_result = analyze_search_results_handler(
            analysis_task, 
            {
                "search_data": search_result.get("result", {}),
                "query": user_query
            }
        )
        
        if not analysis_result.get("success", False):
            print(f"\nError during analysis: {analysis_result.get('error', 'Unknown error')}")
            return
        
        # 4. Generate report
        report_task = DirectHandlerTask(
            task_id="generate_report",
            name="Generate Executive Report",
            handler_name="generate_executive_report_handler"
        )
        report_result = generate_executive_report_handler(
            report_task,
            {
                "analysis_data": analysis_result.get("result", {}),
                "query": user_query
            }
        )
        
        if not report_result.get("success", False):
            print(f"\nError generating report: {report_result.get('error', 'Unknown error')}")
            return
        
        # Print summary
        print("\nAnalysis complete!")
        report_summary = report_result.get("result", {}).get("summary", "No summary available")
        print(f"\n{report_summary}")
        
        # Save report if requested
        report = report_result.get("result", {}).get("report", "")
        if report and args.save_report:
            report_path = f"executive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            try:
                with open(report_path, "w") as f:
                    f.write(report)
                logger.info(f"Report saved to {report_path}")
                print(f"\nFull report saved to: {report_path}")
            except Exception as e:
                logger.error(f"Failed to save report: {e}")
        
        # Display the report in the console
        print("\n--- Executive Report Preview ---")
        print(report[:500] + "..." if len(report) > 500 else report)
        print("\n--- End of Preview ---")
                
    except Exception as e:
        logger.error(f"Error during execution: {e}")
        print(f"\nError: {e}")

if __name__ == "__main__":
    main() 