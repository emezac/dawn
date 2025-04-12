#!/usr/bin/env python3
"""
Debug panel for the Dawn Framework.

This module provides a web interface for viewing debug information
when debug mode is enabled. It includes:

- System information
- Configuration
- Workflow execution history
- Task performance metrics
- Variable resolution history
- Error logs
"""  # noqa: D202

import os
import sys
import time
import json
import logging
import platform
from typing import Dict, Any, List, Optional
from pathlib import Path

from core.utils.debug import is_debug_mode
from core.config import get, as_dict

# Configure logger
logger = logging.getLogger("dawn.web.debug_panel")

# In-memory store for debug data
_debug_data = {
    "workflows": [],  # Workflow execution history
    "errors": [],     # Errors across the application
    "start_time": time.time(),  # When the application started
    "performance": {
        "workflow_count": 0,
        "task_count": 0,
        "successful_tasks": 0,
        "failed_tasks": 0,
        "total_workflow_time": 0,
        "slowest_workflow": None
    }
}

def register_workflow_execution(workflow_data: Dict[str, Any]) -> None:
    """
    Register a workflow execution with the debug panel.
    
    Args:
        workflow_data: Data about the workflow execution
    """
    if not is_debug_mode():
        return
    
    # Add timestamp if not present
    if "timestamp" not in workflow_data:
        workflow_data["timestamp"] = time.time()
    
    # Add to workflows list (limited to 100 entries)
    _debug_data["workflows"].append(workflow_data)
    if len(_debug_data["workflows"]) > 100:
        _debug_data["workflows"] = _debug_data["workflows"][-100:]
    
    # Update performance metrics
    _debug_data["performance"]["workflow_count"] += 1
    
    # Update task counts
    task_count = len(workflow_data.get("execution_path", []))
    _debug_data["performance"]["task_count"] += task_count
    
    # Update success/failure counts
    for task_id, timing in workflow_data.get("task_timings", {}).items():
        if timing.get("success", False):
            _debug_data["performance"]["successful_tasks"] += 1
        else:
            _debug_data["performance"]["failed_tasks"] += 1
    
    # Update total workflow time
    workflow_time = workflow_data.get("performance_summary", {}).get("total_time", 0)
    _debug_data["performance"]["total_workflow_time"] += workflow_time
    
    # Update slowest workflow
    if not _debug_data["performance"]["slowest_workflow"] or workflow_time > _debug_data["performance"]["slowest_workflow"].get("time", 0):
        _debug_data["performance"]["slowest_workflow"] = {
            "id": workflow_data.get("workflow_id"),
            "name": workflow_data.get("workflow_name"),
            "time": workflow_time
        }
    
    logger.debug(f"Registered workflow execution: {workflow_data.get('workflow_name')}")

def register_error(error_data: Dict[str, Any]) -> None:
    """
    Register an error with the debug panel.
    
    Args:
        error_data: Data about the error
    """
    if not is_debug_mode():
        return
    
    # Add timestamp if not present
    if "timestamp" not in error_data:
        error_data["timestamp"] = time.time()
    
    # Add to errors list (limited to 100 entries)
    _debug_data["errors"].append(error_data)
    if len(_debug_data["errors"]) > 100:
        _debug_data["errors"] = _debug_data["errors"][-100:]
    
    logger.debug(f"Registered error: {error_data.get('error_type')}: {error_data.get('error_message')}")

def get_debug_data() -> Dict[str, Any]:
    """
    Get debug data for the debug panel.
    
    Returns:
        Dictionary containing debug data
    """
    if not is_debug_mode():
        return {"debug_mode": False}
    
    # Calculate uptime
    uptime = time.time() - _debug_data["start_time"]
    
    # Get system information
    system_info = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "node": platform.node(),
        "cpu_count": os.cpu_count(),
        "uptime": uptime,
        "cwd": os.getcwd(),
    }
    
    # Get config information (mask sensitive values)
    config = as_dict()
    masked_config = {}
    for key, value in config.items():
        if isinstance(value, dict):
            masked_config[key] = {}
            for sub_key, sub_value in value.items():
                if sub_key.endswith("_key") or sub_key.endswith("_secret") or "password" in sub_key:
                    masked_config[key][sub_key] = "***MASKED***"
                else:
                    masked_config[key][sub_key] = sub_value
        else:
            if key.endswith("_key") or key.endswith("_secret") or "password" in key:
                masked_config[key] = "***MASKED***"
            else:
                masked_config[key] = value
    
    # Return the debug data
    return {
        "debug_mode": True,
        "system_info": system_info,
        "config": masked_config,
        "workflows": _debug_data["workflows"],
        "errors": _debug_data["errors"],
        "performance": _debug_data["performance"]
    }

