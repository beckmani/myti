# Design Document

## Overview

The StageManager is a classifier agent in Python that helps users navigate through multi-stage tasks. It receives user text input and classifies it into one of seven status codes (NEXT, PREVIOUS, EXIT, HELP, CARE, HELLO, UNKNOWN) based on the user's intent using a Large Language Model (LLM) for intelligent natural language understanding. The agent uses a JSON task context containing task information and stages to make contextually aware classification decisions.

The system is designed to be a conversational interface for task navigation, where users can express their intent in natural language and receive appropriate status codes that drive the task flow logic. By leveraging an LLM, the system can handle complex, ambiguous, and varied natural language expressions with high accuracy.

The agent follows established Python design patterns with clear separation of concerns, modular components, and consistent error handling throughout.

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
│                  (Python-based Agent)                    │
│  ┌─────────────────────────────────────────────────┐   │
│  │         Input Validation & Parsing              │   │
│  └──────────────────┬──────────────────────────────┘   │
│                     │                                    │
│  ┌──────────────────▼──────────────────────────────┐   │
│  │      Classification Engine                      │   │
│  │  ┌──────────────────────────────────────────┐  │   │
│  │  │         LLM Client                       │  │   │
│  │  │  - Prompt Construction                   │  │   │
│  │  │  - API Communication                     │  │   │
│  │  │  - Response Parsing                      │  │   │
│  │  └──────────────────────────────────────────┘  │   │
│  │  - Context Analysis                             │   │
│  │  - Stage Awareness                              │   │
│  └──────────────────┬──────────────────────────────┘   │
│                     │                                    │
│  ┌──────────────────▼──────────────────────────────┐   │
│  │      Response Generator                         │   │
│  └──────────────────┬──────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
              JSON Response
         {status: "...", message: "..."}
                     
                     
┌─────────────────────────────────────────────────────────┐
│                   LLM Service (External)                 │
│              (OpenAI, Anthropic, etc.)                   │
└─────────────────────────────────────────────────────────┘
```

### Component Responsibilities

1. **Input Validation & Parsing**: Validates user text input and parses JSON task context
2. **Classification Engine**: Core logic for determining the appropriate status code using LLM
3. **LLM Client**: Handles communication with LLM API, prompt construction, and response parsing
4. **Response Generator**: Formats the classification result as JSON with status code and message

## Components and Interfaces

### 1. StageManager Agent (Main Component)

The primary agent class that orchestrates all classification components.

**Interface:**
```python
class StageManager:
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the StageManager agent.
        
        Args:
            config: Optional configuration dictionary for classification rules
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

Core classification logic using LLM for intent understanding and context awareness.

**Interface:**
```python
class ClassificationEngine:
    def __init__(self, config: Optional[Dict] = None, llm_client: Optional[LLMClient] = None):
        """
        Initialize with optional configuration and LLM client.
        
        Args:
            config: Optional configuration dictionary
            llm_client: Optional LLM client for classification
        """
        pass
    
    def classify_intent(self, user_input: str, task_context: Optional[Dict] = None) -> str:
        """
        Determine the status code from user input and context using LLM.
        
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
    
    def _build_llm_prompt(self, user_input: str, task_context: Optional[Dict] = None) -> str:
        """
        Build the prompt for LLM classification.
        
        Includes user input, task context, stage information, and classification instructions.
        """
        pass
```

### 3a. LLM Client

Handles communication with the LLM API for classification.

