"""
Example of a simple workflow using the AI Agent Framework.

This example demonstrates how to create a simple workflow with tasks
that use both LLM and tools, and how to execute it with an agent.
"""

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Add parent directory to path to import the framework
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.task import Task
from core.workflow import Workflow
from core.agent import Agent
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
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
    )
    return response.choices[0].message.content.strip()

def execute_llm_task(task):
    """Execute a task that requires LLM processing."""
    prompt = task.input_data["prompt"]
    response = call_openai(prompt)
    task.output_data = {"response": response}

def main():
    """Run a simple example workflow."""
    print("Starting AI Agent Framework Example")
    
    # Create an agent
    agent = Agent(
        agent_id="example_agent",
        name="Example Agent",
    )
    
    # Register tools
    agent.register_tool("calculate", calculate)
    agent.register_tool("check_length", check_length)
    
    # Create a workflow
    workflow = Workflow(
        workflow_id="example_workflow",
        name="Example Workflow"
    )
    
    # Task 1: Generate a topic for an email using LLM
    task1 = Task(
        task_id="generate_topic",
        name="Generate Email Topic",
        is_llm_task=True,
        input_data={
            "prompt": "Generate a professional topic for a business email. Keep it concise."
        },
        max_retries=1
    )
    
    # Task 2: Generate email content using the topic from Task 1
    task2 = Task(
        task_id="generate_email",
        name="Generate Email Content",
        is_llm_task=True,
        input_data={
            "prompt": "Write a professional business email with the following topic: ${generate_topic}.output_data.response"
        },
        max_retries=1
    )
    
    # Task 3: Check the length of the generated email
    task3 = Task(
        task_id="check_email_length",
        name="Check Email Length",
        is_llm_task=False,
        tool_name="check_length",
        input_data={
            "content": "${generate_email}.output_data.response",
            "min_length": 100,
            "max_length": 500
        }
    )
    
    # Task 4A: If email is too short, generate a longer one
    task4a = Task(
        task_id="generate_longer_email",
        name="Generate Longer Email",
        is_llm_task=True,
        input_data={
            "prompt": "The email you wrote is too short. Please expand on the email with topic: ${generate_topic}.output_data.response. Make it more detailed and at least 200 words."
        },
        max_retries=1
    )
    
    # Task 4B: If email is too long, generate a shorter one
    task4b = Task(
        task_id="generate_shorter_email",
        name="Generate Shorter Email",
        is_llm_task=True,
        input_data={
            "prompt": "The email you wrote is too long. Please make a more concise version of the email with topic: ${generate_topic}.output_data.response. Keep it under 300 words."
        },
        max_retries=1
    )
    
    # Task 5: Calculate some metrics (dummy task to demonstrate tool usage)
    task5 = Task(
        task_id="calculate_metrics",
        name="Calculate Email Metrics",
        is_llm_task=False,
        tool_name="calculate",
        input_data={
            "operation": "multiply",
            "a": 2,
            "b": 3
        }
    )
    
    # Task 6: Final summary
    task6 = Task(
        task_id="final_summary",
        name="Generate Summary",
        is_llm_task=True,
        input_data={
            "prompt": "Summarize the email creation process. The final email has a topic of '${generate_topic}.output_data.response' and the calculated metric is ${calculate_metrics}.output_data.response."
        }
    )
    
    # Add tasks to workflow
    workflow.add_task(task1)
    workflow.add_task(task2)
    workflow.add_task(task3)
    workflow.add_task(task4a)
    workflow.add_task(task4b)
    workflow.add_task(task5)
    workflow.add_task(task6)
    
    # Set up conditional logic
    task3.next_task_id_on_success = "calculate_metrics"  # Default path if length is OK
    
    # Load workflow into agent
    agent.load_workflow(workflow)
    
    # Run the workflow
    results = agent.run()
    
    # Execute LLM tasks
    for task_id, task in workflow.tasks.items():
        if task.is_llm_task:
            execute_llm_task(task)
    
    # Print results
    print("\nWorkflow Results:")
    print(f"Status: {results['status']}")
    
    # Print task outputs
    print("\nTask Outputs:")
    for task_id, task_data in results['tasks'].items():
        print(f"\n{task_data['name']} (ID: {task_id}):")
        print(f"Status: {task_data['status']}")
        
        if 'output_data' in task_data and task_data['output_data']:
            if 'response' in task_data['output_data']:
                print(f"Output: {task_data['output_data']['response']}")
            elif 'error' in task_data['output_data']:
                print(f"Error: {task_data['output_data']['error']}")
    
    print("\nExample completed!")


if __name__ == "__main__":
    main()