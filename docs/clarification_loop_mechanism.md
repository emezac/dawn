# Clarification Loop Mechanism

## Overview

The Clarification Loop Mechanism allows the "Think & Analyze" planning component to identify ambiguity in user requests and pause the workflow to request additional information before proceeding with plan generation. This creates a more interactive and accurate planning process.

## Key Components

### 1. Ambiguity Detection

The planner LLM prompt is enhanced to identify potential ambiguities in the user request:
- Missing parameters needed for planning
- Multiple possible interpretations of the request
- Vague or underspecified goals
- Insufficient context to choose the appropriate tools/handlers

### 2. Clarification Request Protocol

When ambiguity is detected, the planner outputs a special JSON structure that signals:
- The specific areas of ambiguity
- Questions to ask the user
- Context about why clarification is needed

Example clarification request schema:
```json
{
  "needs_clarification": true,
  "ambiguity_details": [
    {
      "aspect": "search_scope",
      "description": "The search scope is unclear",
      "clarification_question": "Would you like to search in all documents or only recent ones?",
      "possible_options": ["all_documents", "recent_documents"]
    },
    {
      "aspect": "output_format",
      "description": "Output format preference not specified",
      "clarification_question": "How would you like the results formatted?",
      "possible_options": ["summary", "detailed_report", "bullet_points"]
    }
  ]
}
```

### 3. Workflow Pause Mechanism

The workflow engine needs to support pausing execution when clarification is needed:

1. Detect the `needs_clarification` flag in the planner output
2. Store the current workflow state
3. Provide an interface for receiving the user's response
4. Resume workflow execution with the clarified input

### 4. Implementation Approach

#### A. Modify Planning Handler

Update the `plan_user_request_handler` to:
- Check for ambiguity in user requests
- Generate appropriate clarification questions
- Output a well-structured clarification request when needed

#### B. Workflow State Management

Implement a state management solution:
1. Add a `workflow_state` field to the context
2. Use an enum for state tracking: `INITIALIZING`, `PLANNING`, `AWAITING_CLARIFICATION`, `EXECUTING`, etc.
3. Store workflow execution path and clarification history

#### C. UI Integration

Design the UI/chat interface to:
- Display clarification questions to the user
- Collect user responses
- Format responses appropriately for the workflow

#### D. Resume Logic

Implement logic to resume workflow execution:
1. Merge the user's clarification with the original request
2. Restart the planning process with enhanced context
3. Track clarification iterations to prevent excessive loops

## Integration with Chat Planner Workflow

1. Add a new `check_for_ambiguity` step early in the workflow
2. If ambiguity is detected, transition to the `AWAITING_CLARIFICATION` state
3. When user provides clarification, append it to the context and restart planning
4. Set a maximum number of clarification iterations (e.g., 3) to prevent infinite loops

## Technical Considerations

- **Stateful Execution**: Requires persistence of workflow state between user interactions
- **Context Tracking**: Need to track original request + all clarifications for planning
- **LLM Prompt Design**: Critical to instruct the LLM to detect ambiguity without being overly cautious

## Example Flow

1. User: "Find information about the topic"
2. System: (internally) Identifies ambiguity about which "topic" and what "information"
3. System: "I need clarification: What specific topic are you interested in? And what kind of information are you looking for?"
4. User: "I'm interested in renewable energy, specifically recent advancements in solar technology"
5. System: (internally) Restarts planning with combined context
6. System: (proceeds with executing the clarified plan) 