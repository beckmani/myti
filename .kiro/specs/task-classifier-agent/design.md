# Design Document

## Overview

The StageManager is a classifier agent built using the strends library in Python that helps users navigate through multi-stage tasks. It receives user text input and classifies it into one of seven status codes (NEXT, PREVIOUS, EXIT, HELP, CARE, HELLO, UNKNOWN) based on the user's intent. The agent uses a JSON task context containing task information and stages to make contextually aware classification decisions. When the CARE status is detected, the agent integrates with an MCP (Model Context Protocol) server to notify a caregiver before returning the status.

The system is designed to be a conversational interface for task navigation, where users can express their intent in natural language and receive appropriate status codes that drive the task flow logic.

## Architecture

The StageManager follows a layered architecture with clear separation of concerns:

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface Layer                  │
│              (External System/Application)               │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ User Input + Task Context (JSON)
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   StageManager Agent                     │
│                  (strends-based Agent)                   │
│  ┌─────────────────────────────────────────────────┐   │
│  │         Input Validation & Parsing              │   │
│  └──────────────────┬──────────────────────────────┘   │
│                     │                                    │
│  ┌──────────────────▼──────────────────────────────┐   │
│  │      Classification Engine                      │   │
│  │  - Pattern Matching                             │   │
│  │  - Context Analysis                             │   │
│  │  - Stage Awareness                              │   │
│  └──────────────────┬──────────────────────────────┘   │
│                     │                                    │
│  ┌──────────────────▼──────────────────────────────┐   │
│  │      Response Generator                         │   │
│  └──────────────────┬──────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Status Code = CARE?
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   MCP Server Client                      │
│              (Caregiver Service Integration)             │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
              JSON Response
         {status: "...", message: "..."}
```

### Component Responsibilities

1. **Input Validation & Parsing**: Validates user text input and parses JSON task context
2. **Classification Engine**: Core logic for determining the appropriate status code
3. **Response Generator**: Formats the classification result as JSON with status code and message
4. **MCP Server Client**: Handles communication with external caregiver service

## Components and Interfaces

### 1. StageManager Agent (Main Component)

The primary agent class built using the strends library.

**Interface:**
```python
class StageManager:
    def __init__(self, config: Optional[Dict] = None, mcp_client: Optional[MCPClient] = None):
        """
        Initialize the StageManager agent.
        
        Args:
            config: Optional configuration dictionary for classification rules
            mcp_client: Optional MCP client for caregiver service integration
        """
        pass
    
    def classify(self, user_input: str, task_context: Optional[Dict] = None) -> Dict:
        """
        Classify user input and return status code with message.
        
        Args:
            user_input: User's text input
            task_context: Optional JSON task context with stages
            
        Returns:
            Dictionary with 'status' and 'message' keys
            
        Raises:
            ValueError: If input is invalid
            JSONDecodeError: If task_context is malformed
        """
        pass
```

### 2. Input Validator

Validates and sanitizes user input and task context.

**Interface:**
```python
class InputValidator:
    @staticmethod
    def validate_user_input(user_input: str) -> bool:
        """Validate user text input is not empty or whitespace-only."""
        pass
    
    @staticmethod
    def validate_task_context(task_context: Dict) -> bool:
        """Validate task context has required fields: task, description, status, stages."""
        pass
    
    @staticmethod
    def parse_task_context(task_json: str) -> Dict:
        """Parse JSON string to task context dictionary."""
        pass
```

### 3. Classification Engine

Core classification logic with pattern matching and context awareness.

**Interface:**
```python
class ClassificationEngine:
    def __init__(self, config: Optional[Dict] = None):
        """Initialize with optional classification rules configuration."""
        pass
    
    def classify_intent(self, user_input: str, task_context: Optional[Dict] = None) -> str:
        """
        Determine the status code from user input and context.
        
        Returns one of: NEXT, PREVIOUS, EXIT, HELP, CARE, HELLO, UNKNOWN
        """
        pass
    
    def extract_stage_info(self, user_input: str, task_context: Optional[Dict] = None) -> Optional[str]:
        """Extract current stage information from input or context."""
        pass
    
    def is_at_first_stage(self, task_context: Dict, current_stage: str) -> bool:
        """Check if current stage is the first stage."""
        pass
    
    def is_at_last_stage(self, task_context: Dict, current_stage: str) -> bool:
        """Check if current stage is the last stage."""
        pass
```

### 4. Response Generator

Generates JSON responses with status codes and contextual messages.

**Interface:**
```python
class ResponseGenerator:
    @staticmethod
    def generate_response(status_code: str, context: Optional[Dict] = None) -> Dict:
        """
        Generate JSON response with status code and message.
        
        Args:
            status_code: One of the seven status codes
            context: Optional context for generating appropriate message
            
        Returns:
            Dictionary with 'status' and 'message' keys
        """
        pass