async def debug_panel_handler(request) -> Dict[str, Any]:
    """
    Handler for debug panel requests.
    
    Args:
        request: The HTTP request
        
    Returns:
        Response data
    """
    if not is_debug_mode():
        return {"error": "Debug mode is not enabled"}
    
    path_parts = request.path.strip("/").split("/")
    
    # Root path returns general debug data
    if len(path_parts) <= 1:
        return get_debug_data()
    
    # Handle specific paths
    subpath = path_parts[1]
    
    if subpath == "workflows":
        # Get workflow list or specific workflow
        if len(path_parts) > 2:
            workflow_id = path_parts[2]
            for workflow in _debug_data["workflows"]:
                if workflow.get("workflow_id") == workflow_id:
                    return workflow
            return {"error": f"Workflow with ID {workflow_id} not found"}
        else:
            return {"workflows": _debug_data["workflows"]}
    
    elif subpath == "errors":
        # Get error list
        return {"errors": _debug_data["errors"]}
    
    elif subpath == "performance":
        # Get performance metrics
        return {"performance": _debug_data["performance"]}
    
    elif subpath == "system":
        # Get system information
        return {"system_info": get_debug_data()["system_info"]}
    
    elif subpath == "config":
        # Get configuration
        return {"config": get_debug_data()["config"]}
    
    else:
        return {"error": f"Unknown debug panel path: {subpath}"}

def setup_debug_panel(app) -> None:
    """
    Set up the debug panel in a web application.
    
    Args:
        app: The web application
    """
    if not is_debug_mode():
        return
    
    # Register routes
    # Placeholder for actual route registration, which depends on the web framework used
    logger.info("Debug panel enabled at /debug")

