# StageManager

A stage manager classifier agent in Python. StageManager helps users navigate through multi-stage tasks by intelligently classifying their natural language input into actionable status codes.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Basic Classification](#basic-classification)
  - [Task Context](#task-context)
  - [LLM Configuration](#llm-configuration)
  - [Custom Configuration](#custom-configuration)
- [Configuration](#configuration)
- [Data Models](#data-models)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Security](#security)
- [Testing](#testing)
- [Development](#development)
- [Requirements](#requirements)
- [License](#license)

## Overview

The StageManager is a classifier agent that analyzes user text input and classifies it into one of seven status codes to facilitate task navigation:

| Status Code | Description | Example Inputs |
|------------|-------------|----------------|
| **NEXT** | Proceed to the next stage | "continue", "next", "proceed", "forward" |
| **PREVIOUS** | Go back to the previous stage | "back", "previous", "return", "go back" |
| **EXIT** | Exit the task flow | "quit", "exit", "leave", "stop" |
| **HELP** | Request assistance | "help", "assist", "support", "call" |
| **CARE** | Express need for support | "worried", "anxious", "scared", "concerned" |
| **HELLO** | Greeting or introduction | "hello", "hi", "hey", "greetings" |
| **UNKNOWN** | Unclear or ambiguous input | Any input that doesn't match patterns |

## Features

- 🤖 **LLM-Powered Classification**: Uses Large Language Models for intelligent natural language understanding
- ☁️ **AWS Bedrock Support**: Native integration with AWS Bedrock models (Claude, Titan, and more)
- 🎯 **Intent Classification**: Accurately classifies user input into 7 status codes
- 🔄 **Context-Aware**: Uses task context and stage information for intelligent decisions
- 🛡️ **Stage Boundary Protection**: Prevents invalid navigation (e.g., PREVIOUS at first stage)
- 🔧 **Configurable**: Customize classification rules, LLM settings, and patterns
- 🏗️ **Clean Architecture**: Well-structured codebase with clear separation of concerns
- 🌍 **Unicode Support**: Handles special characters and unicode input
- ✅ **Comprehensive Testing**: Unit tests and property-based tests with Hypothesis
- 📝 **Type-Safe**: Full type hints and data validation
- 🔄 **Fallback Support**: Gracefully falls back to pattern-based classification if LLM is unavailable

## Installation

### Basic Installation

```bash
pip install -e .
```

### Development Installation

For development with testing dependencies:

```bash
pip install -e ".[dev]"
```

### From Source

```bash
git clone <repository-url>
cd stage-manager
pip install -e .
```

## Quick Start

### Basic Usage

```python
from stage_manager.stage_manager import StageManager

# Initialize the agent
manager = StageManager()

# Classify user input
result = manager.classify("I want to continue")
print(result)
# Output: {"status": "NEXT", "message": "Moving forward to the next stage."}
```

### Using AWS Bedrock

StageManager has native support for AWS Bedrock, providing access to Claude and other models hosted on AWS:

```python
from stage_manager.stage_manager import StageManager

# Configure with AWS Bedrock
config = {
    "llm": {
        "api_key": "bedrock",  # Use AWS credentials
        "model": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        "region": "us-west-2",
        "timeout": 30
    }
}

# Create StageManager with Bedrock
manager = StageManager(config=config)

# Classify with Bedrock
result = manager.classify("I need help with this task")
print(result)
# Output: {"status": "HELP", "message": "Help is on the way..."}
```

**Supported Bedrock Models:**
- **Anthropic Claude**: `us.anthropic.claude-sonnet-4-5-20250929-v1:0`, `anthropic.claude-v2`, `anthropic.claude-3-sonnet`, `anthropic.claude-3-haiku`
- **Amazon Titan**: `amazon.titan-text-express-v1`, `amazon.titan-text-lite-v1`
- **AI21 Labs**: `ai21.j2-ultra-v1`, `ai21.j2-mid-v1`
- **Cohere**: `cohere.command-text-v14`, `cohere.command-light-text-v14`
- **Meta**: `meta.llama2-13b-chat-v1`, `meta.llama2-70b-chat-v1`

**AWS Credentials:**
- Uses AWS credentials from environment variables, `~/.aws/credentials`, or IAM roles
- Requires `bedrock:InvokeModel` permission
- See [AWS Bedrock Examples](examples/bedrock_usage.py) for detailed usage

**Using Different Bedrock Models:**
```python
# Claude 3.5 Sonnet (recommended)
config = {"llm": {"api_key": "bedrock", "model": "us.anthropic.claude-sonnet-4-5-20250929-v1:0"}}

# Claude 2
config = {"llm": {"api_key": "bedrock", "model": "anthropic.claude-v2"}}

# Amazon Titan
config = {"llm": {"api_key": "bedrock", "model": "amazon.titan-text-express-v1"}}

manager = StageManager(config=config)
```

## Usage

### Basic Classification

The simplest way to use StageManager is to classify user input without any context:

```python
from stage_manager.stage_manager import StageManager

manager = StageManager()

# Test various inputs
inputs = ["next", "go back", "help me", "I'm worried", "hello", "quit"]

for user_input in inputs:
    result = manager.classify(user_input)
    print(f"{user_input} -> {result['status']}: {result['message']}")
```

### Task Context

Provide task context to enable context-aware classification and stage boundary protection:

```python
from stage_manager.stage_manager import StageManager

manager = StageManager()

# Define task context
task_context = {
    "task": "morning_routine",
    "description": "Daily morning routine tasks",
    "status": "in progress",
    "current_stage": "breakfast",
    "stages": [
        {
            "stage": "wake_up",
            "description": "Wake up and get out of bed",
            "timeout": 300
        },
        {
            "stage": "breakfast",
            "description": "Eat a healthy breakfast",
            "timeout": 600
        },
        {
            "stage": "exercise",
            "description": "Do morning exercises",
            "timeout": 900
        }
    ]
}

# Classify with context
result = manager.classify("go back", task_context)
print(result)
# Output: {"status": "PREVIOUS", "message": "Going back to the previous stage."}
```

### LLM Configuration

Enable LLM-powered classification for more intelligent natural language understanding:

```python
from stage_manager.stage_manager import StageManager
import os

# Configure with LLM
config = {
    "llm": {
        "api_key": os.getenv("LLM_API_KEY"),  # Use environment variable for security
        "model": "gpt-4",
        "timeout": 30,
        "max_retries": 3
    }
}

manager = StageManager(config=config)

# LLM can handle more complex and ambiguous natural language
result = manager.classify("Let's move forward with this")
print(result['status'])  # Output: NEXT

result = manager.classify("Can we revisit the previous step?")
print(result['status'])  # Output: PREVIOUS

result = manager.classify("I'm not sure what to do here")
print(result['status'])  # Output: HELP
```

**Supported LLM Providers:**
- OpenAI (GPT-4, GPT-3.5-turbo)
- Anthropic (Claude models)
- Custom/self-hosted models

**LLM Configuration Options:**
- `api_key` (required): API key for the LLM service
- `model` (optional): Model name (default: "gpt-4")
- `endpoint` (optional): Custom API endpoint for self-hosted models
- `timeout` (optional): Request timeout in seconds (default: 30)
- `max_retries` (optional): Maximum retry attempts (default: 3)
- `retry_delay` (optional): Initial retry delay in seconds (default: 1)

**Fallback Behavior:**
If LLM is unavailable or not configured, StageManager automatically falls back to pattern-based classification.

### Custom Configuration

Customize classification rules to match your specific use case:

```python
from stage_manager.stage_manager import StageManager

# Define custom configuration
config = {
    "classification_rules": {
        "NEXT": ["next", "continue", "proceed", "forward", "onward", "advance"],
        "PREVIOUS": ["back", "previous", "return", "rewind", "undo"],
        "EXIT": ["exit", "quit", "leave", "stop", "done", "cancel"],
        "HELP": ["help", "assist", "support", "guide", "info"],
        "CARE": ["worried", "anxious", "scared", "stressed", "overwhelmed"],
        "HELLO": ["hello", "hi", "hey", "greetings", "howdy"]
    }
}

manager = StageManager(config=config)

# Now "onward" will be classified as NEXT
result = manager.classify("onward!")
print(result['status'])  # Output: NEXT
```

## Configuration

### Configuration Format

The configuration is a dictionary with two main sections:

```python
{
    "llm": {
        "api_key": "your-api-key-here",
        "model": "gpt-4",
        "timeout": 30,
        "max_retries": 3
    },
    "classification_rules": {
        "NEXT": ["next", "continue", "proceed", ...],
        "PREVIOUS": ["back", "previous", "return", ...],
        "EXIT": ["exit", "quit", "leave", ...],
        "HELP": ["help", "assist", "support", ...],
        "CARE": ["worried", "anxious", "scared", ...],
        "HELLO": ["hello", "hi", "hey", ...]
    }
}
```

### Configuration Options

#### LLM Configuration

- **api_key** (string, required): API key for the LLM service
  - **Security**: Use environment variables, never hardcode
  - Example: `os.getenv("LLM_API_KEY")`

- **model** (string, optional): Model name to use
  - Default: `"gpt-4"`
  - OpenAI: `"gpt-4"`, `"gpt-3.5-turbo"`
  - Anthropic: `"claude-3-opus"`, `"claude-3-sonnet"`

- **endpoint** (string, optional): Custom API endpoint
  - Default: Auto-detected from model name
  - Use for self-hosted models

- **timeout** (integer, optional): Request timeout in seconds
  - Default: `30`
  - Range: `> 0`

- **max_retries** (integer, optional): Maximum retry attempts
  - Default: `3`
  - Range: `>= 0`

- **retry_delay** (integer, optional): Initial retry delay in seconds
  - Default: `1`
  - Uses exponential backoff

#### Classification Rules

- **Type**: `Dict[str, List[str]]`
- **Description**: Maps status codes to lists of keywords/patterns for pattern-based classification
- **Default**: Built-in patterns for each status code
- **Note**: Used as fallback when LLM is unavailable
- **Example**:
  ```python
  "classification_rules": {
      "NEXT": ["next", "continue", "proceed", "forward"],
      "PREVIOUS": ["back", "previous", "return"]
  }
  ```

#### MCP Server

- **url** (string): URL of the MCP server
  - Default: `"http://localhost:8080"`
  - Example: `"https://mcp.example.com"`

- **timeout** (integer): Timeout in seconds for MCP operations
  - Default: `30`
  - Range: `> 0`

### Loading Configuration from File

```python
import json
from stage_manager.stage_manager import StageManager

# Load from JSON file
with open("config.json", "r") as f:
    config = json.load(f)

manager = StageManager(config=config)
```

Example `config.json`:

```json
{
  "llm": {
    "api_key": "your-api-key-here",
    "model": "gpt-4",
    "timeout": 30,
    "max_retries": 3
  },
  "classification_rules": {
    "NEXT": ["next", "continue", "proceed", "forward"],
    "PREVIOUS": ["back", "previous", "return"],
    "EXIT": ["exit", "quit", "leave", "stop"],
    "HELP": ["help", "assist", "support"],
    "CARE": ["worried", "anxious", "scared"],
    "HELLO": ["hello", "hi", "hey"]
  }
}
```

**Security Note:** For production, load the API key from environment variables:

```python
import os
import json

with open("config.json", "r") as f:
    config = json.load(f)

# Override API key from environment
if "llm" in config:
    config["llm"]["api_key"] = os.getenv("LLM_API_KEY")

manager = StageManager(config=config)
```

## Data Models

StageManager provides type-safe data models for working with tasks and stages:

### Stage

Represents a single stage within a task flow.

```python
from stage_manager.models import Stage

stage = Stage(
    stage="breakfast",
    description="Eat a healthy breakfast",
    timeout=600
)

# Validate the stage
if stage.validate():
    print("Stage is valid")

# Convert to dictionary
stage_dict = stage.to_dict()
```

### TaskContext

Represents a complete task with multiple stages.

```python
from stage_manager.models import TaskContext, Stage

task = TaskContext(
    task="morning_routine",
    description="Daily morning routine",
    status="in progress",
    stages=[
        Stage(stage="wake_up", description="Wake up", timeout=300),
        Stage(stage="breakfast", description="Eat breakfast", timeout=600)
    ]
)

# Validate the task context
if task.validate():
    print("Task context is valid")

# Convert to dictionary
task_dict = task.to_dict()

# Create from dictionary
task = TaskContext.from_dict(task_dict)
```

### ClassificationResponse

Represents the response from classification.

```python
from stage_manager.models import ClassificationResponse

response = ClassificationResponse(
    status="NEXT",
    message="Moving forward to the next stage."
)

# Validate the response
if response.validate():
    print("Response is valid")

# Convert to JSON
json_str = response.to_json()
```

## API Reference

### StageManager

Main classifier agent class.

#### `__init__(config: Optional[Dict] = None)`

Initialize the StageManager agent.

**Parameters:**
- `config` (Dict, optional): Configuration dictionary for classification rules and LLM settings

**Example:**
```python
manager = StageManager()
manager = StageManager(config={"classification_rules": {...}})
```

#### `classify(user_input: str, task_context: Optional[Dict] = None) -> Dict`

Classify user input and return status code with message.

**Parameters:**
- `user_input` (str): User's text input
- `task_context` (Dict, optional): Task context with stages

**Returns:**
- `Dict`: Dictionary with 'status' and 'message' keys

**Raises:**
- Returns error response (not exception) for invalid input

**Example:**
```python
result = manager.classify("continue")
result = manager.classify("next", task_context)
```

### InputValidator

Static methods for input validation.

#### `validate_user_input(user_input: str) -> bool`

Validate user text input is not empty or whitespace-only.

#### `validate_task_context(task_context: Dict) -> bool`

Validate task context has required fields.

#### `parse_task_context(task_json: str) -> Optional[Dict]`

Parse JSON string to task context dictionary.

### ClassificationEngine

Core classification logic.

#### `classify_intent(user_input: str, task_context: Optional[Dict] = None) -> str`

Determine the status code from user input and context.

#### `extract_stage_info(user_input: str, task_context: Optional[Dict] = None) -> Optional[str]`

Extract current stage information from input or context.

#### `is_at_first_stage(task_context: Dict, current_stage: str) -> bool`

Check if current stage is the first stage.

#### `is_at_last_stage(task_context: Dict, current_stage: str) -> bool`

Check if current stage is the last stage.

### ResponseGenerator

Generate formatted responses.

#### `generate_response(status_code: str, context: Optional[Dict] = None) -> Dict`

Generate JSON response with status code and message.

## Examples

The `examples/` directory contains comprehensive examples:

### Basic Usage

```bash
python examples/basic_usage.py
```

Demonstrates:
- Basic classification
- Classification with task context
- Custom configuration
- LLM integration
- Error handling
- Stage boundary awareness

### Advanced Usage

```bash
python examples/advanced_usage.py
```

Demonstrates:
- Building a task flow system
- Configuration management
- Working with data models
- Error recovery patterns
- Unicode handling

### AWS Bedrock Usage

```bash
python examples/bedrock_usage.py
```

Demonstrates:
- Using AWS Bedrock with configuration
- Bedrock configuration options
- Different Bedrock models (Claude 3.5, Titan, etc.)
- AWS credentials management
- Error handling with Bedrock

## Security

StageManager follows security best practices for handling sensitive data and API keys.

### API Key Security

**Never hardcode API keys in your source code.** Always use environment variables or secret management services:

```python
import os

# ✅ Good: Load from environment
config = {
    "llm": {
        "api_key": os.getenv("LLM_API_KEY"),
        "model": "gpt-4"
    }
}

# ❌ Bad: Hardcoded API key
# config = {"llm": {"api_key": "sk-1234567890abcdef"}}
```

### Best Practices

1. **Use Environment Variables**: Store API keys in environment variables
2. **Use Secret Management**: For production, use AWS Secrets Manager, Azure Key Vault, or HashiCorp Vault
3. **Rotate Keys Regularly**: Rotate API keys every 90 days minimum
4. **Use IAM Roles**: For AWS deployments, use IAM roles instead of access keys
5. **Enable HTTPS**: Always use HTTPS for external connections
6. **Sanitize Input**: Validate and sanitize user input to prevent injection attacks
7. **Redact Sensitive Data**: Never log API keys or sensitive information
8. **Monitor Usage**: Set up monitoring and alerts for unusual activity

### AWS Bedrock Security

When using AWS Bedrock:

- Use IAM roles with least privilege (recommended)
- Enable CloudTrail logging for audit trails
- Use VPC endpoints for private connectivity
- Implement resource-based policies

**Required IAM Permissions:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "*"
    }
  ]
}
```

### Additional Resources

For comprehensive security guidance, see:
- [Security Best Practices Guide](docs/SECURITY.md) - Detailed security documentation
- [Configuration Guide](docs/CONFIGURATION.md) - Secure configuration practices
- [AWS Bedrock Examples](examples/bedrock_usage.py) - Secure AWS integration

## Testing

### Run All Tests

```bash
pytest
```

### Run Unit Tests Only

```bash
pytest tests/unit/
```

### Run Property-Based Tests Only

```bash
pytest tests/property/
```

### Run Integration Tests Only

```bash
pytest tests/integration/
```

### Run with Coverage

```bash
pytest --cov=stage_manager --cov-report=html
```

### Test Structure

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_classification_engine.py
│   ├── test_models.py
│   └── ...
├── property/                # Property-based tests with Hypothesis
│   └── test_response_properties.py
└── integration/             # End-to-end integration tests
    └── test_care_flow.py
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd stage-manager

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Code Style

The project follows PEP 8 style guidelines. All code includes:
- Type hints for function parameters and return values
- Comprehensive docstrings
- Logging for debugging and monitoring
- Error handling with graceful fallbacks

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Requirements

### Runtime Requirements

- Python >= 3.8
- hypothesis >= 6.0.0

### Development Requirements

- pytest >= 7.0.0
- pytest-asyncio >= 0.21.0

### Optional Requirements

- boto3 (for AWS Bedrock support)
- OpenAI/Anthropic API keys (for LLM-powered classification)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or contributions, please open an issue on the project repository.

## Acknowledgments

- Property-based testing powered by Hypothesis
- AWS Bedrock integration for scalable LLM access
- Follows EARS (Easy Approach to Requirements Syntax) specification patterns
