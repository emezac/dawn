"""
Final Complex Conditional Workflow Example with Fallback Logic

This workflow does the following:
1. Uploads a training document.
2. Creates a vector store from the uploaded file’s ID.
3. Extracts document insights via file search.
   - If the output is too short (≤ 100 characters), it branches to regenerate insights.
4. Performs a web search for AI ethics.
   - If web search fails or times out, it follows the failure branch and executes a fallback task to supply a default result.
5. Uses an LLM to generate a combined summary using the document insights and the web search (or fallback) result.
6. Writes the final summary to a Markdown file.
"""

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Add parent directory to path to import framework modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.registry import ToolRegistry
from core.workflow import Workflow
from core.task import Task

# Load environment variables from .env file
load_dotenv()

# Instantiate the OpenAI client for LLM tasks
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_openai(prompt):
    """Call the OpenAI API to generate a response for LLM tasks."""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

def dict_to_task(task_dict):
    """Convert a task dictionary to a Task object."""
    return Task(
        task_id=task_dict["id"],
        name=task_dict["name"],
        is_llm_task=task_dict.get("is_llm_task", False),
        tool_name=task_dict.get("tool_name"),
        input_data=task_dict.get("input_data"),
        max_retries=task_dict.get("max_retries", 0),
        next_task_id_on_success=task_dict.get("next_task_id_on_success"),
        next_task_id_on_failure=task_dict.get("next_task_id_on_failure"),
        condition=task_dict.get("condition")
    )