# Generate HTML for the debug panel
def get_debug_panel_html() -> str:
    """
    Generate HTML for the debug panel.
    
    Returns:
        HTML for the debug panel
    """
    if not is_debug_mode():
        return "<h1>Debug mode is not enabled</h1>"
    
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dawn Framework Debug Panel</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                line-height: 1.6;
                color: #333;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                background-color: #333;
                color: white;
                padding: 1rem;
                margin-bottom: 1rem;
            }
            .nav {
                background-color: #444;
                padding: 0.5rem;
            }
            .nav a {
                color: white;
                text-decoration: none;
                padding: 0.5rem 1rem;
                display: inline-block;
            }
            .nav a:hover {
                background-color: #555;
            }
            .section {
                margin-bottom: 2rem;
                border: 1px solid #ddd;
                border-radius: 4px;
                overflow: hidden;
            }
            .section-header {
                background-color: #f5f5f5;
                padding: 0.5rem 1rem;
                border-bottom: 1px solid #ddd;
                font-weight: bold;
            }
            .section-content {
                padding: 1rem;
            }
            .table {
                width: 100%;
                border-collapse: collapse;
            }
            .table th, .table td {
                padding: 0.5rem;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            .table th {
                background-color: #f5f5f5;
            }
            .table tr:hover {
                background-color: #f5f5f5;
            }
            .status-success {
                color: green;
            }
            .status-error {
                color: red;
            }
            pre {
                background-color: #f5f5f5;
                padding: 1rem;
                overflow: auto;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Dawn Framework Debug Panel</h1>
        </div>
        <div class="nav">
            <a href="#system">System Info</a>
            <a href="#config">Configuration</a>
            <a href="#workflows">Workflows</a>
            <a href="#performance">Performance</a>
            <a href="#errors">Errors</a>
        </div>
        <div class="container">
            <div id="system" class="section">
                <div class="section-header">System Information</div>
                <div class="section-content">
                    <div id="system-content">Loading system information...</div>
                </div>
            </div>
            <div id="config" class="section">
                <div class="section-header">Configuration</div>
                <div class="section-content">
                    <div id="config-content">Loading configuration...</div>
                </div>
            </div>
            <div id="workflows" class="section">
                <div class="section-header">Workflows</div>
                <div class="section-content">
                    <table class="table" id="workflow-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Tasks</th>
                                <th>Success Rate</th>
                                <th>Duration</th>
                                <th>Timestamp</th>
                                <th>Details</th>
                            </tr>
                        </thead>
                        <tbody id="workflow-body">
                            <tr>
                                <td colspan="7">Loading workflows...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <div id="performance" class="section">
                <div class="section-header">Performance Metrics</div>
                <div class="section-content">
                    <div id="performance-content">Loading performance metrics...</div>
                </div>
            </div>
            <div id="errors" class="section">
                <div class="section-header">Errors</div>
                <div class="section-content">
                    <table class="table" id="error-table">
                        <thead>
                            <tr>
                                <th>Timestamp</th>
                                <th>Type</th>
                                <th>Message</th>
                                <th>Context</th>
                            </tr>
                        </thead>
                        <tbody id="error-body">
                            <tr>
                                <td colspan="4">Loading errors...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <script>
            // Fetch debug data from API
            async function fetchDebugData() {
                try {
                    const response = await fetch('/debug/api');
                    const data = await response.json();
                    
                    if (!data.debug_mode) {
                        document.body.innerHTML = '<h1>Debug mode is not enabled</h1>';
                        return;
                    }
                    
                    // Update system info
                    document.getElementById('system-content').innerHTML = formatSystemInfo(data.system_info);
                    
                    // Update config
                    document.getElementById('config-content').innerHTML = formatConfig(data.config);
                    
                    // Update workflows
                    updateWorkflowTable(data.workflows);
                    
                    // Update performance
                    document.getElementById('performance-content').innerHTML = formatPerformance(data.performance);
                    
                    // Update errors
                    updateErrorTable(data.errors);
                    
                } catch (error) {
                    console.error('Error fetching debug data:', error);
                }
            }
            
            // Format system info
            function formatSystemInfo(info) {
                if (!info) return 'No system information available.';
                
                let html = '<table class="table">';
                for (const [key, value] of Object.entries(info)) {
                    html += `<tr><td><strong>${key}</strong></td><td>${value}</td></tr>`;
                }
                html += '</table>';
                
                return html;
            }
            
            // Format config
            function formatConfig(config) {
                if (!config) return 'No configuration available.';
                
                return `<pre>${JSON.stringify(config, null, 2)}</pre>`;
            }
            
            // Update workflow table
            function updateWorkflowTable(workflows) {
                if (!workflows || workflows.length === 0) {
                    document.getElementById('workflow-body').innerHTML = '<tr><td colspan="7">No workflows found.</td></tr>';
                    return;
                }
                
                let html = '';
                for (const workflow of workflows) {
                    const taskCount = workflow.execution_path ? workflow.execution_path.length : 0;
                    const successRate = workflow.performance_summary ? 
                        `${(workflow.performance_summary.success_rate * 100).toFixed(1)}%` : 'N/A';
                    const duration = workflow.performance_summary ? 
                        `${workflow.performance_summary.total_time.toFixed(2)}s` : 'N/A';
                    const timestamp = new Date(workflow.timestamp * 1000).toLocaleString();
                    
                    html += `
                        <tr>
                            <td>${workflow.workflow_id || 'N/A'}</td>
                            <td>${workflow.workflow_name || 'N/A'}</td>
                            <td>${taskCount}</td>
                            <td>${successRate}</td>
                            <td>${duration}</td>
                            <td>${timestamp}</td>
                            <td><button onclick="showWorkflowDetails('${workflow.workflow_id}')">Details</button></td>
                        </tr>
                    `;
                }
                
                document.getElementById('workflow-body').innerHTML = html;
            }
            
            // Format performance metrics
            function formatPerformance(performance) {
                if (!performance) return 'No performance data available.';
                
                let html = '<table class="table">';
                html += `<tr><td><strong>Total Workflows</strong></td><td>${performance.workflow_count}</td></tr>`;
                html += `<tr><td><strong>Total Tasks</strong></td><td>${performance.task_count}</td></tr>`;
                html += `<tr><td><strong>Successful Tasks</strong></td><td>${performance.successful_tasks}</td></tr>`;
                html += `<tr><td><strong>Failed Tasks</strong></td><td>${performance.failed_tasks}</td></tr>`;
                html += `<tr><td><strong>Total Workflow Time</strong></td><td>${performance.total_workflow_time.toFixed(2)}s</td></tr>`;
                
                if (performance.slowest_workflow) {
                    html += `
                        <tr>
                            <td><strong>Slowest Workflow</strong></td>
                            <td>${performance.slowest_workflow.name} (${performance.slowest_workflow.time.toFixed(2)}s)</td>
                        </tr>
                    `;
                }
                
                html += '</table>';
                
                return html;
            }
            
            // Update error table
            function updateErrorTable(errors) {
                if (!errors || errors.length === 0) {
                    document.getElementById('error-body').innerHTML = '<tr><td colspan="4">No errors found.</td></tr>';
                    return;
                }
                
                let html = '';
                for (const error of errors) {
                    const timestamp = new Date(error.timestamp * 1000).toLocaleString();
                    const context = error.context ? JSON.stringify(error.context) : 'N/A';
                    
                    html += `
                        <tr>
                            <td>${timestamp}</td>
                            <td>${error.error_type || 'N/A'}</td>
                            <td>${error.error_message || 'N/A'}</td>
                            <td><pre>${context}</pre></td>
                        </tr>
                    `;
                }
                
                document.getElementById('error-body').innerHTML = html;
            }
            
            // Show workflow details in a modal
            function showWorkflowDetails(workflowId) {
                // Placeholder for actual implementation
                alert(`Viewing details for workflow ${workflowId} not implemented yet.`);
            }
            
            // Initial fetch
            fetchDebugData();
            
            // Refresh data every 10 seconds
            setInterval(fetchDebugData, 10000);
        </script>
    </body>
    </html>
    """ 