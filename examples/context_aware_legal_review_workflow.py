"""
Context-Aware Legal Contract Review Workflow Example

This workflow demonstrates the context-aware agent enhancements, including:
1. Vector Store integration for document search
2. Long-Term Memory (LTM) for storing and retrieving context
3. File Search integration with the LLM interface

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
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

# Add the project root directory to Python's module search path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.agent import Agent
from core.task import Task
from core.tools.registry import ToolRegistry
from core.workflow import Workflow

load_dotenv()

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


def create_vector_stores_if_needed():
    """
    Create vector stores for legal guidelines and agent LTM if they don't exist.
    Returns a tuple of (legal_guidelines_vs_id, agent_ltm_vs_id).
    """
    registry = ToolRegistry()

    list_result = registry.execute_tool("list_vector_stores", {})
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
        create_result = registry.execute_tool("create_vector_store", {"name": "Internal Legal Guidelines"})
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

        upload_result = registry.execute_tool(
            "upload_file_to_vector_store",
            {"vector_store_id": legal_vs_id, "file_path": legal_doc_path, "purpose": "assistants"},
        )
        if not upload_result["success"]:
            print("Failed to upload legal guidelines:", upload_result["error"])
        else:
            print("Uploaded legal guidelines to vector store")

        os.remove(legal_doc_path)

    if not ltm_vs_id:
        create_result = registry.execute_tool("create_vector_store", {"name": "Agent LTM"})
        if not create_result["success"]:
            print("Failed to create agent LTM vector store:", create_result["error"])
            return legal_vs_id, None
        ltm_vs_id = create_result["result"]
        print(f"Created new agent LTM vector store: {ltm_vs_id}")

        # Test the save_to_ltm tool directly
        print("\nTesting save_to_ltm tool directly...")
        test_save_result = registry.execute_tool(
            "save_to_ltm", {"vector_store_id": ltm_vs_id, "text_content": "This is a test of the save_to_ltm tool."}
        )
        if not test_save_result["success"]:
            print("Direct test of save_to_ltm failed:", test_save_result["error"])
            print("Will continue with workflow, but saving to LTM may fail.")
        else:
            print("Direct test of save_to_ltm succeeded:", test_save_result["result"])

        # Now proceed with the actual save
        save_result = registry.execute_tool(
            "save_to_ltm",
            {
                "vector_store_id": ltm_vs_id,
                "text_content": "Previous contract reviews have shown that clients often negotiate for longer termination periods and higher hourly rates.",
            },
        )
        if not save_result["success"]:
            print("Failed to save initial memory to LTM:", save_result["error"])
        else:
            print("Saved initial memory to LTM")

    return legal_vs_id, ltm_vs_id


def build_legal_review_workflow(legal_vs_id, ltm_vs_id, draft_contract):
    """
    Build the legal contract review workflow.

    Args:
        legal_vs_id: Vector store ID for legal guidelines
        ltm_vs_id: Vector store ID for agent LTM
        draft_contract: The draft contract text to review

    Returns:
        A Workflow object with all tasks configured
    """
    workflow = Workflow(workflow_id="legal_review_workflow", name="Legal Contract Review Workflow")

    task1 = Task(
        task_id="task_1_extract_topics",
        name="Extract Contract Topics",
        is_llm_task=True,
        input_data={
            "prompt": f"Identify the main legal topics or clause types present in this contract draft:\n\n{draft_contract}\n\nList them concisely."
        },
        next_task_id_on_success="task_2_search_internal_docs",
    )
    workflow.add_task(task1)

    task2 = Task(
        task_id="task_2_search_internal_docs",
        name="Search Internal Legal Guidelines",
        is_llm_task=True,
        input_data={
            "prompt": "Based *only* on the provided internal legal documents, retrieve relevant guidelines, standard clauses, and potential compliance issues related to the following topics found in a draft contract: ${task_1_extract_topics.output_data}. Also check guidelines relevant to the overall contract structure if applicable."
        },
        next_task_id_on_success="task_4_synthesize_and_redline",
        use_file_search=True,
        file_search_vector_store_ids=[legal_vs_id],
        parallel=True,
    )
    # Print debugging information about the legal guidelines vector store ID
    print(f"\nDebug - Legal Guidelines Vector Store ID: '{legal_vs_id}', Type: {type(legal_vs_id)}")
    workflow.add_task(task2)

    task3 = Task(
        task_id="task_3_search_web_updates",
        name="Search Web for Recent Legal Updates",
        tool_name="web_search",
        input_data={
            "query": "Recent legal updates or notable court rulings in California concerning contract clauses related to: ${task_1_extract_topics.output_data}",
            "context_size": "medium",
        },
        next_task_id_on_success="task_4_synthesize_and_redline",
        parallel=True,
    )
    workflow.add_task(task3)

    task4 = Task(
        task_id="task_4_synthesize_and_redline",
        name="Synthesize Findings and Generate Redlines",
        is_llm_task=True,
        input_data={
            "prompt": f"""Review the following draft contract:
            --- DRAFT CONTRACT ---
            {draft_contract}
            --- END DRAFT CONTRACT ---
            
            Consider the following context:
            1. Internal Legal Guidelines Summary: ${{task_2_search_internal_docs.output_data}}
            2. Recent Web Updates Summary: ${{task_3_search_web_updates.output_data}}
            3. (Implicit Context) Relevant past interactions or preferences from long-term memory.
            
            Note: If any of the above information is missing, please continue with the available information.
            
            Your task is to act as an in-house legal reviewer. Identify specific clauses in the draft contract that deviate from our internal guidelines or are potentially impacted by recent web updates.
            Generate specific, actionable redline suggestions for these clauses. For each suggestion, briefly cite the reason (e.g., "Internal Guideline Section 3.2", "Recent Update on [Topic]").
            If a clause is compliant or standard, note that.
            If the overall contract seems compliant based on the provided context, state "Overall compliant".
            Focus ONLY on the information retrieved from internal docs and web search. Do not add general legal advice.
            """
        },
        next_task_id_on_success="task_5_save_to_ltm",
        use_file_search=True,
        file_search_vector_store_ids=[ltm_vs_id],
        parallel=False,
    )
    workflow.add_task(task4)

    task5 = Task(
        task_id="task_5_save_to_ltm",
        name="Save Review Summary to LTM",
        tool_name="save_to_ltm",
        input_data={
            "vector_store_id": ltm_vs_id if ltm_vs_id else "vs_default",
            "text_content": f"Contract review performed on {datetime.now().strftime('%Y-%m-%d')} for draft: '{draft_contract[:100]}...'. Key findings/Redlines: ${{task_4_synthesize_and_redline.output_data[:500]}}...",
        },
        next_task_id_on_success="task_6_format_output",
        next_task_id_on_failure="task_6_format_output",
        max_retries=1,
    )
    # Print debugging information about the vector store ID
    print(f"\nDebug - LTM Vector Store ID: '{ltm_vs_id}', Type: {type(ltm_vs_id)}")
    workflow.add_task(task5)

    task6 = Task(
        task_id="task_6_format_output",
        name="Format Final Review Report",
        tool_name="write_markdown",
        input_data={
            "file_path": os.path.join(os.path.dirname(__file__), "output", "contract_review_report.md"),
            "content": f"""# Contract Review Report

