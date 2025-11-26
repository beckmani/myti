# StageManager Configuration Guide

This guide explains how to configure the StageManager agent to customize its behavior for your specific use case.

## Table of Contents

- [Overview](#overview)
- [Configuration Structure](#configuration-structure)
- [LLM Configuration](#llm-configuration)
- [Classification Rules](#classification-rules)
- [MCP Server Configuration](#mcp-server-configuration)
- [Loading Configuration](#loading-configuration)
- [Configuration Examples](#configuration-examples)
- [Best Practices](#best-practices)

## Overview

StageManager can be configured in three main areas:

1. **LLM Configuration**: Configure Large Language Model integration for intelligent classification
2. **Classification Rules**: Customize the keywords and patterns used for pattern-based classification
3. **MCP Server**: Configure the Model Context Protocol server for caregiver notifications

Configuration is optional - StageManager works out of the box with sensible defaults.

## Configuration Structure

The configuration is a Python dictionary with the following structure:

```python
{
    "llm": {
        "api_key": "...",
        "model": "...",
        "endpoint": "...",
        "timeout": ...,
        "max_retries": ...,
        "retry_delay": ...
    },
    "classification_rules": {
        "NEXT": [...],
        "PREVIOUS": [...],
        "EXIT": [...],
        "HELP": [...],
        "CARE": [...],
        "HELLO": [...]
    },
    "mcp_server": {
        "url": "...",
        "timeout": ...
    }
}
```

## LLM Configuration

Configure Large Language Model integration for intelligent natural language understanding and classification.

### Structure

```python
"llm": {
    "api_key": "your-api-key-here",
    "model": "gpt-4",
    "endpoint": "https://api.openai.com/v1/chat/completions",
    "timeout": 30,
    "max_retries": 3,
    "retry_delay": 1
}
```

### Parameters

#### `api_key` (string, required)

API key for the LLM service.

- **Required**: Yes
- **Security**: Never commit API keys to version control. Use environment variables or secure key management.
- **Example**: `"sk-..."`

#### `model` (string, optional)

Model name to use for classification.

- **Default**: `"gpt-4"`
- **OpenAI Models**: `"gpt-4"`, `"gpt-4-turbo"`, `"gpt-3.5-turbo"`
- **Anthropic Models**: `"claude-3-opus"`, `"claude-3-sonnet"`, `"claude-3-haiku"`
- **AWS Bedrock Models**: `"anthropic.claude-v2"`, `"amazon.titan-text-express-v1"`, etc.
- **Custom Models**: Any model name supported by your endpoint

#### `region` (string, optional)

AWS region for Bedrock service (only used when provider is Bedrock).

- **Default**: `"us-east-1"`
- **Common Regions**: `"us-east-1"`, `"us-west-2"`, `"eu-west-1"`, `"ap-southeast-1"`
- **Purpose**: Specifies which AWS region to use for Bedrock API calls

#### `endpoint` (string, optional)

Custom API endpoint URL.

- **Default**: Determined by model name (OpenAI or Anthropic)
- **Use Cases**: Self-hosted models, custom LLM providers
- **Format**: Full URL including protocol
- **Examples**:
  - `"https://api.openai.com/v1/chat/completions"`
  - `"https://api.anthropic.com/v1/messages"`
  - `"http://localhost:8000/v1/completions"` (local model)

#### `timeout` (integer, optional)

Request timeout in seconds.

- **Default**: `30`
- **Range**: > 0
- **Recommended**: 10-60 seconds
- **Purpose**: Prevents hanging if LLM service is slow

#### `max_retries` (integer, optional)

Maximum number of retry attempts for failed requests.

- **Default**: `3`
- **Range**: >= 0
- **Purpose**: Improves reliability by retrying transient failures

#### `retry_delay` (integer, optional)

Initial delay between retries in seconds (uses exponential backoff).

- **Default**: `1`
- **Range**: > 0
- **Behavior**: Delay doubles with each retry (1s, 2s, 4s, etc.)

### Example: OpenAI Configuration

```python
config = {
    "llm": {
        "api_key": "sk-...",
        "model": "gpt-4",
        "timeout": 30,
        "max_retries": 3
    }
}
```

### Example: Anthropic Configuration

```python
config = {
    "llm": {
        "api_key": "sk-ant-...",
        "model": "claude-3-opus",
        "endpoint": "https://api.anthropic.com/v1/messages",
        "timeout": 45
    }
}
```

### Example: AWS Bedrock Configuration

```python
config = {
    "llm": {
        "api_key": "bedrock",  # Use "bedrock" to use default AWS credentials
        "model": "anthropic.claude-v2",  # Bedrock model ID
        "region": "us-east-1",  # AWS region
        "timeout": 30,
        "max_retries": 3
    }
}
```

**Supported Bedrock Models:**
- Anthropic Claude: `anthropic.claude-v2`, `anthropic.claude-v2:1`, `anthropic.claude-3-sonnet`, `anthropic.claude-3-haiku`
- Amazon Titan: `amazon.titan-text-express-v1`, `amazon.titan-text-lite-v1`
- AI21 Labs: `ai21.j2-ultra-v1`, `ai21.j2-mid-v1`
- Cohere: `cohere.command-text-v14`, `cohere.command-light-text-v14`
- Meta: `meta.llama2-13b-chat-v1`, `meta.llama2-70b-chat-v1`

**AWS Credentials:**
- Set `api_key` to `"bedrock"` to use default AWS credentials from environment/config
- Or provide AWS access key (requires separate secret key configuration)
- Ensure your AWS credentials have `bedrock:InvokeModel` permission

### Example: Custom/Self-Hosted Model

```python
config = {
    "llm": {
        "api_key": "custom-key",
        "model": "llama-2-70b",
        "endpoint": "http://localhost:8000/v1/completions",
        "timeout": 60,
        "max_retries": 2
    }
}
```

### LLM Behavior

- **No Configuration**: If no LLM configuration is provided, StageManager uses pattern-based classification
- **Missing API Key**: If API key is missing, LLM integration is skipped with a warning
- **Connection Failure**: Falls back to pattern-based classification
- **Invalid Response**: Returns UNKNOWN status and logs the error
- **Retry Logic**: Automatically retries failed requests with exponential backoff

### Security Best Practices

1. **Never hardcode API keys** in your source code
2. **Use environment variables** for API keys:

```python
import os

config = {
    "llm": {
        "api_key": os.getenv("LLM_API_KEY"),
        "model": "gpt-4"
    }
}
```

3. **Use secure key management** services (AWS Secrets Manager, Azure Key Vault, etc.)
4. **Rotate API keys** regularly
5. **Monitor API usage** to detect unauthorized access

## Classification Rules

Classification rules define the keywords and patterns that map user input to status codes.

### Structure

```python
"classification_rules": {
    "STATUS_CODE": ["pattern1", "pattern2", "pattern3", ...]
}
```

### Status Codes

The following status codes can be configured:

| Status Code | Purpose | Default Patterns |
|------------|---------|------------------|
| **NEXT** | Move to next stage | "next", "continue", "proceed", "forward", "go on" |
| **PREVIOUS** | Go to previous stage | "back", "previous", "return", "go back" |
| **EXIT** | Exit the task | "exit", "quit", "leave", "stop", "end" |
| **HELP** | Request assistance | "help", "assist", "support", "call" |
| **CARE** | Need support (triggers caregiver) | "worried", "anxious", "scared", "concerned", "upset" |
| **HELLO** | Greeting | "hello", "hi", "hey", "greetings" |

### Pattern Matching

- Patterns are case-insensitive
- Patterns are matched as substrings (e.g., "next" matches "next please")
- First matching pattern wins
- If no pattern matches, status is UNKNOWN

### Example: Custom Classification Rules

```python
config = {
    "classification_rules": {
        "NEXT": [
            "next",
            "continue",
            "proceed",
            "forward",
            "onward",
            "advance",
            "let's go",
            "move on"
        ],
        "PREVIOUS": [
            "back",
            "previous",
            "return",
            "go back",
            "rewind",
            "undo",
            "step back"
        ],
        "EXIT": [
            "exit",
            "quit",
            "leave",
            "stop",
            "end",
            "cancel",
            "done",
            "finish"
        ],
        "HELP": [
            "help",
            "assist",
            "support",
            "call",
            "guide",
            "info",
            "explain",
            "what do i do"
        ],
        "CARE": [
            "worried",
            "anxious",
            "scared",
            "concerned",
            "upset",
            "stressed",
            "overwhelmed",
            "afraid",
            "nervous"
        ],
        "HELLO": [
            "hello",
            "hi",
            "hey",
            "greetings",
            "howdy",
            "good morning",
            "good afternoon",
            "good evening"
        ]
    }
}
```

### Localization Example

You can add patterns in different languages:

```python
config = {
    "classification_rules": {
        "NEXT": [
            # English
            "next", "continue", "proceed",
            # Spanish
            "siguiente", "continuar",
            # French
            "suivant", "continuer",
            # German
            "weiter", "fortfahren"
        ],
        "HELP": [
            # English
            "help", "assist",
            # Spanish
            "ayuda", "asistir",
            # French
            "aide", "aider",
            # German
            "hilfe", "helfen"
        ]
    }
}
```

### Domain-Specific Patterns

Customize patterns for your specific domain:

```python
# Healthcare domain
config = {
    "classification_rules": {
        "NEXT": ["next step", "ready for next", "proceed with treatment"],
        "CARE": ["pain", "discomfort", "feeling unwell", "need nurse"],
        "HELP": ["question", "don't understand", "need clarification"]
    }
}

# Education domain
config = {
    "classification_rules": {
        "NEXT": ["next lesson", "continue learning", "move forward"],
        "PREVIOUS": ["review previous", "go back to lesson"],
        "HELP": ["need help", "don't understand", "explain again"]
    }
}

# Customer service domain
config = {
    "classification_rules": {
        "NEXT": ["next step", "what's next", "continue"],
        "EXIT": ["cancel order", "stop process", "nevermind"],
        "HELP": ["speak to agent", "need help", "talk to human"]
    }
}
```

## MCP Server Configuration

Configure the Model Context Protocol server for caregiver notifications when CARE status is detected.

### Structure

```python
"mcp_server": {
    "url": "http://localhost:8080",
    "timeout": 30
}
```

### Parameters

#### `url` (string, required)

The URL of the MCP server.

- **Format**: Full URL including protocol
- **Examples**:
  - `"http://localhost:8080"` - Local development
  - `"https://mcp.example.com"` - Production server
  - `"http://192.168.1.100:8080"` - Network server

#### `timeout` (integer, optional)

Timeout in seconds for MCP operations.

- **Default**: 30
- **Range**: > 0
- **Recommended**: 10-60 seconds
- **Purpose**: Prevents hanging if MCP server is slow or unresponsive

### Example: MCP Configuration

```python
config = {
    "mcp_server": {
        "url": "https://mcp.example.com",
        "timeout": 45
    }
}
```

### MCP Behavior

- **Connection Failure**: If MCP server is unavailable during initialization, StageManager logs a warning and continues without MCP integration
- **Call Failure**: If caregiver call fails, CARE status is still returned with a message indicating the failure
- **Graceful Degradation**: StageManager always works, even if MCP is unavailable

## Loading Configuration

### Method 1: Direct Dictionary

```python
from stage_manager.stage_manager import StageManager

config = {
    "classification_rules": {
        "NEXT": ["next", "continue"],
        "PREVIOUS": ["back", "previous"]
    }
}

manager = StageManager(config=config)
```

### Method 2: From JSON File

```python
import json
from stage_manager.stage_manager import StageManager

# Load configuration from file
with open("config.json", "r") as f:
    config = json.load(f)

manager = StageManager(config=config)
```

Example `config.json`:

```json
{
  "classification_rules": {
    "NEXT": ["next", "continue", "proceed"],
    "PREVIOUS": ["back", "previous", "return"],
    "EXIT": ["exit", "quit", "leave"],
    "HELP": ["help", "assist", "support"],
    "CARE": ["worried", "anxious", "scared"],
    "HELLO": ["hello", "hi", "hey"]
  },
  "mcp_server": {
    "url": "http://localhost:8080",
    "timeout": 30
  }
}
```

### Method 3: From Environment Variables

```python
import os
import json
from stage_manager.stage_manager import StageManager

# Load MCP URL from environment
mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:8080")
mcp_timeout = int(os.getenv("MCP_TIMEOUT", "30"))

config = {
    "mcp_server": {
        "url": mcp_url,
        "timeout": mcp_timeout
    }
}

manager = StageManager(config=config)
```

### Method 4: From YAML File

```python
import yaml
from stage_manager.stage_manager import StageManager

# Load configuration from YAML
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

manager = StageManager(config=config)
```

Example `config.yaml`:

```yaml
classification_rules:
  NEXT:
    - next
    - continue
    - proceed
  PREVIOUS:
    - back
    - previous
    - return
  EXIT:
    - exit
    - quit
    - leave
  HELP:
    - help
    - assist
    - support
  CARE:
    - worried
    - anxious
    - scared
  HELLO:
    - hello
    - hi
    - hey

mcp_server:
  url: http://localhost:8080
  timeout: 30
```

## Configuration Examples

### Minimal Configuration

Only override what you need:

```python
config = {
    "classification_rules": {
        "NEXT": ["next", "continue"],
        "PREVIOUS": ["back"]
    }
}

manager = StageManager(config=config)
# Other status codes use default patterns
```

### Production Configuration

```python
import os

config = {
    "llm": {
        "api_key": os.getenv("LLM_API_KEY"),
        "model": "gpt-4",
        "timeout": 30,
        "max_retries": 3
    },
    "classification_rules": {
        "NEXT": ["next", "continue", "proceed", "forward", "go on"],
        "PREVIOUS": ["back", "previous", "return", "go back"],
        "EXIT": ["exit", "quit", "leave", "stop", "end"],
        "HELP": ["help", "assist", "support", "call"],
        "CARE": ["worried", "anxious", "scared", "concerned", "upset"],
        "HELLO": ["hello", "hi", "hey", "greetings"]
    },
    "mcp_server": {
        "url": "https://mcp.production.example.com",
        "timeout": 30
    }
}
```

### Development Configuration

```python
import os

config = {
    "llm": {
        "api_key": os.getenv("LLM_API_KEY"),
        "model": "gpt-3.5-turbo",  # Faster/cheaper for development
        "timeout": 60,  # Longer timeout for debugging
        "max_retries": 2
    },
    "classification_rules": {
        "NEXT": ["next", "n", "continue", "c"],  # Short aliases for testing
        "PREVIOUS": ["back", "b", "prev", "p"],
        "EXIT": ["exit", "quit", "q"],
        "HELP": ["help", "h", "?"]
    },
    "mcp_server": {
        "url": "http://localhost:8080",
        "timeout": 60  # Longer timeout for debugging
    }
}
```

### Multi-Language Configuration

```python
config = {
    "classification_rules": {
        "NEXT": [
            # English
            "next", "continue", "proceed",
            # Spanish
            "siguiente", "continuar", "proceder",
            # French
            "suivant", "continuer", "procéder"
        ],
        "PREVIOUS": [
            # English
            "back", "previous",
            # Spanish
            "atrás", "anterior",
            # French
            "retour", "précédent"
        ],
        "HELP": [
            # English
            "help", "assist",
            # Spanish
            "ayuda", "asistir",
            # French
            "aide", "aider"
        ]
    }
}
```

## Best Practices

### 1. Start with Defaults

Begin with default configuration and only customize what you need:

```python
# Good: Minimal customization
config = {
    "classification_rules": {
        "CARE": ["worried", "anxious", "scared", "emergency"]
    }
}

# Avoid: Unnecessary full configuration
# (unless you really need to change everything)
```

### 2. Use Specific Patterns

More specific patterns reduce false positives:

```python
# Good: Specific patterns
"NEXT": ["next step", "continue to next", "proceed forward"]

# Risky: Very generic patterns
"NEXT": ["ok", "yes", "sure"]  # Too broad, may match unintended input
```

### 3. Avoid Pattern Overlap

Ensure patterns don't overlap between status codes:

```python
# Bad: "help" appears in multiple status codes
"HELP": ["help", "need help"],
"CARE": ["help me", "need help"]  # Conflict!

# Good: Distinct patterns
"HELP": ["help", "assist", "guide"],
"CARE": ["worried", "anxious", "scared"]
```

### 4. Test Your Configuration

Always test custom configurations:

```python
manager = StageManager(config=custom_config)

test_inputs = [
    "next please",
    "go back",
    "I need help",
    "I'm worried"
]

for input_text in test_inputs:
    result = manager.classify(input_text)
    print(f"{input_text} -> {result['status']}")
```

### 5. Document Custom Patterns

Keep documentation of why you chose specific patterns:

```python
config = {
    "classification_rules": {
        # Added "onward" for military/formal contexts
        "NEXT": ["next", "continue", "proceed", "onward"],
        
        # Added "distressed" for healthcare context
        "CARE": ["worried", "anxious", "scared", "distressed"]
    }
}
```

### 6. Use Environment-Specific Configs

Different configurations for different environments:

```python
import os

env = os.getenv("ENVIRONMENT", "development")

if env == "production":
    config = load_config("config.production.json")
elif env == "staging":
    config = load_config("config.staging.json")
else:
    config = load_config("config.development.json")

manager = StageManager(config=config)
```

### 7. Version Your Configuration

Keep configuration in version control:

```
project/
├── config/
│   ├── default.json
│   ├── production.json
│   ├── staging.json
│   └── development.json
├── stage_manager/
└── tests/
```

### 8. Validate Configuration

Validate configuration before using:

```python
def validate_config(config):
    """Validate configuration structure."""
    if "classification_rules" in config:
        rules = config["classification_rules"]
        required_codes = ["NEXT", "PREVIOUS", "EXIT", "HELP", "CARE", "HELLO"]
        
        for code in required_codes:
            if code not in rules:
                print(f"Warning: Missing classification rules for {code}")
            elif not isinstance(rules[code], list):
                raise ValueError(f"Rules for {code} must be a list")
    
    if "mcp_server" in config:
        mcp = config["mcp_server"]
        if "url" not in mcp:
            raise ValueError("MCP server URL is required")
        if "timeout" in mcp and mcp["timeout"] <= 0:
            raise ValueError("MCP timeout must be positive")
    
    return True

# Use validation
if validate_config(config):
    manager = StageManager(config=config)
```

## Troubleshooting

### Configuration Not Applied

**Problem**: Custom patterns don't seem to work

**Solution**: Check that configuration is passed to constructor:

```python
# Wrong
config = {...}
manager = StageManager()  # Config not passed!

# Correct
config = {...}
manager = StageManager(config=config)
```

### MCP Connection Fails

**Problem**: MCP server connection fails during initialization

**Solution**: This is expected behavior. StageManager logs a warning and continues without MCP:

```python
# Check logs for:
# "MCP server unavailable during initialization"
# "Continuing without MCP integration"
```

### Pattern Not Matching

**Problem**: User input not matching expected pattern

**Solution**: Check pattern matching rules:

```python
# Patterns are case-insensitive and substring matches
"NEXT": ["next"]  # Matches: "next", "Next", "NEXT", "next please"

# Test your patterns
manager = StageManager(config=config)
result = manager.classify("your test input")
print(result['status'])
```

### Invalid Configuration Format

**Problem**: Configuration causes errors

**Solution**: Ensure correct structure:

```python
# Correct structure
config = {
    "classification_rules": {  # Dict
        "NEXT": ["next", "continue"]  # List of strings
    },
    "mcp_server": {  # Dict
        "url": "http://localhost:8080",  # String
        "timeout": 30  # Integer
    }
}
```

## Additional Resources

- [API Documentation](API.md) - Detailed API reference
- [Examples](../examples/) - Working code examples
- [README](../README.md) - Getting started guide
