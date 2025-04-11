"""
Context-Aware Legal Contract Review Workflow Example

This workflow demonstrates the context-aware agent enhancements, including:
1. Vector Store integration for document search
2. Long-Term Memory (LTM) for storing and retrieving context
3. File Search integration with the LLM interface
4. DirectHandlerTask for custom processing
5. Enhanced variable resolution for complex data structures

The workflow performs a legal contract review with the following steps:
1. Extract key topics/clauses from a draft contract
2. Search internal legal documents for relevant guidelines (using vector stores)
3. Search the web for recent legal updates
4. Synthesize findings and generate redlines
5. Save a summary to long-term memory
6. Format the final output as a markdown report

Prerequisites:
- OpenAI API key set in environment variables
- Vector stores for legal guidelines and agent LTM
"""

import os
import sys
import tempfile
import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

from dotenv import load_dotenv
from openai import OpenAI

# Add the project root directory to Python's module search path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.agent import Agent
from core.task import Task, DirectHandlerTask
from core.tools.registry import ToolRegistry
from core.workflow import Workflow
from core.tools.registry_access import (
    get_registry, register_tool, execute_tool, 
    tool_exists, get_available_tools
)

load_dotenv()

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

SAMPLE_CONTRACT = """
CONSULTING AGREEMENT

This Consulting Agreement (the "Agreement") is made and entered into as of [DATE], by and between XYZ Corp., a Delaware corporation ("Company"), and ABC Consulting LLC, a California limited liability company ("Consultant").

1. SERVICES. Consultant will provide consulting services to the Company as described in Exhibit A (the "Services").

2. COMPENSATION. Company shall pay Consultant $150 per hour for Services performed. Consultant shall invoice Company monthly, and payment shall be due within 30 days of receipt of invoice.

3. TERM AND TERMINATION. This Agreement shall commence on [START DATE] and continue for a period of one year. Either party may terminate this Agreement with 30 days written notice.

4. INTELLECTUAL PROPERTY. All work product developed by Consultant in performing the Services shall be the sole and exclusive property of the Company. Consultant hereby assigns all right, title, and interest in such work product to the Company.

5. CONFIDENTIALITY. Consultant agrees to maintain the confidentiality of all proprietary information disclosed by the Company for a period of 5 years.

6. INDEMNIFICATION. Consultant agrees to indemnify and hold harmless the Company from any claims arising from Consultant's negligence or willful misconduct.

7. GOVERNING LAW. This Agreement shall be governed by the laws of the State of California.

8. ARBITRATION. Any disputes arising under this Agreement shall be resolved through binding arbitration in San Francisco, California.

9. ENTIRE AGREEMENT. This Agreement constitutes the entire understanding between the parties and supersedes all prior agreements.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.
"""


