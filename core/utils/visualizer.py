import re
from typing import Any, Dict, List, Optional

import graphviz
import networkx as nx

from core.task import Task
from core.workflow import Workflow


def _extract_dependencies_from_value(value: Any, current_task_id: str) -> List[str]:
    """Extracts task IDs referenced in placeholders within a string or list item."""
    dependencies = []
    # Regex to find ${task_id.output_data...}
    placeholder_regex = r"\${([^.}]+)\.output_data\.[^}]+}"

    if isinstance(value, str):
        matches = re.findall(placeholder_regex, value)
        for ref_task_id in matches:
            if ref_task_id != current_task_id:  # Avoid self-references if they somehow occur
                dependencies.append(ref_task_id)
    elif isinstance(value, list):
        for item in value:
            # Recursively check items in the list
            dependencies.extend(_extract_dependencies_from_value(item, current_task_id))
    elif isinstance(value, dict):
        for dict_value in value.values():
            # Recursively check values in a dictionary
            dependencies.extend(_extract_dependencies_from_value(dict_value, current_task_id))

    return list(set(dependencies))  # Return unique dependencies


def visualize_workflow(workflow: Workflow, filename: str = "workflow_graph", format: str = "pdf", view: bool = False):
    """
    Generates a visual representation of the workflow dependency graph using Graphviz.

    Args:
        workflow: The Workflow object to visualize.
        filename: The base name for the output file (without extension).
        format: The output format (e.g., 'pdf', 'png', 'svg').
        view: If True, automatically opens the generated file.
    """
    dot = graphviz.Digraph(comment=f"Workflow: {workflow.name}")
    dot.attr(rankdir="TB", label=f"Workflow: {workflow.name} (ID: {workflow.id})", fontsize="20")

    # Add nodes (Tasks)
    for task_id, task in workflow.tasks.items():
        # Node styling based on type or status (optional)
        shape = "box"
        style = "filled"
        fillcolor = "lightgrey"  # Default
        if task.is_llm_task:
            fillcolor = "lightblue"
        if task.parallel:
            shape = "ellipse"  # Indicate parallel capability
            fillcolor = "lightyellow"

        label = f"ID: {task.id}\nName: {task.name}"
        if task.condition:
            label += f"\nCond: {task.condition}"

        dot.node(task.id, label=label, shape=shape, style=style, fillcolor=fillcolor)

    # Add edges (Dependencies)
    edge_styles = {
        "data": {"color": "black", "style": "solid", "label": " data"},
        "success": {"color": "green", "style": "dashed", "label": " on_success"},
        "failure": {"color": "red", "style": "dashed", "label": " on_failure"},
        "condition_true": {"color": "blue", "style": "dotted", "label": " if_true"},
        "condition_false": {"color": "orange", "style": "dotted", "label": " if_false"},
    }

    processed_edges = set()  # To avoid duplicate edges

    for task_id, task in workflow.tasks.items():
        # 1. Data Dependencies from Input Placeholders
        if task.input_data:
            for value in task.input_data.values():
                deps = _extract_dependencies_from_value(value, task.id)
                for dep_task_id in deps:
                    if dep_task_id in workflow.tasks:
                        edge = (dep_task_id, task_id)
                        if edge not in processed_edges:
                            dot.edge(dep_task_id, task_id, **edge_styles["data"])
                            processed_edges.add(edge)
                    else:
                        print(f"Warning: Task '{task_id}' references unknown task '{dep_task_id}' in input.")

        # 2. Control Flow Dependencies (Conditional Logic)
        if task.condition:
            # If condition is present, success/failure paths represent the two outcomes
            if task.next_task_id_on_success and task.next_task_id_on_success in workflow.tasks:
                edge = (task_id, task.next_task_id_on_success)
                if edge not in processed_edges:
                    dot.edge(task_id, task.next_task_id_on_success, **edge_styles["condition_true"])
                    processed_edges.add(edge)
            if task.next_task_id_on_failure and task.next_task_id_on_failure in workflow.tasks:
                edge = (task_id, task.next_task_id_on_failure)
                if edge not in processed_edges:
                    dot.edge(task_id, task.next_task_id_on_failure, **edge_styles["condition_false"])
                    processed_edges.add(edge)
        else:
            # If no condition, success/failure paths are direct control flow
            if task.next_task_id_on_success and task.next_task_id_on_success in workflow.tasks:
                edge = (task_id, task.next_task_id_on_success)
                if edge not in processed_edges:
                    dot.edge(task_id, task.next_task_id_on_success, **edge_styles["success"])
                    processed_edges.add(edge)
            if task.next_task_id_on_failure and task.next_task_id_on_failure in workflow.tasks:
                edge = (task_id, task.next_task_id_on_failure)
                if edge not in processed_edges:
                    dot.edge(task_id, task.next_task_id_on_failure, **edge_styles["failure"])
                    processed_edges.add(edge)

        # 3. Implicit Sequential Dependency (Optional - can make graph cluttered)
        # This adds an edge if task A is immediately before task B in task_order
        # AND there isn't already an explicit edge (data or control flow) between them.
        # try:
        #     current_index = workflow.task_order.index(task_id)
        #     if current_index + 1 < len(workflow.task_order):
        #         next_task_id_in_order = workflow.task_order[current_index + 1]
        #         # Check if an edge already exists due to data or control flow
        #         explicit_edge_exists = False
        #         if (task_id, next_task_id_in_order) in processed_edges:
        #             explicit_edge_exists = True
        #         else:
        #             # Check reverse for data deps if next task uses current task's output
        #             next_task_obj = workflow.tasks.get(next_task_id_in_order)
        #             if next_task_obj and next_task_obj.input_data:
        #                  for val in next_task_obj.input_data.values():
        #                       if task_id in _extract_dependencies_from_value(val, next_task_id_in_order):
        #                            explicit_edge_exists = True
        #                            break
        #
        #         if not explicit_edge_exists:
        #              dot.edge(task_id, next_task_id_in_order, style="dotted", color="gray", label=" sequence")
        #              processed_edges.add((task_id, next_task_id_in_order)) # Mark sequence edge
        # except ValueError:
        #     pass # Task not found in order, should not happen

    # Render the graph
    try:
        output_path = dot.render(filename=filename, format=format, cleanup=True, view=view)
        print(f"Workflow graph generated: {output_path}")
    except graphviz.backend.execute.ExecutableNotFound:
        print("\nError: Graphviz executable not found.")
        print("Please install Graphviz (https://graphviz.org/download/) and ensure it's in your system's PATH.")
    except Exception as e:
        print(f"\nError generating graph: {e}")
