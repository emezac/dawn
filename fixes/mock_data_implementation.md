# Mock Data Implementation Best Practices

## Issue

Several workflows, including the `tariff_impact_workflow.py` and `trump_tariff_analyzer.py`, needed to handle scenarios where external data retrieval (particularly web searches) might fail. This required implementing fallback mock data mechanisms to ensure workflows could continue execution in these failure scenarios. However, there was inconsistency in how mock data was implemented, leading to potential confusion and maintenance challenges.

## Root Cause

The root cause of the issue was twofold:

1. **Inconsistent implementation patterns**: Different workflows implemented mock data fallbacks in various ways, sometimes using command-line flags, sometimes using try-except blocks with fallbacks, and sometimes using dedicated mock data functions.

2. **Unclear separation of concerns**: In some implementations, mock data generation was mixed with data retrieval logic, making it difficult to test and maintain.

## Solution

A standardized pattern for implementing mock data fallbacks in Dawn workflows was established, with the following key principles:

1. **Explicit mock data control**: Use command-line arguments (like `--use_mock_data`) to explicitly control when mock data should be used
2. **Graceful fallbacks**: Automatically fall back to mock data when external services fail, with appropriate logging
3. **Separated mock data definitions**: Keep mock data generation logic separate from the main data retrieval functions
4. **Realistic mock data**: Design mock data to closely mimic the structure of real data
5. **Transparent indication**: Clearly indicate when mock data is being used, both in logs and in results

## Implementation Details

The Trump Tariff Analyzer workflow provides a good reference implementation:

```python
def trump_tariff_search_tool(task: ToolInvocation) -> dict:
    """
    Performs targeted search for information about Trump's tariff policies.
    """
    try:
        # Extract parameters
        query = task.parameters.get("query", "")
        focus_areas = task.parameters.get("focus_areas", ["impact", "countries", "sectors"])
        
        if not query:
            query = "Trump tariff policies impact global economy"
        
        # Enhance query with focus areas
        enhanced_query = f"Trump {query}"
        if "countries" in focus_areas:
            enhanced_query += " affected countries"
        if "sectors" in focus_areas:
            enhanced_query += " affected industries sectors"
        if "impact" in focus_areas:
            enhanced_query += " economic impact"
        
        logger.info(f"Performing Trump tariff search with query: {enhanced_query}")
        
        # Use web search tool
        try:
            web_search_tool = WebSearchTool()
            result_text = web_search_tool.perform_search(enhanced_query)
            
            # Parse and structure the results
            search_results = {
                "query": enhanced_query,
                "timestamp": datetime.now().isoformat(),
                "results": [{
                    "content": result_text,
                    "title": "Trump Tariff Analysis",
                    "url": "https://search-results.com/trump-tariffs"
                }],
                "focus_areas": focus_areas
            }
            
            return {
                "success": True,
                "result": search_results
            }
        except Exception as e:
            logger.warning(f"Web search failed: {e}, using fallback data")
            # Fallback to mock data
            return {
                "success": True,
                "result": {
                    "query": enhanced_query,
                    "timestamp": datetime.now().isoformat(),
                    "results": [{
                        "content": "Trump has imposed tariffs on various countries including China, European Union, Canada, and Mexico. The tariffs range from 10% to 25% on various goods including steel, aluminum, and consumer products. The economic impact has been significant with retaliatory tariffs from affected countries and disruption to global supply chains.",
                        "title": "Trump Tariff Impact Analysis (Mock Data)",
                        "url": "https://example.com/mock-trump-tariffs"
                    }],
                    "focus_areas": focus_areas
                }
            }
    except Exception as e:
        logger.error(f"Error in trump_tariff_search_tool: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to retrieve tariff data: {str(e)}"
        }
```

In the `main()` function, explicit control via command-line arguments is provided:

```python
# Parse command line arguments
parser = argparse.ArgumentParser(description="Run Trump Tariff Analyzer workflow")
parser.add_argument("--query", default="How have Trump's tariff policies affected global trade?",
                    help="Query for Trump tariff analysis")
parser.add_argument("--use_mock_data", action="store_true",
                    help="Use mock data instead of web search")
parser.add_argument("--save_report", action="store_true", default=True,
                    help="Save the generated report to a file")
```

For more complex mock data scenarios, consider extracting mock data into a dedicated function:

```python
def get_mock_tariff_data(query: str, focus_areas: List[str]) -> dict:
    """
    Generate mock tariff data that mimics the structure of real data.
    Used when web search fails or when explicitly requested.
    """
    return {
        "query": query,
        "timestamp": datetime.now().isoformat(),
        "results": [{
            "content": "Mock tariff data content...",
            "title": "Mock Tariff Analysis",
            "url": "https://example.com/mock-data"
        }],
        "focus_areas": focus_areas,
        "is_mock": True  # Explicitly indicate this is mock data
    }
```

## Testing

To test the mock data implementation:

1. Run the workflow with the `--use_mock_data` flag to verify it works correctly with mock data
2. Temporarily modify the web search function to raise an exception to verify fallback mechanism
3. Compare the structure of mock data with real data to ensure compatibility
4. Verify that appropriate warning logs are generated when falling back to mock data

## Best Practices

1. **Explicit Control**: Always provide a command-line flag or configuration option to explicitly use mock data for testing purposes.

2. **Transparent Fallbacks**: When using fallback mock data due to external service failures, clearly log warnings to indicate this is happening.

3. **Structural Compatibility**: Ensure mock data closely mirrors the structure of real data to prevent downstream processing issues.

4. **Clear Indication**: Add an indicator field (e.g., `is_mock: true`) to help distinguish mock data from real data.

5. **Separate Definition**: Extract mock data generation into separate functions to improve maintainability.

6. **Realistic but Simplified**: Make mock data realistic enough for testing but don't overcomplicate it.

7. **Documentation**: Document how mock data is implemented and how to trigger it in tests or development.

## Related Documentation

- [Workflow Patterns Documentation](../docs/workflow_patterns.md)
- [Example Workflows Documentation](../docs/example_workflows.md)
- [Testing Framework](../docs/testing_framework.md) 