```

### 5. MCP Client

Handles communication with the MCP server for caregiver notifications.

**Interface:**
```python
class MCPClient:
    def __init__(self, server_url: str, timeout: int = 30):
        """Initialize MCP client with server URL."""
        pass
    
    def connect(self) -> bool:
        """Establish connection to MCP server. Returns True if successful."""
        pass
    
    def call_caregiver(self, user_input: str, task_context: Optional[Dict] = None) -> bool:
        """
        Call caregiver service through MCP server.
        
        Returns True if successful, False otherwise.
        """
        pass
    
    def is_connected(self) -> bool:
        """Check if connection to MCP server is active."""
        pass
```

## Data Models

### Task Context Structure

```python
{
    "task": str,              # Task name/identifier
    "description": str,       # Task description
    "status": str,           # Task status (e.g., "not started", "in progress", "completed")
    "stages": [              # List of stages
        {
            "stage": str,           # Stage name
            "description": str,     # Stage description
            "timeout": int          # Timeout in seconds
        }
    ]
}
```

### Classification Response Structure

```python
{
    "status": str,    # One of: NEXT, PREVIOUS, EXIT, HELP, CARE, HELLO, UNKNOWN
    "message": str    # Contextual message explaining the classification
}
```

### Configuration Structure

```python
{
    "classification_rules": {
        "NEXT": ["next", "continue", "proceed", "forward", "go on"],
        "PREVIOUS": ["back", "previous", "return", "go back"],
        "EXIT": ["exit", "quit", "leave", "stop", "end"],
        "HELP": ["help", "assist", "support", "call"],
        "CARE": ["worried", "anxious", "scared", "concerned", "upset"],
        "HELLO": ["hello", "hi", "hey", "greetings"]
    },
    "mcp_server": {
        "url": str,
        "timeout": int
    }
}
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Input acceptance
*For any* non-empty, non-whitespace string, the StageManager should accept it as valid input without raising an exception.
**Validates: Requirements 1.1**

### Property 2: Whitespace rejection
*For any* string composed entirely of whitespace characters (spaces, tabs, newlines), the StageManager should reject the input and return an error response.
**Validates: Requirements 1.2**

### Property 3: Input immutability
*For any* valid user input string, after processing by the StageManager, the original input string should remain unchanged.
**Validates: Requirements 1.3**

### Property 4: Unicode handling
*For any* string containing unicode characters or special characters, the StageManager should process it without raising encoding errors or exceptions.
**Validates: Requirements 1.4**

### Property 5: Response structure validity
*For any* valid user input, the StageManager should return a JSON response containing exactly one status code from {NEXT, PREVIOUS, EXIT, HELP, CARE, HELLO, UNKNOWN} and a non-empty message field.
**Validates: Requirements 2.1, 2.9**

### Property 6: Task context parsing
*For any* valid JSON task context with required fields (task, description, status, stages), the StageManager should parse it without errors and extract all stage information.
**Validates: Requirements 4.1, 4.2**

### Property 7: Context influences classification
*For any* user input that could be ambiguous, providing different task contexts (with different current stages) should potentially result in different classification decisions, demonstrating context awareness.
**Validates: Requirements 4.3**

### Property 8: Malformed context handling
*For any* malformed JSON or task context missing required fields, the StageManager should return a clear error message without crashing.
**Validates: Requirements 4.4**

### Property 9: Configuration loading
*For any* valid configuration dictionary with classification rules, the StageManager should load and apply those rules to subsequent classifications.
**Validates: Requirements 5.1, 5.2**

### Property 10: Stage extraction from input
*For any* user input containing explicit stage indicators (e.g., "at stage 2"), the StageManager should extract the stage information and use it in classification decisions.
**Validates: Requirements 9.1**

### Property 11: Stage boundary awareness
*For any* task context where the current stage is at the beginning or end of the stages array, the StageManager should consider these boundaries when classifying PREVIOUS or NEXT requests respectively.
**Validates: Requirements 9.4, 9.5**

### Property 12: CARE triggers MCP call
*For any* user input that results in CARE status classification, the StageManager should attempt to call the Caregiver Service through the MCP Server before returning the response.
**Validates: Requirements 8.1**

## Error Handling

The StageManager implements comprehensive error handling at multiple levels:

### Input Validation Errors

- **Empty/Whitespace Input**: Returns `{"status": "ERROR", "message": "Input cannot be empty or whitespace-only"}`
- **Invalid Unicode**: Handles encoding errors gracefully and attempts to process with fallback encoding
- **None Input**: Returns `{"status": "ERROR", "message": "Input cannot be None"}`

### Task Context Errors

- **Malformed JSON**: Returns `{"status": "ERROR", "message": "Invalid JSON format in task context: {error_details}"}`
- **Missing Required Fields**: Returns `{"status": "ERROR", "message": "Task context missing required field: {field_name}"}`
- **Invalid Stage Structure**: Returns `{"status": "ERROR", "message": "Invalid stage structure in task context"}`

### MCP Server Errors

- **Connection Failure**: Logs warning and continues operation without MCP integration
- **Call Failure During CARE**: Returns CARE status with message indicating caregiver notification failed
- **Timeout**: Logs timeout and returns CARE status with appropriate message