```
{draft_contract[:500]}...
```

${{task_4_synthesize_and_redline.output_data}}

*Internal Guidelines Citations included in redlines*
*LTM Context Used: Yes*

{datetime.now().strftime('%Y-%m-%d')}
""",
        },
        parallel=False,
    )
    workflow.add_task(task6)

    return workflow


def main():
    """Main function to run the context-aware legal review workflow."""
    print("Starting Context-Aware Legal Contract Review Workflow Example")

    if not os.environ.get("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY environment variable is not set.")
        print("This example requires an OpenAI API key to run.")
        print("Please set the OPENAI_API_KEY environment variable and try again.")
        print("Example: export OPENAI_API_KEY=your_api_key_here")
        print("\nExiting without running the workflow.")
        return

    legal_vs_id, ltm_vs_id = create_vector_stores_if_needed()
    if not legal_vs_id or not ltm_vs_id:
        print("Failed to set up required vector stores. Exiting.")
        return

    workflow = build_legal_review_workflow(legal_vs_id, ltm_vs_id, SAMPLE_CONTRACT)

    agent = Agent(agent_id="legal_review_agent", name="Legal Contract Review Agent")
    agent.load_workflow(workflow)

    print("\nExecuting legal contract review workflow...")
    result = agent.run()

    # Show a summary of task statuses
    print("\nWorkflow Task Summary:")
    completed_tasks = 0
    failed_tasks = 0

    for task_id in workflow.tasks:
        task = workflow.get_task(task_id)
        if task:
            status = task.status
            print(f"  - {task.name} (ID: {task.id}): {status}")
            if status == "completed":
                completed_tasks += 1
            elif status == "failed":
                failed_tasks += 1
        else:
            print(f"  - Task ID {task_id}: Not found in workflow")

    print(f"\nCompleted Tasks: {completed_tasks}, Failed Tasks: {failed_tasks}")

    if completed_tasks > 0:
        print("\nOutput from completed tasks:")
        for task_id in workflow.tasks:
            task = workflow.get_task(task_id)
            if task and task.status == "completed" and task.output_data:
                output = task.output_data.get("response", "No output")
                if len(output) > 200:
                    output = output[:200] + "..."
                print(f"  - {task.name}: {output}")

    # Check for specific output task
    output_task = workflow.get_task("task_6_format_output")
    if output_task and output_task.output_data and "response" in output_task.output_data:
        output_path = output_task.output_data["response"]

        print(f"\nReview report saved to: {output_path}")

        try:
            with open(output_path, "r", encoding="utf-8") as f:
                md_content = f.read()
            print("\nFinal Review Report Content:\n")
            print(md_content)
        except Exception as e:
            print(f"Error reading review report: {str(e)}")
    else:
        print("\nFinal output task did not complete successfully.")

    if result:
        print("\nWorkflow completed successfully overall.")
    else:
        print("\nWorkflow encountered errors during execution.")
        print("Check the task summary above for details on which tasks failed.")


if __name__ == "__main__":
    main()