**Interface:**
```python
class LLMClient:
    def __init__(self, api_key: str, model: str = "gpt-4", endpoint: Optional[str] = None, timeout: int = 30):
        """
        Initialize LLM client.
        
        Args:
            api_key: API key for LLM service
            model: Model name to use (e.g., "gpt-4", "claude-3-opus")
            endpoint: Optional custom API endpoint
            timeout: Request timeout in seconds
        """
        pass
    
    def classify(self, prompt: str) -> Dict:
        """
        Send classification request to LLM.
        
        Args:
            prompt: The constructed prompt for classification
            
        Returns:
            Dictionary with 'status' and 'message' keys
            
        Raises:
            LLMConnectionError: If connection to LLM service fails
            LLMTimeoutError: If request times out
            LLMResponseError: If response is invalid or unparseable
        """
        pass
    
    def is_available(self) -> bool:
        """Check if LLM service is available."""
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
    "llm": {
        "api_key": str,              # API key for LLM service
        "model": str,                # Model name (e.g., "gpt-4", "claude-3-opus")
        "endpoint": Optional[str],   # Optional custom API endpoint
        "timeout": int,              # Request timeout in seconds (default: 30)
        "max_retries": int,          # Maximum retry attempts (default: 3)
        "retry_delay": int           # Delay between retries in seconds (default: 1)
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
*For any* valid configuration dictionary with classification rules and LLM settings, the StageManager should load and apply those rules to subsequent classifications.
**Validates: Requirements 6.1, 6.2, 9.1, 9.2**

### Property 10: Stage extraction from input
*For any* user input containing explicit stage indicators (e.g., "at stage 2"), the StageManager should extract the stage information and use it in classification decisions.
**Validates: Requirements 5.1**

### Property 11: Stage boundary awareness
*For any* task context where the current stage is at the beginning or end of the stages array, the StageManager should consider these boundaries when classifying PREVIOUS or NEXT requests respectively.
**Validates: Requirements 5.4, 5.5**

### Property 12: LLM prompt includes user input
*For any* valid user input, the LLM prompt constructed by the ClassificationEngine should contain the user's input text.
**Validates: Requirements 10.1**

### Property 13: LLM prompt includes task context
*For any* classification request with task context, the LLM prompt should include the task name, description, and current stage information.
**Validates: Requirements 10.2, 10.3**

### Property 14: LLM response parsing
*For any* valid LLM response containing a status code, the ClassificationEngine should successfully parse and extract the status code.
**Validates: Requirements 8.3**

### Property 15: LLM unavailability handling
*For any* classification request when the LLM service is unavailable, the StageManager should return an error response without crashing.
**Validates: Requirements 8.4**

### Property 16: LLM timeout handling
*For any* classification request with a configured timeout, if the LLM service exceeds the timeout, the StageManager should handle it gracefully and return an appropriate error response.
**Validates: Requirements 9.3**

### Property 17: LLM retry behavior
*For any* failed LLM request with retry configuration, the StageManager should retry the request according to the configured retry settings before returning an error.
**Validates: Requirements 9.4**

### Property 18: Invalid LLM response handling
*For any* LLM response that is invalid or unparseable, the StageManager should return UNKNOWN status code and log the error without crashing.
**Validates: Requirements 8.5**

### Property 19: Ambiguous input handling
*For any* ambiguous user input, the StageManager should return the most contextually appropriate status code based on task context, or UNKNOWN if no clear match exists.
**Validates: Requirements 7.1, 7.2, 7.3**

### Property 20: LLM classification flow
*For any* valid user input and task context, the ClassificationEngine should send the information to the LLM service and receive a classification response.
**Validates: Requirements 8.1, 8.2**

### Property 21: LLM prompt instructions
*For any* LLM prompt constructed by the ClassificationEngine, the prompt should include clear instructions about all seven status codes and their meanings.
**Validates: Requirements 10.4**

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

### Configuration Errors

- **Invalid Configuration Format**: Logs warning and falls back to default configuration
- **Missing LLM Configuration**: Uses default LLM configuration values

### LLM Service Errors

- **Connection Failure**: Returns `{"status": "ERROR", "message": "Unable to connect to LLM service"}`
- **Timeout**: Returns `{"status": "ERROR", "message": "LLM service request timed out"}`
- **Invalid Response**: Returns `{"status": "UNKNOWN", "message": "Unable to parse LLM response"}` and logs the error
- **API Key Missing**: Returns `{"status": "ERROR", "message": "LLM API key not configured"}`
- **Rate Limit Exceeded**: Implements exponential backoff and retry, returns error if all retries fail

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
4. **Property 9 (Configuration)**: Generate random configuration dictionaries (including LLM settings) and verify they are applied
5. **Property 10-11 (Stage Awareness)**: Generate random stage indicators and task contexts to verify stage extraction and boundary handling
6. **Property 12-13 (LLM Prompts)**: Generate random inputs and contexts to verify LLM prompts include all required information
7. **Property 14-15 (LLM Response Handling)**: Generate various LLM responses (valid, invalid, unavailable) and verify parsing and error handling
8. **Property 16-18 (LLM Error Handling)**: Test timeout handling, retry behavior, and invalid response handling
9. **Property 19 (Ambiguous Input)**: Generate ambiguous inputs with various contexts to verify appropriate classification
10. **Property 20-21 (LLM Integration)**: Verify LLM classification flow and prompt instruction completeness

### Unit Testing

Unit tests will cover specific examples and integration points:

**Core Classification Tests:**
- Test each status code with representative examples (NEXT: "continue", "next"; PREVIOUS: "go back"; EXIT: "quit"; HELP: "help me"; CARE: "I'm worried"; HELLO: "hello"; UNKNOWN: "banana")
- Test ambiguous inputs with different contexts
- Test multi-intent inputs
- Test classification with mocked LLM responses

**LLM Integration Tests:**
- Test successful LLM connection and classification
- Test LLM unavailable during initialization
- Test LLM timeout handling
- Test invalid LLM response parsing
- Test LLM response validation
- Test prompt construction with various contexts
- Test retry logic for failed LLM calls

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
- User input with context → Context-aware classification → Response

### Test Organization

```
tests/
├── unit/
│   ├── test_input_validator.py
│   ├── test_classification_engine.py
│   ├── test_llm_client.py
│   └── test_response_generator.py
├── property/
│   ├── test_input_properties.py
│   ├── test_classification_properties.py
│   ├── test_context_properties.py
│   └── test_llm_properties.py
└── integration/
    └── test_stage_manager_integration.py