def custom_save_to_ltm(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Custom implementation of save_to_ltm tool.
    
    Args:
        input_data: Dictionary containing vector_store_id and text_content
        
    Returns:
        Dictionary with the result of the operation
    """
    vector_store_id = input_data.get("vector_store_id", "")
    text_content = input_data.get("text_content", "")
    
    if not vector_store_id or not text_content:
        return {
            "success": False,
            "result": "Failed: Missing parameters",
            "error": "Missing required parameters",
            "error_type": "MissingParameter"
        }
    
    # Since we can't directly use the OpenAI vector store API in this example,
    # we'll simulate saving to LTM by writing to a local file instead
    try:
        # Create a directory to simulate LTM storage
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ltm_dir = os.path.join(script_dir, "output", "ltm_storage")
        print(f"Creating LTM directory: {ltm_dir}")
        os.makedirs(ltm_dir, exist_ok=True)
        
        # Create a filename based on timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ltm_entry_{timestamp}.txt"
        file_path = os.path.join(ltm_dir, filename)
        
        print(f"Writing to file: {file_path}")
        
        # Write content to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"Vector Store ID: {vector_store_id}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Content Length: {len(text_content)}\n")
            f.write("\n--- CONTENT ---\n")
            f.write(text_content)
        
        # Verify the file was created
        if os.path.exists(file_path):
            print(f"Simulated LTM save successful: {file_path}")
            return {
                "success": True,
                "result": file_path
            }
        else:
            print(f"File was not created at {file_path}")
            return {
                "success": False,
                "result": "Failed: File not created",
                "error": "File write operation completed but file not found",
                "error_type": "FileNotFound"
            }
    except Exception as e:
        error_message = f"Error simulating LTM save: {e}"
        print(error_message)
        return {
            "success": False,
            "result": "Failed: Exception during save",
            "error": error_message,
            "error_type": type(e).__name__
        }


def save_to_ltm_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler function for saving text to Long-Term Memory vector store.
    
    Args:
        input_data: Dictionary containing vector_store_id and text_content
        
    Returns:
        Dictionary with the result of the operation
    """
    # Add debugging to see what's in the input data
    print("\nDEBUG save_to_ltm_handler input:")
    print(f"  Vector Store ID: {input_data.get('vector_store_id', 'Not provided')}")
    text_content = input_data.get("text_content", "")
    content_preview = text_content[:100] + "..." if len(text_content) > 100 else text_content
    print(f"  Text Content (preview): {content_preview}")
    print(f"  Text Content Length: {len(text_content)}")
    
    vector_store_id = input_data.get("vector_store_id", "")
    
    if not vector_store_id or not text_content:
        print("ERROR: Missing required parameters in save_to_ltm_handler")
        return {
            "success": False,
            "result": "Failed due to missing parameters",
            "error": "Missing required parameters vector_store_id or text_content",
            "error_type": "MissingParameter"
        }
    
    try:
        # First try to use our direct custom implementation
        print("Using direct custom_save_to_ltm implementation")
        try:
            result = custom_save_to_ltm(input_data)
            print(f"Direct custom_save_to_ltm result: {result.get('success', False)}")
            
            # If successful, return the result
            if result.get("success", False):
                return result
                
            # Otherwise, try the registry as fallback
            print("Direct implementation failed, trying registry as fallback")
        except Exception as e:
            print(f"ERROR in direct custom_save_to_ltm: {str(e)}")
            # Continue to try the registry
        
        # Try to use the registry's save_to_ltm if available
        if tool_exists("save_to_ltm"):
            # Use the registered tool
            print("Using registered save_to_ltm tool")
            result = execute_tool("save_to_ltm", {
                "vector_store_id": vector_store_id,
                "text_content": text_content
            })
        else:
            # Fallback to another custom implementation attempt
            print("Registered tool not found, making second attempt with custom save_to_ltm implementation")
            # We already tried custom_save_to_ltm above, but we'll try a simpler approach here
            try:
                # Create a simplified file save as last resort
                script_dir = os.path.dirname(os.path.abspath(__file__))
                output_dir = os.path.join(script_dir, "output")
                os.makedirs(output_dir, exist_ok=True)
                
                # Save to a file with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                fallback_file = os.path.join(output_dir, f"ltm_fallback_{timestamp}.txt")
                
                with open(fallback_file, "w", encoding="utf-8") as f:
                    f.write(f"FALLBACK SAVE\nVector Store ID: {vector_store_id}\n\n{text_content}")
                
                result = {
                    "success": True,
                    "result": fallback_file,
                    "note": "Used fallback file save mechanism"
                }
            except Exception as fallback_error:
                print(f"ERROR in fallback save: {str(fallback_error)}")
                result = {
                    "success": False,
                    "result": "All save attempts failed",
                    "error": f"Multiple save failures: {str(fallback_error)}",
                    "error_type": "CascadingFailure"
                }
        
        # Ensure proper structure in the returned result
        if not isinstance(result, dict):
            result = {"success": False, "error": "Tool did not return a dictionary"}
        
        # Add a result field if not present but success is True
        if result.get("success", False) and "result" not in result:
            result["result"] = "Successfully saved to LTM"
            
        # Add additional metadata
        if "metadata" not in result:
            result["metadata"] = {}
        
        result["metadata"].update({
            "timestamp": datetime.now().isoformat(),
            "operation": "save_to_ltm",
            "handler": "save_to_ltm_handler"
        })
        
        print(f"LTM Save final result: {result.get('success', False)}")
        return result
    except Exception as e:
        print(f"ERROR in save_to_ltm_handler: {str(e)}")
        # Return a structured error response that won't break the workflow
        return {
            "success": False,
            "result": f"Error occurred but workflow will continue: {str(e)}",
            "error": f"Exception while saving to LTM: {str(e)}",
            "error_type": type(e).__name__,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "operation": "save_to_ltm_failed",
                "error": str(e)
            }
        }


