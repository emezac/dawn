# Framework Fixes and Solutions

This directory contains documentation for fixes and solutions to recurring issues in the Dawn AI Agent Framework. Each file documents a specific problem that was encountered, its root cause, the solution implemented, and how to avoid or address it in the future.

## Purpose

The purpose of this directory is to:

1. Document solutions to non-trivial issues for future reference
2. Provide guidance for developers encountering similar problems
3. Prevent the same issues from being repeatedly fixed
4. Serve as a knowledge base for the framework's maintenance

## Format

Each fix documentation follows a standard format:

```
# Issue Name

## Issue
Description of the problem and its symptoms

## Root Cause
Analysis of what caused the issue

## Solution
Detailed explanation of how the issue was fixed

## Implementation Details
Code examples showing before and after changes

## Testing
How the fix was tested and verified

## Additional Notes
Any other relevant information
```

## Current Fixes

- [Graphviz Dependency Fix](graphviz_dependency_fix.md) - Documents how to handle optional graphviz dependency, making the visualization features gracefully degrade when the dependency is missing.
- [Nested JSON in Plan Validation Fix](nested_json_in_plan_validation_fix.md) - Fix for handling nested JSON structures in plan validation that caused schema validation errors.

## Contributing

When fixing significant issues in the framework:

1. Document the issue and solution in a new markdown file in this directory
2. Follow the standard format described above
3. Include code samples, error messages, and other relevant details
4. Reference the fix in relevant code comments
5. Add the new fix to this README

## Usage Guidelines

- Reference these fixes in code comments when implementing similar functionality
- Check this directory when encountering issues to see if a solution already exists
- Use these documents for training new team members on the framework's design and common pitfalls

## Available Fix Documentation

### Python Module Import Fix
- **File**: [python_module_import_fix.md](python_module_import_fix.md)
- **Problem**: Python module import errors when running examples or tests
- **Solution**: Properly configured setup.py and helper scripts for correct PYTHONPATH setup

### Framework Compatibility Patch
- **File**: [framework_compatibility_patch.md](framework_compatibility_patch.md)
- **Problem**: API changes in the framework causing compatibility issues with example code
- **Solution**: Wrapper functions approach for backwards compatibility without monkey patching

### Pytest Compatible Tools
- **File**: [pytest_compatible_tools.md](pytest_compatible_tools.md)
- **Problem**: Tools designed for production use not working well with pytest
- **Solution**: Improved error handling and testability in tool implementations

### Vector Store ID Validation
- **File**: [vector_store_id_guide.md](vector_store_id_guide.md)
- **Affected Files**: Various vector store related files
- **Problem**: Inconsistent vector store ID validation causing test failures
- **Solution**: Enhanced validation functions to ensure vector store IDs start with "vs_"

### Workflow Compatibility Fixes
- **File**: [workflow_compatibility_fixes.md](workflow_compatibility_fixes.md)
- **Problem**: Changes in workflow implementation breaking example code
- **Solution**: Defensive programming techniques to handle different workflow structures

### Smart Compliance Workflow Fix
- **File**: [smart_compliance_workflow_fix.md](smart_compliance_workflow_fix.md)
- **Affected Files**: examples/smart_compliance_workflow.py, run_example.sh
- **Problem**: Custom tool execution and task failures in the smart compliance workflow
- **Solution**: WorkflowEngine patching and DirectHandlerTask implementation for custom tool execution

## Using These Solutions

Each fix document contains:
1. A detailed description of the problem
2. The implemented solution
3. Code examples
4. Best practices for avoiding similar issues
5. Future improvement suggestions

## Simplified Example

A simplified example implementing these fixes can be found at:
```
examples/simplified_compliance_workflow.py
```

This example demonstrates how to use wrapper functions for framework compatibility.

## Contributing

When fixing a significant issue:
1. Document the problem and solution in a markdown file in this directory
2. Follow the established format (Problem, Solution, Code Examples, Best Practices)
3. Update this README.md to include your new fix
4. Consider creating a simplified example demonstrating the fix 