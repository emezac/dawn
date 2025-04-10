import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

from core.agent import Agent
from core.task import Task
from core.tools.registry import ToolRegistry
from core.utils.visualizer import visualize_workflow
from core.workflow import Workflow


def main():
    """Sets up and runs the complex conditional parallel workflow."""
    print("Starting Final Complex Conditional Workflow (Parallel Execution - Cleaned)")
    load_dotenv()  # Load environment variables (.env file)

    # --- Instantiate ToolRegistry ---
    try:
        tool_registry = ToolRegistry()

    except Exception as e:
        print(f"FATAL: Failed to initialize ToolRegistry: {e}")
        return

    # --- Create Agent ---
    try:
        agent = Agent(
            agent_id="complex_cond_parallel_agent_clean",
            name="Complex Conditional Parallel Agent (Clean)",
            tool_registry=tool_registry,
        )
    except Exception as e:
        print(f"FATAL: Failed to initialize Agent: {e}")
        return

    # --- Create Workflow ---
    workflow = Workflow(
        workflow_id="complex_cond_parallel_workflow_clean",
        name="Complex Conditional Parallel Workflow (Clean)",
    )

    # --- Define File Paths ---
    current_dir = os.path.dirname(__file__)
    pdf_dir = os.path.join(current_dir, "pdfs")
    os.makedirs(pdf_dir, exist_ok=True)
    upload_file_path = os.path.join(pdf_dir, "training.pdf")
    if not os.path.exists(upload_file_path):
        try:
            with open(upload_file_path, "w", encoding="utf-8") as f:
                f.write("Dummy content.")

        except Exception as e:
            print(f"Warning: Could not create dummy PDF file: {e}")
    output_dir = os.path.join(current_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_file_path = os.path.join(output_dir, "AI_ethics_summary_cond_parallel_clean.md")

    # --- Task Definitions (Using Corrected Placeholder Syntax) ---
    try:
        task1_upload = Task(
            task_id="upload_file_task",
            name="1. Upload Training Doc",
            is_llm_task=False,
            tool_name="file_upload",
            input_data={"file_path": upload_file_path, "purpose": "assistants"},
            parallel=False,
            next_task_id_on_success="create_vector_store_task",
        )
        task2_create_vs = Task(
            task_id="create_vector_store_task",
            name="2. Create Vector Store",
            is_llm_task=False,
            tool_name="vector_store_create",
            input_data={
                "name": "Training Doc Store Clean",
                "file_ids": ["${upload_file_task.output_data.result}"],  # Correct
            },
            parallel=False,
            next_task_id_on_success="file_search_task",
        )
        task3_file_search = Task(
            task_id="file_search_task",
            name="3. Extract Doc Insights (RAG)",
            is_llm_task=False,
            tool_name="file_read",
            input_data={
                "vector_store_ids": ["${create_vector_store_task.output_data.result}"],  # Correct
                "query": "Extract key insights regarding AI ethics from the training document.",
                "max_num_results": 5,
                "include_search_results": True,
            },
            parallel=True,
            condition="len(output_data.get('result', '')) > 50",
            next_task_id_on_success="generate_summary_task",
            next_task_id_on_failure="regenerate_insights_task",
        )
        task4_web_search = Task(
            task_id="web_search_task",
            name="4. Web Search AI Ethics",
            is_llm_task=False,
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
            parallel=True,
            next_task_id_on_success="generate_summary_task",
            next_task_id_on_failure="default_web_search_task",
        )
        task3b_regenerate = Task(
            task_id="regenerate_insights_task",
            name="3B. Regenerate Doc Insights",
            is_llm_task=True,
            input_data={
                "prompt": "The extracted insights from the document vector store ${create_vector_store_task.output_data.result} were insufficient or extraction failed. Generate a detailed summary of key insights on AI ethics."  # Correct
            },
            parallel=False,
            max_retries=1,
            next_task_id_on_success="generate_summary_task",
        )
        task4b_default_web = Task(
            task_id="default_web_search_task",
            name="4B. Default Web Search Result",
            is_llm_task=True,
            input_data={
                "prompt": "The web search failed. Provide a generalized default summary of recent advancements in AI ethics research (auditing, education, governance)."
            },
            parallel=False,
            max_retries=1,
            next_task_id_on_success="generate_summary_task",
        )
        task5_summarize = Task(
            task_id="generate_summary_task",
            name="5. Generate Combined Summary",
            is_llm_task=True,
            input_data={
                "prompt": (
                    "Create a comprehensive summary on AI ethics using the following sources. Prioritize primary sources. State if a source failed/provided no info.\n\n"
                    "Primary Doc Insights: '${file_search_task.output_data.result}'\n"  # Correct
                    "Regenerated Doc Insights: '${regenerate_insights_task.output_data.response}'\n"  # Correct
                    "Primary Web Search Results: '${web_search_task.output_data.result}'\n"  # Correct
                    "Default Web Summary: '${default_web_search_task.output_data.response}'\n\n"  # Correct
                    "Structure output in Markdown."
                )
            },
            parallel=False,
            max_retries=1,
            next_task_id_on_success="write_markdown_task",
        )
        task6_write_md = Task(
            task_id="write_markdown_task",
            name="6. Write Summary to Markdown",
            is_llm_task=False,
            tool_name="write_markdown",
            input_data={
                "file_path": output_file_path,
                "content": "${generate_summary_task.output_data.response}",  # Correct
            },
            parallel=False,
        )
    except Exception as e:
        print(f"FATAL: Error defining tasks: {e}")
        return

    # --- Add tasks to workflow ---
    try:
        workflow.add_task(task1_upload)
        workflow.add_task(task2_create_vs)
        workflow.add_task(task3_file_search)
        workflow.add_task(task4_web_search)
        workflow.add_task(task3b_regenerate)
        workflow.add_task(task4b_default_web)
        workflow.add_task(task5_summarize)
        workflow.add_task(task6_write_md)

    except Exception as e:
        print(f"FATAL: Error adding tasks to workflow: {e}")
        return

    # --- Visualize the Workflow ---
    print("\nGenerating workflow visualization...")
    # Save the graph in the 'output' directory with a specific name
    viz_filename = os.path.join(output_dir, f"{workflow.id}_graph")
    visualize_workflow(workflow, filename=viz_filename, format="pdf", view=False)  # Set view=True to auto-open
    print("-" * 30)

    # --- Load and run ---
    agent.load_workflow(workflow)
    print("\nRunning workflow asynchronously...")
    results = agent.run_async()

    # --- Print results ---
    print("\n--- Workflow Execution Results ---")
    print(f"Final Workflow Status: {results.get('status', 'N/A')}")
    if "error" in results and results["error"]:
        print(f"Workflow Execution Error: {results['error']}")

    print("\n--- Task Outputs ---")
    tasks_data = results.get("tasks", {})
    if not tasks_data:
        print("No task data available.")

    final_md_file_path = None
    for task_id in workflow.task_order:
        if task_id in tasks_data:
            task_data = tasks_data[task_id]
            print(f"\nTask: {task_data.get('name', 'Unknown')} (ID: {task_id})")
            print(f"  Status: {task_data.get('status', 'N/A')}")
            output = task_data.get("output_data", {})
            if output:
                if "result" in output:
                    # Limit printing potentially large tool results
                    result_preview = str(output["result"])
                    result_preview = result_preview[:200] + "..." if len(result_preview) > 200 else result_preview
                    print(f"  Result (Preview): {result_preview}")
                    if task_id == task6_write_md.id and task_data.get("status") == "completed":
                        final_md_file_path = output["result"]
                elif "response" in output:
                    response_preview = (
                        output["response"][:200] + "..." if len(output["response"]) > 200 else output["response"]
                    )
                    print(f"  Response (Preview): {response_preview}")
                elif "error" in output:
                    print(f"  Error: {output['error']}")
                else:
                    print(f"  Output Data: {output}")
            elif task_data.get("status") not in ["pending"]:
                print("  No output data recorded.")
        # else: print(f"\nTask ID {task_id} not found in results.") # Optional log

    # --- Read and print final Markdown file ---
    if final_md_file_path and os.path.exists(final_md_file_path) and results.get("status") == "completed":
        print(f"\n--- Reading Final Markdown File ({final_md_file_path}) ---")
        try:
            with open(final_md_file_path, "r", encoding="utf-8") as f:
                md_content = f.read()
            print(md_content)
            print("----------------------------------------------------")
        except Exception as e:
            print(f"Error reading final Markdown file: {str(e)}")
    elif results.get("status") == "completed":
        print(f"\nWarning: Workflow completed, but final markdown file not found/read.")
    elif results.get("status") == "failed":
        print("\nWorkflow failed. Markdown file not generated.")

    print(f"\nScript finished. Check output folder for {os.path.basename(output_file_path)}.")


# --- Script Entry Point ---
if __name__ == "__main__":
    main()
