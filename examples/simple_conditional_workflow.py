"""
Conditional Workflow Example using the AI Agent Framework.

This workflow demonstrates conditional execution:
1. Generate an email topic (LLM).
2. Generate email content using the topic (LLM).
3. Check the length of the generated email (tool: check_length).
   - If the email is too short, branch to generate a longer email.
   - Otherwise, proceed to calculate metrics.
4. (Conditional) Generate a longer email if needed (LLM).
5. Calculate email metrics (tool: calculate).
6. Generate a final summary (LLM).

The engine will follow the failure branch (next_task_id_on_failure) when check_length fails.
"""

import os
import sys

# Add parent directory to path to import the framework modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from openai import OpenAI

from core.agent import Agent
from core.task import Task
from core.workflow import Workflow
from tools.basic_tools import calculate, check_length

# Load environment variables from .env file
load_dotenv()

# Instantiate the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def call_openai(prompt):
    """Helper function to call OpenAI API."""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()


def execute_llm_task(task):
    """Execute a task that requires LLM processing."""
    prompt = task.input_data["prompt"]
    response = call_openai(prompt)
    task.output_data = {"response": response}


def main():
    print("Starting Conditional Workflow Example")

    # Create an agent
    agent = Agent(agent_id="conditional_agent", name="Conditional Agent")

    # Register tools (existing basic tools)
    agent.register_tool("calculate", calculate)
    agent.register_tool("check_length", check_length)

    # Create a workflow
    workflow = Workflow(workflow_id="conditional_workflow", name="Conditional Workflow Example")

    # Task 1: Generate an email topic (LLM task)
    task1 = Task(
        task_id="generate_topic",
        name="Generate Email Topic",
        is_llm_task=True,
        input_data={"prompt": "Generate a professional topic for a business email. Keep it concise."},
        max_retries=1,
        next_task_id_on_success="generate_email",
    )

    # Task 2: Generate email content using the topic (LLM task)
    task2 = Task(
        task_id="generate_email",
        name="Generate Email Content",
        is_llm_task=True,
        input_data={
            "prompt": "Write a professional business email with the following topic: ${generate_topic}.output_data.response"
        },
        max_retries=1,
        next_task_id_on_success="check_email_length",
    )

    # Task 3: Check the length of the generated email (tool task)
    # If the check fails (i.e. email is too short), branch to generate a longer email.
    # Otherwise, continue to calculate metrics.
    task3 = Task(
        task_id="check_email_length",
        name="Check Email Length",
        is_llm_task=False,
        tool_name="check_length",
        input_data={
            "content": "${generate_email}.output_data.response",
            "min_length": 100,
            "max_length": 500,
        },
        next_task_id_on_success="calculate_metrics",
        next_task_id_on_failure="generate_longer_email",
    )

    # Task 4: (Conditional) Generate a longer email (LLM task) if the original email is too short.
    task4 = Task(
        task_id="generate_longer_email",
        name="Generate Longer Email",
        is_llm_task=True,
        input_data={
            "prompt": "The email you wrote is too short. Please expand on the email with topic: ${generate_topic}.output_data.response. Make it more detailed and at least 200 words."
        },
        max_retries=1,
        next_task_id_on_success="calculate_metrics",
    )

    # Task 5: Calculate email metrics (tool task)
    task5 = Task(
        task_id="calculate_metrics",
        name="Calculate Email Metrics",
        is_llm_task=False,
        tool_name="calculate",
        input_data={"operation": "multiply", "a": 2, "b": 3},
        next_task_id_on_success="final_summary",
    )

    # Task 6: Generate a final summary (LLM task)
    task6 = Task(
        task_id="final_summary",
        name="Generate Summary",
        is_llm_task=True,
        input_data={
            "prompt": "Summarize the email creation process. The final email has a topic of '${generate_topic}.output_data.response' and the calculated metric is ${calculate_metrics}.output_data.response."
        },
    )

    # Add tasks to workflow in the order they are defined
    workflow.add_task(task1)
    workflow.add_task(task2)
    workflow.add_task(task3)
    workflow.add_task(task4)
    workflow.add_task(task5)
    workflow.add_task(task6)

    # Note: For this simple conditional workflow, the branching is defined in Task 3.
    # If check_email_length fails (e.g. email is too short), the engine will follow the failure branch
    # and execute generate_longer_email. If it succeeds, it will continue with calculate_metrics.

    # Load workflow into agent and run it
    agent.load_workflow(workflow)
    results = agent.run()

    # Execute LLM tasks
    for task_id, task in workflow.tasks.items():
        if task.is_llm_task:
            execute_llm_task(task)

    # Print results
    print("\nWorkflow Results:")
    print(f"Status: {results['status']}")
    print("\nTask Outputs:")
    for task_id, task_data in results["tasks"].items():
        print(f"\n{task_data['name']} (ID: {task_id}):")
        print(f"Status: {task_data['status']}")
        if "output_data" in task_data and task_data["output_data"]:
            if "response" in task_data["output_data"]:
                print(f"Output: {task_data['output_data']['response']}")
            elif "error" in task_data["output_data"]:
                print(f"Error: {task_data['output_data']['error']}")

    print("\nConditional Workflow Example completed!")


if __name__ == "__main__":
    main()