def write_markdown_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler function for writing content to a Markdown file.
    
    Args:
        input_data: Dictionary containing file_path and content
        
    Returns:
        Dictionary with the result of the operation
    """
    # Add debugging to see what's in the input data
    print("\nDEBUG write_markdown_handler input:")
    file_path = input_data.get("file_path", "")
    print(f"  File Path: {file_path}")
    content = input_data.get("content", "")
    content_preview = content[:100] + "..." if len(content) > 100 else content
    print(f"  Content (preview): {content_preview}")
    print(f"  Content Length: {len(content)}")
    
    # Try to get analysis result if available
    analysis_data = input_data.get("analysis_result", None)
    if analysis_data and isinstance(analysis_data, dict) and "report_markdown" in analysis_data:
        print("Using structured analysis report markdown")
        content = analysis_data.get("report_markdown", content)
    
    if not file_path:
        print("ERROR: Missing file_path parameter in write_markdown_handler")
        file_path = "legal_report_default.md"  # Set a default path
    
    if not content:
        print("ERROR: Missing content parameter in write_markdown_handler")
        content = "# Legal Report\n\nNo content was provided for this report."
    
    # Make file_path absolute if it's not already
    if not os.path.isabs(file_path):
        # Create an output directory within the current script directory
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        file_path = os.path.join(output_dir, file_path)
    
    # Ensure directory exists
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"Successfully wrote content to {file_path}")
        return {
            "success": True,
            "result": file_path,
            "metadata": {
                "file_size": len(content),
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        print(f"ERROR in write_markdown_handler: {str(e)}")
        return {
            "success": False,
            "result": None,
            "error": f"Failed to write file: {str(e)}",
            "error_type": type(e).__name__
        }


def search_web_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler function for web search operations.
    
    Args:
        input_data: Dictionary containing search query and parameters
        
    Returns:
        Dictionary with the search results
    """
    query = input_data.get("query", "")
    context_size = input_data.get("context_size", "medium")
    
    if not query:
        return {
            "success": False,
            "error": "Missing query parameter",
            "error_type": "MissingParameter"
        }
    
    # Use the standardized registry access to execute the web_search tool
    result = execute_tool("web_search", {
        "query": query,
        "context_size": context_size
    })
    
    # Add some processing of the results if needed
    if result.get("success") and "result" in result:
        # In a real implementation, you might process/format the results here
        result["metadata"] = {
            "query": query,
            "timestamp": datetime.now().isoformat()
        }
    
    return result


