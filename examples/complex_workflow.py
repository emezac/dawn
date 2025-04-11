"""
Final Complex Workflow Example (Sequential Execution with Manual Variable Substitution)

This workflow does the following:
1. Uploads a training document using the file upload tool.
2. Creates a vector store using the uploaded file's ID.
3. Extracts document insights via file search (RAG) using the vector store.
4. Performs a web search for supplementary information on AI ethics.
5. Uses an LLM to generate a combined summary.
6. Writes the summary to a Markdown file.

Each task is executed sequentially with outputs from previous tasks substituted into subsequent tasks.
"""

import os
import sys
import logging
from typing import Dict, Any

from dotenv import load_dotenv
from openai import OpenAI

# Add parent directory to path to import framework modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.workflow import Workflow
from core.tools.registry import ToolRegistry # Keep for type hint
# Import the singleton access function
from core.tools.registry_access import get_registry, register_tool

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
            {"role": "user", "content": prompt},
        ],
        max_tokens=1000,  # Increased token limit for a more complete output
    )
    return response.choices[0].message.content.strip()


def main():
    print("Starting Final Complex Workflow Example (Sequential Execution)")

    # Get the singleton registry
    registry = get_registry()

    # ------------------
    # Task 1: File Upload
    # ------------------
    upload_input = {
        "file_path": os.path.join(os.path.dirname(__file__), "pdfs", "training.pdf"),
        "purpose": "assistants",
    }
    print("\n[Task 1] Upload Training Document")
    result1 = registry.execute_tool("file_upload", upload_input)
    if not result1["success"]:
        print("Task 1 failed:", result1["error"])
        return
    file_id = result1["result"]
    print("Task 1 output (file ID):", file_id)

    # ------------------
    # Task 2: Create Vector Store
    # ------------------
    # Here we substitute the file ID from Task 1 into the file_ids array.
    task2_input = {
        "name": "Training Document Store",
        "file_ids": [file_id],  # using actual file_id from Task 1
    }
    print("\n[Task 2] Create Vector Store")
    result2 = registry.execute_tool("vector_store_create", task2_input)
    if not result2["success"]:
        print("Task 2 failed:", result2["error"])
        return
    vector_store_id = result2["result"]
    print("Task 2 output (vector store ID):", vector_store_id)

    # ------------------
    # Task 3: File Search (RAG)
    # ------------------
    task3_input = {
        "vector_store_ids": [vector_store_id],  # using actual vector store ID
        "query": "Extract key insights regarding AI ethics from the training document.",
        "max_num_results": 5,
        "include_search_results": True,
    }
    print("\n[Task 3] Extract Document Insights")
    result3 = registry.execute_tool("file_read", task3_input)
    if not result3["success"]:
        print("Task 3 failed:", result3["error"])
        return
    file_search_output = result3["result"]
    print("Task 3 output (file search result):", file_search_output)

    # ------------------
    # Task 4: Web Search for AI Ethics
    # ------------------
    task4_input = {
        "query": "What are the latest advancements in AI ethics research?",
        "context_size": "medium",
        "user_location": {
            "type": "approximate",
            "country": "US",
            "city": "San Francisco",
            "region": "CA",
        },
    }
    print("\n[Task 4] Web Search for AI Ethics")
    result4 = registry.execute_tool("web_search", task4_input)
    if not result4["success"]:
        print("Task 4 failed:", result4["error"])
        return
    web_search_output = result4["result"]
    print("Task 4 output (web search result):", web_search_output)

    # ------------------
    # Task 5: Generate Combined Summary via LLM
    # ------------------
    # Construct a prompt using the outputs from Task 3 and Task 4.
    prompt = (
        f"Using the document insights: '{file_search_output}', and the web search results: '{web_search_output}', "
        "generate a comprehensive summary on the current state of AI ethics. "
        "Present the summary in well-structured Markdown format with appropriate headings."
    )
    print("\n[Task 5] Generate Combined Summary (LLM Task)")
    summary = call_openai(prompt)
    print("Task 5 output (summary):", summary)

    # ------------------
    # Task 6: Write Summary to Markdown
    # ------------------
    task6_input = {
        "file_path": os.path.join(os.path.dirname(__file__), "output", "AI_ethics_summary.md"),
        "content": summary,  # using actual summary from Task 5
    }
    print("\n[Task 6] Write Summary to Markdown")
    result6 = registry.execute_tool("write_markdown", task6_input)
    if not result6["success"]:
        print("Task 6 failed:", result6["error"])
        return
    final_md_file = result6["result"]
    print("Task 6 output (Markdown file path):", final_md_file)

    # Read and print the final Markdown file content
    try:
        with open(final_md_file, "r", encoding="utf-8") as f:
            md_content = f.read()
        print("\nFinal Markdown File Content:\n")
        print(md_content)
    except Exception as e:
        print("Error reading final Markdown file:", str(e))

    print("\nFinal Complex Workflow completed! Check the output folder for AI_ethics_summary.md.")


if __name__ == "__main__":
    # --- Setup ---
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    # Get the singleton registry
    registry = get_registry()

    # Register custom tools
    # ... existing code ...

    main()
