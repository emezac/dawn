# Dawn Framework Example Workflows

This directory contains example workflows that demonstrate the capabilities of the Dawn workflow framework.

## Available Examples

### Real Estate Advisor Workflow

A comprehensive workflow for analyzing real estate properties and providing investment advice.

**Features:**
- Natural language user input processing
- Web search for property listings and market data
- Data analysis and investment recommendations
- Comprehensive report generation
- **Internationally Compatible**: Works with properties worldwide without geographic bias
- **Multilingual Input Recognition**: Understands location, price, and bedroom specifications in multiple languages
- **Multiple Currency Support**: Recognizes 7 major world currencies (USD, EUR, MXP, GBP, JPY, BRL, CAD)
- **Flexible Price Notation**: Supports both full numbers and 'k' notation (e.g., "500k" = 500,000)

**How to run:**
```bash
python real_estate_advisor_flow.py
```

When prompted, enter your real estate search criteria in natural language, for example:
- "I want a 3 bedroom house in Tokyo under 50M yen"
- "Looking for apartments in Paris with 2 bedrooms under 400k euros"
- "Casas en CDMX cerca del estadio azteca con 3 habitaciones por menos de 2M pesos"
- "Properties in London with 2 beds under £500k"

### Trump Tariff Analyzer

Analyzes the impact of tariffs on different countries and economic sectors.

**How to run:**
```bash
python trump_tariff_analyzer.py
```

### Tariff Impact Workflow

Evaluates the economic consequences of tariff changes on global trade and industries.

**How to run:**
```bash
python tariff_impact_workflow.py
```

### Simple Direct Handler Example

A minimal example demonstrating the basic usage of direct handlers in a workflow.

**How to run:**
```bash
python simple_direct_handler_example.py
```

### Dynamic Input Query Flow

Shows how to build a workflow that dynamically processes user input and generates reports.

**How to run:**
```bash
python dynamic_input_query_flow.py
```

## Running Examples

Most examples accept common command-line arguments:

- `--visualize`: Generate a visualization of the workflow instead of executing it
- `--output [FILENAME]`: Specify the output file for the visualization
- `--debug`: Enable detailed debug logging

Example:
```bash
python real_estate_advisor_flow.py --visualize --output workflow.png
```

## Prerequisites

- Python 3.8 or higher
- Dawn framework installed
- OpenAI API key (set as OPENAI_API_KEY environment variable)

## Extending Examples

These examples provide a starting point for building your own workflows. Feel free to modify them or use components from multiple examples to create custom workflows for your specific needs.

### How It Works

1. **User Input**: The workflow extracts location, price constraints, and bedroom requirements from natural language input
2. **Property Search**: Performs a web search to find real estate listings matching the criteria
3. **Market Analysis**: Searches for market trends and data about the specified location
4. **Analysis**: Analyzes the search results to generate insights
5. **Report Generation**: Creates a comprehensive Markdown report with findings and recommendations

### Documentation

For more details on the international capabilities and pattern matching, see:
- `fixes/real_estate_advisor_international_fix.md`

## Other Examples

[Add information about other examples as needed] 