def main():
    print("Starting Final Complex Conditional Workflow Example with Fallback Logic")
    
    # ------------------
    # Define tasks as dictionaries with fallback for web search
    # ------------------
    
    # Task 1: Upload Training Document
    task1 = {
        "id": "upload_file_task",
        "name": "Upload Training Document",
        "is_llm_task": False,
        "tool_name": "file_upload",
        "input_data": {
            "file_path": os.path.join(os.path.dirname(__file__), "pdfs", "training.pdf"),
            "purpose": "assistants"
        },
        "next_task_id_on_success": "create_vector_store_task"
    }
    
    # Task 2: Create Vector Store
    task2 = {
        "id": "create_vector_store_task",
        "name": "Create Vector Store",
        "is_llm_task": False,
        "tool_name": "vector_store_create",
        "input_data": {
            "name": "Training Document Store",
            "file_ids": ["${upload_file_task}.output_data.response"]
        },
        "next_task_id_on_success": "file_search_task"
    }
    
    # Task 3: Extract Document Insights (File Search)
    task3 = {
        "id": "file_search_task",
        "name": "Extract Document Insights",
        "is_llm_task": False,
        "tool_name": "file_read",
        "input_data": {
            "vector_store_ids": ["${create_vector_store_task}.output_data.response"],
            "query": "Extract key insights regarding AI ethics from the training document.",
            "max_num_results": 5,
            "include_search_results": True
        },
        "next_task_id_on_success": "web_search_task",
        "next_task_id_on_failure": "regenerate_insights_task",
        "condition": "len(output_data['response']) > 100"
    }
    
    # Task 3B: Regenerate Document Insights if Task 3 output is too short (LLM task)
    task3b = {
        "id": "regenerate_insights_task",
        "name": "Regenerate Document Insights",
        "is_llm_task": True,
        "input_data": {
            "prompt": "The extracted insights are too short. Regenerate a more detailed summary of key insights on AI ethics from the training document."
        },
        "max_retries": 1,
        "next_task_id_on_success": "web_search_task"
    }
    
    # Task 4: Web Search for AI Ethics
    # If web search fails (e.g., times out), fallback to Task 4B.
    task4 = {
        "id": "web_search_task",
        "name": "Web Search for AI Ethics",
        "is_llm_task": False,
        "tool_name": "web_search",
        "input_data": {
            "query": "What are the latest advancements in AI ethics research?",
            "context_size": "medium",
            "user_location": {
                "type": "approximate",
                "country": "US",
                "city": "San Francisco",
                "region": "CA"
            }
        },
        "next_task_id_on_success": "create_summary_task",
        "next_task_id_on_failure": "default_web_search_task"
    }
    
    # Task 4B: Fallback Web Search (Default result) if Task 4 fails
    task4b = {
        "id": "default_web_search_task",
        "name": "Default Web Search Result",
        "is_llm_task": True,
        "input_data": {
            "prompt": "Return a default summary of recent advancements in AI ethics research. Include key areas like auditing, education, and governance."
        },
        "max_retries": 1,
        "next_task_id_on_success": "create_summary_task"
    }
    
    # Task 5: Generate Combined Summary via LLM
    task5 = {
        "id": "create_summary_task",
        "name": "Generate Combined Summary",
        "is_llm_task": True,
        "input_data": {
            "prompt": ("Using the document insights: '${file_search_task}.output_data.response', "
                       "and the web search results: '${web_search_task}.output_data.response', "
                       "generate a comprehensive summary on the current state of AI ethics. "
                       "Present the summary in well-structured Markdown format with appropriate headings.")
        },
        "max_retries": 1
    }
    
    # Task 6: Write Summary to Markdown
    task6 = {
        "id": "write_markdown_task",
        "name": "Write Summary to Markdown",
        "is_llm_task": False,
        "tool_name": "write_markdown",
        "input_data": {
            "file_path": os.path.join(os.path.dirname(__file__), "output", "AI_ethics_summary.md"),
            "content": "${create_summary_task}.output_data.response"
        }
    }
    
    # ------------------
    # Build the Workflow
    # ------------------
    workflow = Workflow(workflow_id="conditional_workflow", name="Conditional Workflow Example")
    
    def dict_to_task(task_dict):
        return Task(
            task_id=task_dict["id"],
            name=task_dict["name"],
            is_llm_task=task_dict.get("is_llm_task", False),
            tool_name=task_dict.get("tool_name"),
            input_data=task_dict.get("input_data"),
            max_retries=task_dict.get("max_retries", 0),
            next_task_id_on_success=task_dict.get("next_task_id_on_success"),
            next_task_id_on_failure=task_dict.get("next_task_id_on_failure"),
            condition=task_dict.get("condition")
        )
    
    # Convert dictionaries to Task objects
    task1_obj = dict_to_task(task1)
    task2_obj = dict_to_task(task2)
    task3_obj = dict_to_task(task3)
    task3b_obj = dict_to_task(task3b)
    task4_obj = dict_to_task(task4)
    task4b_obj = dict_to_task(task4b)
    task5_obj = dict_to_task(task5)
    task6_obj = dict_to_task(task6)
    
    # Add tasks to the workflow
    workflow.add_task(task1_obj)
    workflow.add_task(task2_obj)
    workflow.add_task(task3_obj)
    workflow.add_task(task3b_obj)
    workflow.add_task(task4_obj)
    workflow.add_task(task4b_obj)
    workflow.add_task(task5_obj)
    workflow.add_task(task6_obj)
    
    # ------------------
    # Execute the Workflow Sequentially with Manual Variable Substitution
    # ------------------
    registry = ToolRegistry()
    
    # Task 1: File Upload
    print("\n[Task 1] Upload Training Document")
    result1 = registry.execute_tool("file_upload", task1_obj.input_data)
    if not result1["success"]:
        print("Task 1 failed:", result1["error"])
        return
    file_id = result1["result"]
    task1_obj.set_output({"response": file_id})
    print("Task 1 output (file ID):", file_id)
    
    # Task 2: Create Vector Store
    task2_input = task2_obj.input_data.copy()
    task2_input["file_ids"] = [file_id]
    print("\n[Task 2] Create Vector Store")
    result2 = registry.execute_tool("vector_store_create", task2_input)
    if not result2["success"]:
        print("Task 2 failed:", result2["error"])
        return
    vector_store_id = result2["result"]
    task2_obj.set_output({"response": vector_store_id})
    print("Task 2 output (vector store ID):", vector_store_id)
    
    # Task 3: Extract Document Insights
    task3_input = task3_obj.input_data.copy()
    task3_input["vector_store_ids"] = [vector_store_id]
    print("\n[Task 3] Extract Document Insights")
    result3 = registry.execute_tool("file_read", task3_input)
    if not result3["success"]:
        print("Task 3 failed:", result3["error"])
        return
    file_search_output = result3["result"]
    task3_obj.set_output({"response": file_search_output})
    print("Task 3 output (file search result):", file_search_output)
    
    # Conditional Branch: Check Task 3 output length.
    if len(file_search_output) <= 100:
        print("Task 3 output is too short. Executing Task 3B (Regenerate Document Insights)...")
        regenerated_insights = call_openai(task3b_obj.input_data["prompt"])
        task3b_obj.set_output({"response": regenerated_insights})
        file_search_output = regenerated_insights
        print("Task 3B output (regenerated insights):", regenerated_insights)
    else:
        print("Task 3 output is sufficient.")
    
    # Task 4: Web Search for AI Ethics
    print("\n[Task 4] Web Search for AI Ethics")
    result4 = registry.execute_tool("web_search", task4_obj.input_data)
    if not result4["success"]:
        print("Task 4 failed. Executing fallback Task 4B (Default Web Search)...")
        # Fallback: Use default web search result from Task 4B.
        default_result = call_openai(task4b_obj.input_data["prompt"])
        task4b_obj.set_output({"response": default_result})
        web_search_output = default_result
        print("Task 4B output (default web search result):", default_result)
    else:
        web_search_output = result4["result"]
        task4_obj.set_output({"response": web_search_output})
        print("Task 4 output (web search result):", web_search_output)
    
    # Task 5: Generate Combined Summary via LLM
    prompt = (
        f"Using the document insights: '{file_search_output}', and the web search results: '{web_search_output}', "
        "generate a comprehensive summary on the current state of AI ethics. "
        "Present the summary in well-structured Markdown format with appropriate headings."
    )
    print("\n[Task 5] Generate Combined Summary")
    summary = call_openai(prompt)
    task5_obj.set_output({"response": summary})
    print("Task 5 output (summary):", summary)
    
    # Task 6: Write Summary to Markdown
    task6_input = task6_obj.input_data.copy()
    task6_input["content"] = summary
    print("\n[Task 6] Write Summary to Markdown")
    result6 = registry.execute_tool("write_markdown", task6_input)
    if not result6["success"]:
        print("Task 6 failed:", result6["error"])
        return
    final_md_file = result6["result"]
    task6_obj.set_output({"response": final_md_file})
    print("Task 6 output (Markdown file path):", final_md_file)
    
    # Read and print the final Markdown file content
    try:
        with open(final_md_file, "r", encoding="utf-8") as f:
            md_content = f.read()
        print("\nFinal Markdown File Content:\n")
        print(md_content)
    except Exception as e:
        print("Error reading final Markdown file:", str(e))
    
    print("\nFinal Complex Conditional Workflow completed!")
    print("Check the output folder for AI_ethics_summary.md.")


if __name__ == "__main__":
    main()
