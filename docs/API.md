# StageManager API Documentation

This document provides detailed API documentation for all public classes and methods in the StageManager library.

## Table of Contents

- [StageManager](#stagemanager)
- [InputValidator](#inputvalidator)
- [ClassificationEngine](#classificationengine)
- [ResponseGenerator](#responsegenerator)
- [MCPClient](#mcpclient)
- [Data Models](#data-models)
  - [Stage](#stage)
  - [TaskContext](#taskcontext)
  - [ClassificationResponse](#classificationresponse)

---

## StageManager

Main classifier agent class for task stage navigation.

### Class: `StageManager`

```python
from stage_manager.stage_manager import StageManager
```

#### Constructor

```python
def __init__(self, config: Optional[Dict] = None, mcp_client: Optional[MCPClient] = None)
```

Initialize the StageManager agent.

**Parameters:**
- `config` (Dict, optional): Configuration dictionary containing:
  - `classification_rules` (Dict[str, List[str]]): Custom classification patterns
  - `mcp_server` (Dict): MCP server configuration with `url` and `timeout`
- `mcp_client` (MCPClient, optional): Custom MCP client instance for testing or custom implementations

**Example:**
```python
# Basic initialization
manager = StageManager()

# With custom configuration
config = {
    "classification_rules": {
        "NEXT": ["next", "continue", "proceed"],
        "PREVIOUS": ["back", "previous"]
    },
    "mcp_server": {
        "url": "http://localhost:8080",
        "timeout": 30
    }
}
manager = StageManager(config=config)

# With custom MCP client
from stage_manager.mcp_client import MCPClient
mcp = MCPClient(server_url="http://custom-server:8080")
manager = StageManager(mcp_client=mcp)
```

#### Methods

##### `classify(user_input: str, task_context: Optional[Dict] = None) -> Dict`

Classify user input and return status code with message.

**Parameters:**
- `user_input` (str): User's text input to classify
- `task_context` (Dict, optional): Task context dictionary with structure:
  ```python
  {
      "task": str,              # Task name
      "description": str,       # Task description
      "status": str,           # Task status
      "current_stage": str,    # Current stage (optional)
      "stages": [              # List of stages
          {
              "stage": str,
              "description": str,
              "timeout": int
          }
      ]
  }
  ```

**Returns:**
- `Dict`: Response dictionary with structure:
  ```python
  {
      "status": str,    # One of: NEXT, PREVIOUS, EXIT, HELP, CARE, HELLO, UNKNOWN, ERROR
      "message": str    # Contextual message
  }
  ```

**Behavior:**
- Validates user input (rejects empty or whitespace-only)
- Validates task context if provided
- Classifies intent based on patterns and context
- For CARE status: attempts to notify caregiver via MCP
- Returns error response (not exception) for invalid input

**Example:**
```python
# Basic classification
result = manager.classify("I want to continue")
# Returns: {"status": "NEXT", "message": "Moving forward to the next stage."}

# With task context
task_context = {
    "task": "onboarding",
    "description": "User onboarding",
    "status": "in progress",
    "current_stage": "profile",
    "stages": [
        {"stage": "welcome", "description": "Welcome", "timeout": 60},
        {"stage": "profile", "description": "Create profile", "timeout": 300}
    ]
}
result = manager.classify("go back", task_context)
# Returns: {"status": "PREVIOUS", "message": "Going back to the previous stage."}

# Error handling
result = manager.classify("")
# Returns: {"status": "ERROR", "message": "Input cannot be empty or whitespace-only"}
```

---

## InputValidator

Static utility class for validating user input and task context.

### Class: `InputValidator`

```python
from stage_manager.input_validator import InputValidator
```

#### Static Methods

##### `validate_user_input(user_input: str) -> bool`

Validate user text input is not empty or whitespace-only.

**Parameters:**
- `user_input` (str): User's text input

**Returns:**
- `bool`: True if valid, False otherwise

**Validation Rules:**
- Must not be None
- Must be a string
- Must not be empty
- Must not contain only whitespace

**Example:**
```python
InputValidator.validate_user_input("hello")  # True
InputValidator.validate_user_input("")       # False
InputValidator.validate_user_input("   ")    # False
InputValidator.validate_user_input(None)     # False
```

##### `validate_task_context(task_context: Dict[str, Any]) -> bool`

Validate task context has required fields and correct structure.

**Parameters:**
- `task_context` (Dict): Task context dictionary

**Returns:**
- `bool`: True if valid, False otherwise

**Validation Rules:**
- Must not be None
- Must be a dictionary
- Must contain required fields: `task`, `description`, `status`, `stages`
- `stages` must be a list
- Each stage must be a dictionary with fields: `stage`, `description`, `timeout`
- `timeout` must be a non-negative number

**Example:**
```python
valid_context = {
    "task": "test",
    "description": "Test task",
    "status": "active",
    "stages": [
        {"stage": "step1", "description": "First step", "timeout": 300}
    ]
}
InputValidator.validate_task_context(valid_context)  # True

invalid_context = {"task": "test"}  # Missing fields
InputValidator.validate_task_context(invalid_context)  # False
```

##### `parse_task_context(task_json: str) -> Optional[Dict[str, Any]]`

Parse JSON string to task context dictionary.

**Parameters:**
- `task_json` (str): JSON string representation of task context

**Returns:**
- `Dict`: Parsed dictionary if successful
- `None`: If input is invalid

**Raises:**
- `json.JSONDecodeError`: If JSON is malformed

**Example:**
```python
json_str = '{"task": "test", "description": "desc", "status": "active", "stages": []}'
context = InputValidator.parse_task_context(json_str)
# Returns: {"task": "test", "description": "desc", "status": "active", "stages": []}

InputValidator.parse_task_context("")  # Returns: None
InputValidator.parse_task_context("invalid json")  # Raises: JSONDecodeError
```

---

## ClassificationEngine

Core classification logic with pattern matching and context awareness.

### Class: `ClassificationEngine`

```python
from stage_manager.classification_engine import ClassificationEngine
```

#### Constructor

```python
def __init__(self, config: Optional[Dict] = None)
```

Initialize with optional classification rules configuration.

**Parameters:**
- `config` (Dict, optional): Configuration with `classification_rules` key

**Example:**
```python
engine = ClassificationEngine()

# With custom rules
config = {
    "classification_rules": {
        "NEXT": ["next", "continue", "proceed"],
        "PREVIOUS": ["back", "previous"]
    }
}
engine = ClassificationEngine(config=config)
```

#### Methods

##### `classify_intent(user_input: str, task_context: Optional[Dict] = None) -> str`

Determine the status code from user input and context.

**Parameters:**
- `user_input` (str): User's text input
- `task_context` (Dict, optional): Task context with stages

**Returns:**
- `str`: One of: `NEXT`, `PREVIOUS`, `EXIT`, `HELP`, `CARE`, `HELLO`, `UNKNOWN`

**Behavior:**
- Normalizes input (lowercase, strip)
- Extracts stage information
- Matches against classification patterns
- Applies stage boundary logic (prevents PREVIOUS at first stage, NEXT at last stage)
- Returns UNKNOWN if no pattern matches

**Example:**
```python
engine = ClassificationEngine()

engine.classify_intent("continue")  # Returns: "NEXT"
engine.classify_intent("go back")   # Returns: "PREVIOUS"
engine.classify_intent("banana")    # Returns: "UNKNOWN"
```

##### `extract_stage_info(user_input: str, task_context: Optional[Dict] = None) -> Optional[str]`

Extract current stage information from input or context.

**Parameters:**
- `user_input` (str): User's text input
- `task_context` (Dict, optional): Task context

**Returns:**
- `str`: Stage name if found
- `None`: If no stage information available

**Behavior:**
- First tries to extract from user input (patterns like "at stage X" or "stage X")
- Falls back to `current_stage` field in task context
- Returns None if no stage information found

**Example:**
```python
engine = ClassificationEngine()

# From user input
engine.extract_stage_info("I'm at stage breakfast")  # Returns: "breakfast"

# From context
context = {"current_stage": "profile"}
engine.extract_stage_info("continue", context)  # Returns: "profile"

engine.extract_stage_info("hello")  # Returns: None
```

##### `is_at_first_stage(task_context: Dict, current_stage: str) -> bool`

Check if current stage is the first stage.

**Parameters:**
- `task_context` (Dict): Task context with stages
- `current_stage` (str): Current stage name

**Returns:**
- `bool`: True if at first stage, False otherwise

**Example:**
```python
engine = ClassificationEngine()

context = {
    "stages": [
        {"stage": "step1", "description": "First", "timeout": 300},
        {"stage": "step2", "description": "Second", "timeout": 300}
    ]
}

engine.is_at_first_stage(context, "step1")  # True
engine.is_at_first_stage(context, "step2")  # False
```

##### `is_at_last_stage(task_context: Dict, current_stage: str) -> bool`

Check if current stage is the last stage.

**Parameters:**
- `task_context` (Dict): Task context with stages
- `current_stage` (str): Current stage name

**Returns:**
- `bool`: True if at last stage, False otherwise

**Example:**
```python
engine = ClassificationEngine()

context = {
    "stages": [
        {"stage": "step1", "description": "First", "timeout": 300},
        {"stage": "step2", "description": "Second", "timeout": 300}
    ]
}

engine.is_at_last_stage(context, "step1")  # False
engine.is_at_last_stage(context, "step2")  # True
```

---

## ResponseGenerator

Generates JSON responses with status codes and contextual messages.

### Class: `ResponseGenerator`

```python
from stage_manager.response_generator import ResponseGenerator
```

#### Static Methods

##### `generate_response(status_code: str, context: Optional[Dict] = None) -> Dict`

Generate JSON response with status code and message.

**Parameters:**
- `status_code` (str): One of the status codes (NEXT, PREVIOUS, EXIT, HELP, CARE, HELLO, UNKNOWN, ERROR)
- `context` (Dict, optional): Context for customizing message:
  - For CARE: `{"mcp_failed": bool}` - indicates MCP call failure
  - For ERROR: `{"error_message": str}` - custom error message

**Returns:**
- `Dict`: Response with `status` and `message` keys

**Default Messages:**
- NEXT: "Moving forward to the next stage."
- PREVIOUS: "Going back to the previous stage."
- EXIT: "Exiting the task flow."
- HELP: "Help is on the way. What do you need assistance with?"
- CARE: "I understand you need support. A caregiver has been notified."
- HELLO: "Hello! How can I help you today?"
- UNKNOWN: "I'm not sure what you mean. Could you rephrase that?"
- ERROR: "An error occurred while processing your request."

**Example:**
```python
ResponseGenerator.generate_response("NEXT")
# Returns: {"status": "NEXT", "message": "Moving forward to the next stage."}

ResponseGenerator.generate_response("CARE", {"mcp_failed": True})
# Returns: {"status": "CARE", "message": "I understand you need support, but I couldn't reach the caregiver service."}

ResponseGenerator.generate_response("ERROR", {"error_message": "Invalid input"})
# Returns: {"status": "ERROR", "message": "Invalid input"}
```

---

## MCPClient

Client for communicating with MCP (Model Context Protocol) server.

### Class: `MCPClient`

```python
from stage_manager.mcp_client import MCPClient
```

#### Constructor

```python
def __init__(self, server_url: str, timeout: int = 30)
```

Initialize MCP client with server URL.

**Parameters:**
- `server_url` (str): URL of the MCP server
- `timeout` (int, optional): Timeout in seconds for MCP operations (default: 30)

**Raises:**
- `ValueError`: If server_url is invalid

**Example:**
```python
client = MCPClient(server_url="http://localhost:8080")
client = MCPClient(server_url="https://mcp.example.com", timeout=60)
```

#### Methods

##### `connect() -> bool`

Establish connection to MCP server.

**Returns:**
- `bool`: True if connection successful, False otherwise

**Behavior:**
- Validates server URL
- Attempts to establish connection
- Handles connection errors gracefully
- Sets internal connection state

**Example:**
```python
client = MCPClient(server_url="http://localhost:8080")
if client.connect():
    print("Connected successfully")
else:
    print("Connection failed")
```

##### `call_caregiver(user_input: str, task_context: Optional[Dict] = None) -> bool`

Call caregiver service through MCP server.

**Parameters:**
- `user_input` (str): User's text input that triggered CARE status
- `task_context` (Dict, optional): Task context for additional information

**Returns:**
- `bool`: True if caregiver call successful, False otherwise

**Behavior:**
- Validates connection state
- Validates input parameters
- Sends request to MCP server
- Handles timeouts and errors gracefully

**Example:**
```python
client = MCPClient(server_url="http://localhost:8080")
client.connect()

success = client.call_caregiver("I'm feeling worried")
if success:
    print("Caregiver notified")
else:
    print("Failed to notify caregiver")
```

##### `is_connected() -> bool`

Check if connection to MCP server is active.

**Returns:**
- `bool`: True if connected, False otherwise

**Example:**
```python
client = MCPClient(server_url="http://localhost:8080")
print(client.is_connected())  # False

client.connect()
print(client.is_connected())  # True
```

##### `disconnect() -> None`

Disconnect from MCP server and clean up resources.

**Example:**
```python
client = MCPClient(server_url="http://localhost:8080")
client.connect()
# ... use client ...
client.disconnect()
```

---

## Data Models

### Stage

Represents a stage within a task flow.

```python
from stage_manager.models import Stage
```

#### Attributes

- `stage` (str): Stage name/identifier
- `description` (str): Stage description
- `timeout` (int): Timeout in seconds for the stage

#### Methods

##### `validate() -> bool`

Validate the stage data.

**Returns:**
- `bool`: True if valid, False otherwise

**Validation Rules:**
- `stage` must be a non-empty string
- `description` must be a string
- `timeout` must be a non-negative number

##### `to_dict() -> Dict[str, Any]`

Convert stage to dictionary.

**Returns:**
- `Dict`: Dictionary representation

**Example:**
```python
stage = Stage(stage="breakfast", description="Eat breakfast", timeout=600)

if stage.validate():
    stage_dict = stage.to_dict()
    # Returns: {"stage": "breakfast", "description": "Eat breakfast", "timeout": 600}
```

---

### TaskContext

Represents the context of a task with multiple stages.

```python
from stage_manager.models import TaskContext, Stage
```

#### Attributes

- `task` (str): Task name/identifier
- `description` (str): Task description
- `status` (str): Task status (e.g., "not started", "in progress", "completed")
- `stages` (List[Stage]): List of Stage objects

#### Methods

##### `validate() -> bool`

Validate the task context data.

**Returns:**
- `bool`: True if valid, False otherwise

**Validation Rules:**
- `task` must be a non-empty string
- `description` must be a string
- `status` must be a non-empty string
- `stages` must be a list
- Each stage must be a valid Stage object

##### `to_dict() -> Dict[str, Any]`

Convert task context to dictionary.

**Returns:**
- `Dict`: Dictionary representation

##### `from_dict(data: Dict[str, Any]) -> Optional[TaskContext]`

Create TaskContext from dictionary (class method).

**Parameters:**
- `data` (Dict): Dictionary with task context data

**Returns:**
- `TaskContext`: New instance if successful
- `None`: If data is invalid

**Example:**
```python
# Create task context
task = TaskContext(
    task="morning_routine",
    description="Daily routine",
    status="in progress",
    stages=[
        Stage(stage="wake_up", description="Wake up", timeout=300),
        Stage(stage="breakfast", description="Eat breakfast", timeout=600)
    ]
)

# Validate
if task.validate():
    # Convert to dict
    task_dict = task.to_dict()
    
    # Recreate from dict
    task2 = TaskContext.from_dict(task_dict)
```

---

### ClassificationResponse

Represents the response from classification.

```python
from stage_manager.models import ClassificationResponse
```

#### Attributes

- `status` (str): Status code (NEXT, PREVIOUS, EXIT, HELP, CARE, HELLO, UNKNOWN, ERROR)
- `message` (str): Free text message providing context or explanation

#### Methods

##### `validate() -> bool`

Validate the classification response.

**Returns:**
- `bool`: True if valid, False otherwise

**Validation Rules:**
- `status` must be one of the valid status codes
- `message` must be a non-empty string

##### `to_dict() -> Dict[str, str]`

Convert response to dictionary.

**Returns:**
- `Dict`: Dictionary with `status` and `message` keys

##### `to_json() -> str`

Serialize response to JSON string.

**Returns:**
- `str`: JSON string representation

##### `from_dict(data: Dict[str, str]) -> Optional[ClassificationResponse]`

Create ClassificationResponse from dictionary (class method).

**Parameters:**
- `data` (Dict): Dictionary with `status` and `message`

**Returns:**
- `ClassificationResponse`: New instance if successful
- `None`: If data is invalid

**Example:**
```python
# Create response
response = ClassificationResponse(
    status="NEXT",
    message="Moving forward to the next stage."
)

# Validate
if response.validate():
    # Convert to dict
    response_dict = response.to_dict()
    
    # Convert to JSON
    json_str = response.to_json()
    
    # Recreate from dict
    response2 = ClassificationResponse.from_dict(response_dict)
```

---

## Error Handling

All methods handle errors gracefully:

- **Input Validation Errors**: Return error responses instead of raising exceptions
- **MCP Errors**: Log warnings and continue operation
- **Configuration Errors**: Fall back to default configuration
- **JSON Parsing Errors**: Raise `JSONDecodeError` with details

## Logging

All components use Python's `logging` module:

```python
import logging

# Configure logging level
logging.basicConfig(level=logging.INFO)

# Or for debugging
logging.basicConfig(level=logging.DEBUG)
```

Log levels:
- **INFO**: Normal operations, classification results
- **WARNING**: Validation failures, MCP unavailable
- **ERROR**: Exceptions, critical failures
- **DEBUG**: Detailed information for debugging
