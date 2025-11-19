# Requirements Document

## Introduction

This document specifies the requirements for a stage manager classifier agent built using the strends library in Python. The agent acts as a stage manager helping users complete stages in tasks. It receives user text input and classifies it into one of seven status codes (NEXT, PREVIOUS, EXIT, HELP, CARE, HELLO, UNKNOWN) based on the user's intent. The agent also receives a JSON context representing a task with multiple stages to inform its classification decisions. When the CARE status is detected, the agent integrates with an MCP server to call a caregiver before returning the status.

## Glossary

- **StageManager**: The classifier agent that analyzes user text input and assigns it to one of seven predefined status codes
- **strends Library**: A Python library for building agent-based systems
- **Status Code**: One of seven predefined values: NEXT, PREVIOUS, EXIT, HELP, CARE, HELLO, or UNKNOWN
- **User Input**: Free-form text provided by the user expressing their intent
- **Task Flow Context**: A JSON-structured representation of a task containing task name, description, status, and a list of stages with descriptions and timeouts
- **Stage**: A discrete step within a task flow, containing a stage name, description, and timeout value
- **Task Status**: The current execution state of a task (e.g., "not started", "in progress", "completed")
- **Classification Result**: A JSON response containing the status code and free text message returned by the agent
- **MCP Server**: Model Context Protocol server that provides external service integration capabilities
- **Caregiver Service**: An external service accessible through the MCP server that handles care-related requests

## Requirements

### Requirement 1

**User Story:** As a user, I want to provide text input to the agent, so that the system can understand my intent and classify it appropriately.

#### Acceptance Criteria

1. WHEN a user provides text input to the StageManager THEN the StageManager SHALL accept the input as a string
2. WHEN the text input is empty or contains only whitespace THEN the StageManager SHALL reject the input and return an error response
3. WHEN the text input is provided THEN the StageManager SHALL process the input without modifying the original text
4. WHEN the text input contains special characters or unicode THEN the StageManager SHALL handle them appropriately

### Requirement 2

**User Story:** As a user, I want the agent to classify my text input into one of seven status codes, so that the system can respond appropriately to my intent.

#### Acceptance Criteria

1. WHEN the StageManager receives valid user input THEN the StageManager SHALL return a JSON response containing exactly one status code from the set {NEXT, PREVIOUS, EXIT, HELP, CARE, HELLO, UNKNOWN} and a free text message
2. WHEN the user input indicates a desire to proceed forward THEN the StageManager SHALL return the status code NEXT
3. WHEN the user input indicates a desire to go back THEN the StageManager SHALL return the status code PREVIOUS
4. WHEN the user input indicates a desire to quit or leave THEN the StageManager SHALL return the status code EXIT
5. WHEN the user input requests assistance or information THEN the StageManager SHALL return the status code HELP
6. WHEN the user input expresses concern, emotion, or need for support THEN the StageManager SHALL return the status code CARE
7. WHEN the user input is a greeting or introduction THEN the StageManager SHALL return the status code HELLO
8. WHEN the user input does not clearly match any of the other status code patterns THEN the StageManager SHALL return the status code UNKNOWN
9. WHEN the StageManager returns a status code THEN the StageManager SHALL include a free text message providing context or explanation for the classification

### Requirement 3

**User Story:** As a developer, I want the agent to be built using the strends library, so that it follows established patterns for agent-based systems and is maintainable.

#### Acceptance Criteria

1. WHEN the StageManager is initialized THEN the StageManager SHALL use strends library components for agent structure
2. WHEN the agent processes requests THEN the StageManager SHALL follow strends library patterns for message handling and state management
3. WHEN the agent encounters errors THEN the StageManager SHALL use strends library error handling mechanisms

### Requirement 4

**User Story:** As a user, I want the agent to use the task flow context when making classification decisions, so that the classification is relevant to my current workflow state.

#### Acceptance Criteria

1. WHEN the StageManager receives a JSON task flow context THEN the StageManager SHALL parse the JSON structure containing task, description, status, and stages fields
2. WHEN the task flow context contains a stages array THEN the StageManager SHALL extract all stage information including stage names, descriptions, and timeout values
3. WHEN the task flow context contains the current stage information THEN the StageManager SHALL use the stage to inform classification decisions
4. WHEN the task flow context is malformed or missing required fields THEN the StageManager SHALL return a clear error message
5. WHEN no task flow context is provided THEN the StageManager SHALL classify based solely on the user input text

### Requirement 9

**User Story:** As a user, I want the agent to understand the current stage of my day-to-day task from my text input, so that the classification is contextually aware of where I am in the workflow.

#### Acceptance Criteria

1. WHEN the user input contains stage indicators THEN the StageManager SHALL extract the current stage information from the text
2. WHEN the extracted stage information conflicts with the JSON task flow context THEN the StageManager SHALL prioritize the stage information from the user input
3. WHEN the user input does not contain explicit stage information THEN the StageManager SHALL use the stage from the JSON task flow context if available
4. WHEN the current stage indicates the beginning of a task flow THEN the StageManager SHALL consider this when classifying PREVIOUS requests
5. WHEN the current stage indicates the end of a task flow THEN the StageManager SHALL consider this when classifying NEXT requests

### Requirement 5

**User Story:** As a developer, I want the agent to support configurable classification rules, so that the system can be adapted to different task categorization schemes.

#### Acceptance Criteria

1. WHEN the StageManager is initialized with a configuration THEN the StageManager SHALL load classification rules from the provided configuration
2. WHEN classification rules are updated THEN the StageManager SHALL apply the new rules to subsequent classifications
3. WHEN no configuration is provided THEN the StageManager SHALL use default classification rules

### Requirement 6

**User Story:** As a user, I want the agent to handle ambiguous or unclear input gracefully, so that I receive a reasonable classification even when my intent is not perfectly clear.

#### Acceptance Criteria

1. WHEN the user input is ambiguous between multiple status codes THEN the StageManager SHALL return the most likely status code based on context
2. WHEN the user input does not clearly match any status code pattern THEN the StageManager SHALL return the UNKNOWN status code
3. WHEN the user input contains multiple intents THEN the StageManager SHALL prioritize the primary intent for classification

### Requirement 7

**User Story:** As a system administrator, I want the agent to integrate with an MCP server for caregiver services, so that care requests can be handled by external support systems.

#### Acceptance Criteria

1. WHEN the StageManager is initialized THEN the StageManager SHALL establish a connection to the MCP Server
2. WHEN the MCP Server is unavailable during initialization THEN the StageManager SHALL log a warning and continue operation
3. WHEN the connection to the MCP Server fails THEN the StageManager SHALL handle the failure gracefully without crashing

### Requirement 8

**User Story:** As a user, I want the system to notify a caregiver when I express a need for care, so that I can receive timely support.

#### Acceptance Criteria

1. WHEN the StageManager determines the status code is CARE THEN the StageManager SHALL call the Caregiver Service through the MCP Server before returning the status
2. WHEN the Caregiver Service call succeeds THEN the StageManager SHALL return the CARE status code with confirmation of the caregiver notification
3. WHEN the Caregiver Service call fails THEN the StageManager SHALL return the CARE status code with an error indication
4. WHEN the MCP Server is unavailable THEN the StageManager SHALL return the CARE status code without caregiver notification and log the failure