def structure_legal_analysis(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process and structure the legal analysis results into a consistent format.
    
    Args:
        input_data: Dictionary containing all analysis results
        
    Returns:
        Dictionary with structured analysis
    """
    # Add debugging to see what data is received
    print(f"DEBUG - structure_legal_analysis received: {json.dumps(input_data, default=str)[:200]}...")
    
    contract = input_data.get("contract", "")
    redlines = input_data.get("redlines", "")
    topics = input_data.get("topics", "")
    guidelines = input_data.get("guidelines", "")
    web_updates = input_data.get("web_updates", "")
    
    # Validate and ensure we have strings for all inputs
    redlines = str(redlines) if redlines else "No redline suggestions available."
    topics = str(topics) if topics else "No topics identified."
    guidelines = str(guidelines) if guidelines else "No guidelines retrieved."
    web_updates = str(web_updates) if web_updates else "No web updates retrieved."
    
    # Structure the analysis into a comprehensive format
    analysis = {
        "contract_summary": {
            "length": len(contract),
            "topics_identified": topics
        },
        "redline_suggestions": redlines,
        "reference_material": {
            "internal_guidelines": guidelines,
            "web_legal_updates": web_updates
        },
        "analysis_timestamp": datetime.now().isoformat()
    }
    
    # Generate markdown report
    report_md = f"""# Legal Contract Review Report

## Contract Summary
{contract[:300]}...

## Key Topics Identified
{topics}

## Redline Suggestions
{redlines}

## Reference Material Used
- Internal Legal Guidelines
- Web Legal Updates

## Review Timestamp
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return {
        "success": True,
        "result": {
            "analysis": analysis,
            "report_markdown": report_md
        }
    }


def create_vector_stores_if_needed():
    """
    Create vector stores for legal guidelines and agent LTM if they don't exist.
    Returns a tuple of (legal_guidelines_vs_id, agent_ltm_vs_id).
    """
    list_result = execute_tool("list_vector_stores", {})
    if not list_result["success"]:
        print("Failed to list vector stores:", list_result["error"])
        return None, None

    existing_stores = list_result["result"]
    legal_vs_id = None
    ltm_vs_id = None

    for store in existing_stores:
        if store["name"] == "Internal Legal Guidelines":
            legal_vs_id = store["id"]
            print(f"Found existing legal guidelines vector store: {legal_vs_id}")
        elif store["name"] == "Agent LTM":
            ltm_vs_id = store["id"]
            print(f"Found existing agent LTM vector store: {ltm_vs_id}")

    if not legal_vs_id:
        create_result = execute_tool("create_vector_store", {"name": "Internal Legal Guidelines"})
        if not create_result["success"]:
            print("Failed to create legal guidelines vector store:", create_result["error"])
            return None, None
        legal_vs_id = create_result["result"]
        print(f"Created new legal guidelines vector store: {legal_vs_id}")

        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt") as temp_file:
            temp_file.write(
                """
            INTERNAL LEGAL GUIDELINES
            
            1. COMPENSATION GUIDELINES
            - Standard consultant rates should be capped at $125 per hour
            - Payment terms should be net-45 days, not net-30
            - All consultants must provide detailed time tracking
            
            2. INTELLECTUAL PROPERTY GUIDELINES
            - All IP clauses must include "work made for hire" language
            - Company must retain rights to all derivatives and improvements
            - IP assignments must be irrevocable and perpetual
            
            3. CONFIDENTIALITY GUIDELINES
            - Standard confidentiality period is 3 years, not 5 years
            - All confidentiality clauses must include exclusions for publicly available information
            - Consultants must return or destroy all confidential information upon termination
            
            4. TERMINATION GUIDELINES
            - Termination notice period should be 15 days, not 30 days
            - Company should have right to terminate immediately for cause
            - All agreements should include transition assistance provisions
            
            5. DISPUTE RESOLUTION GUIDELINES
            - Arbitration should be conducted by JAMS, not general "binding arbitration"
            - Venue should be Delaware, not California
            - Governing law should be Delaware law, not California law
            """
            )
            legal_doc_path = temp_file.name

        upload_result = execute_tool(
            "upload_file_to_vector_store",
            {"vector_store_id": legal_vs_id, "file_path": legal_doc_path, "purpose": "assistants"},
        )
        if not upload_result["success"]:
            print("Failed to upload legal guidelines:", upload_result["error"])
        else:
            print("Uploaded legal guidelines to vector store")

        os.remove(legal_doc_path)

    if not ltm_vs_id:
        create_result = execute_tool("create_vector_store", {"name": "Agent LTM"})
        if not create_result["success"]:
            print("Failed to create agent LTM vector store:", create_result["error"])
            return legal_vs_id, None
        ltm_vs_id = create_result["result"]
        print(f"Created new agent LTM vector store: {ltm_vs_id}")

        # Test the save_to_ltm directly using our custom implementation
        print("\nTesting custom save_to_ltm directly...")
        test_input = {
            "vector_store_id": ltm_vs_id,
            "text_content": "This is a test of the custom save_to_ltm implementation."
        }
        test_save_result = custom_save_to_ltm(test_input)
        
        if not test_save_result["success"]:
            print("Direct test of custom save_to_ltm failed:", test_save_result.get("error", "Unknown error"))
            print("Will continue with workflow, but saving to LTM may fail.")
        else:
            print("Direct test of custom save_to_ltm succeeded:", test_save_result.get("result", ""))

        # Now test through the handler
        print("\nTesting save_to_ltm_handler...")
        handler_result = save_to_ltm_handler({
            "vector_store_id": ltm_vs_id,
            "text_content": "Previous contract reviews have shown that clients often negotiate for longer termination periods and higher hourly rates."
        })
        
        if not handler_result.get("success", False):
            print("Handler test failed:", handler_result.get("error", "Unknown error"))
        else:
            print("Handler test succeeded:", handler_result.get("result", ""))

    return legal_vs_id, ltm_vs_id


def build_legal_review_workflow(legal_vs_id, ltm_vs_id, draft_contract):
    """
    Build the legal contract review workflow.
    
    Args:
        legal_vs_id: Vector Store ID for legal guidelines
        ltm_vs_id: Vector Store ID for agent long-term memory
        draft_contract: The contract text to analyze
        
    Returns:
        Configured Workflow object
    """
    print("Building legal review workflow...")
    
    # Create workflow
    workflow = Workflow(
        workflow_id="legal_review_workflow",
        name="Context-Aware Legal Contract Review"
    )
    
    # Task 1: Extract key topics from contract
    task1 = Task(
        task_id="extract_topics",
        name="Extract Key Contract Topics",
        is_llm_task=True,
        input_data={
            "prompt": f"""
            Analyze the following contract draft and extract the key legal topics, clauses, and their specific terms.
            
            CONTRACT:
            ```
            {draft_contract}
            ```
            
            For each topic or clause, provide:
            1. The clause title/type
            2. A brief summary of its terms
            3. Any unusual or potentially problematic language

            Format your response as a single JSON object with the following structure:
            {{
                "topics": [
                    {{
                        "title": "clause_title",
                        "summary": "brief_summary",
                        "concerns": "any_concerns"
                    }}
                ]
            }}
            
            Only respond with the JSON object, no other text.
            """
        },
        next_task_id_on_success="parse_topics_json"
    )
    workflow.add_task(task1)
    
    # NEW Task: Parse the extracted topics JSON
    def parse_json_output(input_data):
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
                
                # If we still can't parse it, return a default structure with the error
                return {
                    "success": False,
                    "result": {
                        "topics": [
                            {
                                "title": "Parsing Error",
                                "summary": "Failed to parse LLM output as JSON",
                                "concerns": "Review the contract manually"
                            }
                        ]
                    },
                    "error": f"Failed to parse JSON: {str(e)}"
                }
        
        # If the input was neither a string nor a dict with 'response'
        return {
            "success": False,
            "result": {
                "topics": []
            },
            "error": "Input was not in expected format"
        }
        
    task1b = DirectHandlerTask(
        task_id="parse_topics_json",
        name="Parse Topics JSON Output",
        handler=parse_json_output,
        input_data={
            "llm_output": "${extract_topics.output_data}"
        },
        next_task_id_on_success="search_guidelines"
    )
    workflow.add_task(task1b)
    
    # Task 2: Search for relevant legal guidelines
    task2 = Task(
        task_id="search_guidelines",
        name="Search Legal Guidelines",
        tool_name="file_read",
        input_data={
            "vector_store_ids": [legal_vs_id],
            "query": "Legal guidelines regarding: ${parse_topics_json.output_data.result.topics[0].title}, ${parse_topics_json.output_data.result.topics[1].title | 'compliance'}",
            "max_num_results": 3,
            "include_search_results": True
        },
        next_task_id_on_success="search_web"
    )
    workflow.add_task(task2)
    
    # Task 3: Search the web for recent legal updates
    task3 = Task(
        task_id="search_web",
        name="Search Web for Legal Updates",
        tool_name="web_search",
        input_data={
            "query": "Recent legal updates on ${parse_topics_json.output_data.result.topics[0].title} contracts"
        },
        next_task_id_on_success="generate_redlines"
    )
    workflow.add_task(task3)
    
    # Task 4: Generate redlines based on guidelines and updates
    task4 = Task(
        task_id="generate_redlines",
        name="Generate Contract Redlines",
        is_llm_task=True,
        input_data={
            "prompt": f"""
            You are a legal expert reviewing the following contract. Based on the extracted topics, legal guidelines, and recent updates, generate redline suggestions.
            
            CONTRACT:
            ```
            {draft_contract}
            ```
            
            EXTRACTED TOPICS:
            ${{parse_topics_json.output_data.result.topics | 'No topics extracted'}}
            
            LEGAL GUIDELINES:
            ${{search_guidelines.output_data.result | 'No guidelines found'}}
            
            RECENT UPDATES:
            ${{search_web.output_data.result | 'No recent updates found'}}
            
            Provide your redline suggestions in the following JSON format:
            {{
                "redlines": [
                    {{
                        "clause": "section_name",
                        "current_text": "current_problematic_text",
                        "suggested_text": "suggested_replacement_text",
                        "explanation": "reason_for_change"
                    }}
                ],
                "summary": "overall_summary_of_changes"
            }}
            
            Only respond with the JSON object, no other text.
            """
        },
        next_task_id_on_success="parse_redlines_json"
    )
    workflow.add_task(task4)
    
    # NEW Task: Parse redlines JSON
    task4b = DirectHandlerTask(
        task_id="parse_redlines_json",
        name="Parse Redlines JSON",
        handler=parse_json_output,
        input_data={
            "llm_output": "${generate_redlines.output_data}"
        },
        next_task_id_on_success="save_to_ltm"
    )
    workflow.add_task(task4b)
    
    # Task 5: Save review summary to LTM
    task5 = DirectHandlerTask(
        task_id="save_to_ltm",
        name="Save Review to LTM",
        handler=save_to_ltm_handler,
        input_data={
            "vector_store_id": ltm_vs_id,
            "text_content": """
            LEGAL REVIEW SUMMARY
            
            Date: Current Date
            
            Contract Topics:
            ${parse_topics_json.output_data.result.topics[0].title | 'Topic 1'} - ${parse_topics_json.output_data.result.topics[0].summary | 'No summary available'}
            ${parse_topics_json.output_data.result.topics[1].title | 'Topic 2'} - ${parse_topics_json.output_data.result.topics[1].summary | 'No summary available'}
            
            Redline Summary:
            ${parse_redlines_json.output_data.result.summary | 'No redlines generated'}
            """
        },
        next_task_id_on_success="format_report",
        next_task_id_on_failure="format_report"  # Continue even if LTM save fails
    )
    workflow.add_task(task5)
    
    # Task 6: Format final report
    task6 = DirectHandlerTask(
        task_id="format_report",
        name="Format Final Report",
        handler=write_markdown_handler,
        input_data={
            "file_path": "legal_review_report.md",
            "content": """
            # Legal Contract Review Report

            ## Contract Topics
            ${parse_topics_json.output_data.result.topics | []}
            
            ## Legal Guidelines Referenced
            ${search_guidelines.output_data.result | 'No guidelines found'}
            
            ## Recent Legal Updates
            ${search_web.output_data.result | 'No updates found'}
            
            ## Redline Suggestions
            ${parse_redlines_json.output_data.result.redlines | []}
            
            ## Summary
            ${parse_redlines_json.output_data.result.summary | 'No summary available'}
            
            ## Status
            - Review saved to Long-Term Memory: ${save_to_ltm.output_data.success | False}
            - Report generated on: Current Date and Time
            """
        }
    )
    workflow.add_task(task6)
    
    print("Workflow built with tasks:")
    for task_id, task in workflow.tasks.items():
        task_type = "DirectHandlerTask" if hasattr(task, "is_direct_handler") else "Task"
        print(f"  - {task_id} ({task_type})")
    
    return workflow


def main():
    """
    Run the legal contract review workflow.
    
    This function:
    1. Creates necessary vector stores if they don't exist
    2. Builds and runs the legal review workflow
    3. Handles edge cases and errors gracefully
    """
    print("Starting Context-Aware Legal Contract Review Workflow Example")
    
    # Create necessary output directories
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "output")
    ltm_dir = os.path.join(output_dir, "ltm_storage")
    
    print(f"Creating output directories:")
    print(f"  Main output dir: {output_dir}")
    print(f"  LTM storage dir: {ltm_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(ltm_dir, exist_ok=True)
    
    # Check if directories were created
    if not os.path.exists(output_dir) or not os.path.exists(ltm_dir):
        print("ERROR: Failed to create output directories")
        # Continue anyway, as the handlers will attempt to create dirs as needed
    else:
        print("Output directories created successfully")
    
    # Check for required API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable is required.")
        sys.exit(1)
    
    # Step 1: Create vector stores if needed
    vs_ids = create_vector_stores_if_needed()
    if not vs_ids or not all(vs_ids):
        print("ERROR: Failed to create/confirm vector stores. Exiting.")
        sys.exit(1)
    
    legal_vs_id, ltm_vs_id = vs_ids
    print(f"Using vector stores: Legal={legal_vs_id}, LTM={ltm_vs_id}")
    
    try:
        # Step 2: Build the workflow
        print("Building legal review workflow...")
        workflow = build_legal_review_workflow(legal_vs_id, ltm_vs_id, SAMPLE_CONTRACT)
        
        # Add validation check for DirectHandlerTask usage
        for task_id, task in workflow.tasks.items():
            if hasattr(task, 'is_direct_handler') and task.is_direct_handler:
                # Verify no 'dependencies' attribute is mistakenly set
                if hasattr(task, 'dependencies'):
                    print(f"WARNING: Task {task_id} is a DirectHandlerTask but has a 'dependencies' attribute. This is unsupported and will be removed.")
                    # Remove the dependencies attribute to prevent errors
                    delattr(task, 'dependencies')
    
        # Step 3: Create an agent and assign the workflow
        registry = get_registry() # Get the singleton registry
        agent = Agent(
            agent_id="context_aware_legal_reviewer", 
            name="Context-Aware Legal Review Agent",
            tool_registry=registry # Pass the registry
        )
        agent.load_workflow(workflow)
        
        # Register our custom save_to_ltm handler if needed
        if not tool_exists("save_to_ltm"):
            # Define a dummy function for save_to_ltm that calls our handler
            def dummy_save_to_ltm(input_data):
                print("Using custom save_to_ltm implementation from registered tool")
                try:
                    # Call our custom implementation directly to avoid any registry confusion
                    result = custom_save_to_ltm(input_data)
                    print(f"Custom save_to_ltm result: {result.get('success', False)}")
                    return result
                except Exception as e:
                    print(f"ERROR in save_to_ltm registered tool: {str(e)}")
                    # Return graceful error
                    return {
                        "success": False,
                        "result": f"Error in save_to_ltm: {str(e)}",
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
            
            print("Registering custom save_to_ltm tool")
            success = register_tool("save_to_ltm", dummy_save_to_ltm)
            
            # Verify registration was successful
            if success and tool_exists("save_to_ltm"):
                print("Successfully registered save_to_ltm tool")
            else:
                print("WARNING: Failed to register save_to_ltm tool!")
        else:
            print("save_to_ltm tool already registered")
        
        # Step 4: Run the workflow
        print("\nRunning legal review workflow...")
        result = agent.run()
        
        # Step 5: Handle the workflow completion
        any_failures = False
        critical_failures = False
        
        # Check for specific task failures
        for task_id, task in workflow.tasks.items():
            if task.status == "failed":
                any_failures = True
                
                # Check if this is a critical failure or one we can ignore
                if task_id in ["save_to_ltm", "format_report"]:
                    print(f"Non-critical task failure in {task_id}. Workflow can still be considered successful.")
                else:
                    critical_failures = True
                    print(f"Critical task failure in {task_id}: {getattr(task, 'error', 'Unknown error')}")
        
        # Check if the report was successfully generated
        report_path = None
        if "format_report" in workflow.tasks:
            format_task = workflow.tasks["format_report"]
            if format_task.status == "completed" and isinstance(format_task.output_data, dict):
                report_path = format_task.output_data.get("result")
        
        # Print summary
        print("\nWorkflow execution summary:")
        for task_id, task in workflow.tasks.items():
            status = task.status
            print(f"  - {task.name} ({task_id}): {status}")
        
        # Show the report if available
        if report_path and os.path.exists(report_path):
            print(f"\nReport generated at: {report_path}")
            try:
                with open(report_path, "r") as f:
                    report_content = f.read()
                    print("\nReport Preview:")
                    print("=" * 50)
                    # Print first 500 characters of the report
                    print(report_content[:500] + "..." if len(report_content) > 500 else report_content)
                    print("=" * 50)
            except Exception as e:
                print(f"Error reading report: {str(e)}")
        
        # Define success condition - critical tasks succeeded
        workflow_succeeded = not critical_failures
        
        if workflow_succeeded:
            print("\nWorkflow completed successfully.")
            if any_failures:
                print("Note: Some non-critical tasks failed but the workflow was still successful.")
            return True
        else:
            print("\nWorkflow failed due to critical task failures.")
            return False
            
    except Exception as e:
        print(f"Error executing workflow: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    main()