```

### LLM Testing Strategy

Since LLM responses are non-deterministic, testing will use:

1. **Mocked LLM Responses**: For unit tests, mock the LLM client to return predictable responses
2. **Response Validation**: Test that the system correctly handles various LLM response formats
3. **Error Simulation**: Mock LLM failures, timeouts, and invalid responses
4. **Prompt Validation**: Test that prompts are correctly constructed with all required information
5. **Integration Tests**: Use real LLM calls sparingly in integration tests with known inputs

## Implementation Notes

### Agent Architecture

The StageManager will be implemented following these architectural principles:

1. **Component-Based Design**: Clear separation between validation, classification, LLM communication, and response generation
2. **Dependency Injection**: Components accept dependencies (like LLM client) through constructors for testability
3. **State Management**: Configuration and connection status tracked through instance variables
4. **Consistent Error Handling**: All components return errors in the same JSON format

### Classification Algorithm

The classification engine will use an LLM-based approach:

1. **Preprocessing**: Validate input and extract task context information
2. **Prompt Construction**: Build a structured prompt that includes:
   - User input text
   - Task context (name, description, current stage)
   - Stage boundary information (first/last stage)
   - Clear instructions about the seven status codes
   - Examples of each status code
3. **LLM Request**: Send the prompt to the LLM service with retry logic
4. **Response Parsing**: Extract the status code from the LLM response
5. **Validation**: Ensure the returned status code is one of the seven valid codes
6. **Fallback**: Return UNKNOWN if response is invalid or unparseable

### LLM Prompt Structure

The prompt will follow this structure:

```
You are a task navigation assistant. Classify the user's intent into one of these status codes:

- NEXT: User wants to proceed to the next stage
- PREVIOUS: User wants to go back to the previous stage  
- EXIT: User wants to quit or leave the task
- HELP: User needs assistance or information
- CARE: User expresses concern, emotion, or needs support
- HELLO: User is greeting or introducing themselves
- UNKNOWN: Intent is unclear or doesn't match other categories

Task Context:
- Task: {task_name}
- Description: {task_description}
- Current Stage: {current_stage} ({stage_description})
- Stage Position: {first/middle/last stage}

User Input: "{user_input}"

Respond with ONLY the status code (one word) followed by a brief explanation.
Format: STATUS_CODE: explanation
```

### LLM Integration

The LLM client will be implemented to support multiple providers:

1. **OpenAI Integration**: Support for GPT-4, GPT-3.5-turbo models
2. **Anthropic Integration**: Support for Claude models
3. **Custom Endpoints**: Allow custom API endpoints for self-hosted models
4. **Retry Logic**: Implement exponential backoff for failed requests
5. **Timeout Handling**: Respect configured timeout values
6. **Response Validation**: Validate LLM responses match expected format

### Performance Considerations

- **Caching**: Cache LLM responses for identical inputs (optional, configurable)
- **Lazy Loading**: Load LLM client only when needed
- **Async Operations**: Use async/await for LLM calls to avoid blocking
- **Input Size Limits**: Limit user input to reasonable size (e.g., 1000 characters)
- **Prompt Optimization**: Keep prompts concise to reduce latency and costs
- **Connection Pooling**: Reuse HTTP connections for LLM API calls

### Security Considerations

- **Input Sanitization**: Sanitize user input to prevent injection attacks
- **JSON Validation**: Validate JSON structure before parsing
- **API Key Protection**: Store LLM API keys securely, never log them
- **Prompt Injection Prevention**: Sanitize user input to prevent prompt injection attacks
- **Rate Limiting**: Implement rate limiting for LLM calls to prevent abuse
- **Logging**: Avoid logging sensitive information (PII, API keys)
- **HTTPS Only**: Enforce HTTPS for all external API calls