### Configuration Errors

- **Invalid Configuration Format**: Logs warning and falls back to default configuration
- **Missing Classification Rules**: Uses default rules for missing status codes

### General Error Handling Strategy

1. **Fail Gracefully**: Never crash the agent; always return a valid response
2. **Informative Messages**: Provide clear error messages that help diagnose issues
3. **Logging**: Log all errors with appropriate severity levels
4. **Fallback Behavior**: Use sensible defaults when configuration or external services fail
5. **Error Propagation**: Return errors in the same JSON format as successful responses

## Testing Strategy

The StageManager will be tested using a dual approach combining unit tests and property-based tests to ensure comprehensive coverage.

### Property-Based Testing

We will use **Hypothesis** as the property-based testing library for Python. Each property-based test will:
- Run a minimum of 100 iterations with randomly generated inputs
- Be tagged with a comment referencing the specific correctness property from this design document
- Use the format: `# Feature: task-classifier-agent, Property {number}: {property_text}`

**Property-Based Test Coverage:**

1. **Property 1-4 (Input Handling)**: Generate random strings with various characteristics (unicode, whitespace, special chars) and verify acceptance/rejection behavior
2. **Property 5 (Response Structure)**: Generate random valid inputs and verify all responses have correct structure
3. **Property 6-8 (Context Parsing)**: Generate random task contexts (valid and invalid) and verify parsing behavior
4. **Property 9 (Configuration)**: Generate random configuration dictionaries and verify they are applied
5. **Property 10-11 (Stage Awareness)**: Generate random stage indicators and task contexts to verify stage extraction and boundary handling
6. **Property 12 (CARE Flow)**: Generate care-indicating inputs and verify MCP integration

### Unit Testing

Unit tests will cover specific examples and integration points:

**Core Classification Tests:**
- Test each status code with representative examples (NEXT: "continue", "next"; PREVIOUS: "go back"; EXIT: "quit"; HELP: "help me"; CARE: "I'm worried"; HELLO: "hello"; UNKNOWN: "banana")
- Test ambiguous inputs with different contexts
- Test multi-intent inputs

**MCP Integration Tests:**
- Test successful MCP connection
- Test MCP unavailable during initialization
- Test successful caregiver call
- Test failed caregiver call
- Test MCP timeout

**Configuration Tests:**
- Test initialization with custom configuration
- Test initialization without configuration (defaults)
- Test configuration updates

**Edge Cases:**
- Test PREVIOUS at first stage
- Test NEXT at last stage
- Test empty stages array
- Test single-stage task
- Test conflicting stage information (input vs context)

### Integration Testing

End-to-end tests that verify the complete flow:
- User input → Classification → Response generation
- User input → CARE detection → MCP call → Response
- User input with context → Context-aware classification → Response

### Test Organization

```
tests/
├── unit/
│   ├── test_input_validator.py
│   ├── test_classification_engine.py
│   ├── test_response_generator.py
│   └── test_mcp_client.py
├── property/
│   ├── test_input_properties.py
│   ├── test_classification_properties.py
│   ├── test_context_properties.py
│   └── test_care_flow_properties.py
└── integration/
    └── test_stage_manager_integration.py
```

## Implementation Notes

### strends Library Integration

The StageManager will be implemented as a strends agent with the following structure:

1. **Agent Definition**: Use strends' agent decorator to define the StageManager
2. **Message Handling**: Implement message handlers for classification requests
3. **State Management**: Use strends' state management for tracking configuration and MCP connection status
4. **Error Handling**: Leverage strends' error handling patterns

### Classification Algorithm

The classification engine will use a multi-stage approach:

1. **Preprocessing**: Normalize input (lowercase, strip whitespace)
2. **Pattern Matching**: Check against configured patterns for each status code
3. **Context Analysis**: Consider task context and current stage
4. **Confidence Scoring**: Assign confidence scores to potential matches
5. **Decision**: Select highest confidence match or UNKNOWN if below threshold

### MCP Server Integration

The MCP client will be implemented as a separate module that:

1. Establishes connection during initialization (non-blocking)
2. Provides async methods for calling caregiver service
3. Implements retry logic with exponential backoff
4. Handles timeouts gracefully
5. Logs all MCP interactions for debugging

### Performance Considerations

- **Caching**: Cache compiled regex patterns for classification rules
- **Lazy Loading**: Load MCP client only when needed
- **Async Operations**: Use async/await for MCP calls to avoid blocking
- **Input Size Limits**: Limit user input to reasonable size (e.g., 1000 characters)

### Security Considerations

- **Input Sanitization**: Sanitize user input to prevent injection attacks
- **JSON Validation**: Validate JSON structure before parsing
- **MCP Authentication**: Support authentication tokens for MCP server
- **Rate Limiting**: Implement rate limiting for MCP calls to prevent abuse
- **Logging**: Avoid logging sensitive information (PII)
