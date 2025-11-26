# StageManager Examples

This directory contains example scripts demonstrating how to use the StageManager agent.

## Running Examples

### Basic Usage Examples

Demonstrates fundamental StageManager features:

```bash
python examples/basic_usage.py
```

**Covers:**
- Basic classification without context
- Classification with task context
- Custom configuration
- MCP integration
- Error handling
- Stage boundary awareness

### Advanced Usage Examples

Demonstrates advanced patterns and integration:

```bash
python examples/advanced_usage.py
```

**Covers:**
- Building a complete task flow system
- Configuration management (loading from files)
- Working with data models
- Error recovery patterns
- Unicode and special character handling

### AWS Bedrock Examples

Demonstrates AWS Bedrock integration:

```bash
python examples/bedrock_usage.py
```

**Covers:**
- Using Bedrock with configuration (recommended)
- Bedrock configuration options
- AWS credentials management
- Error handling with Bedrock

**Prerequisites:**
- AWS credentials configured (environment variables, ~/.aws/credentials, or IAM role)
- boto3 installed: `pip install boto3`
- IAM permissions for `bedrock:InvokeModel`

## Example Files

### `basic_usage.py`

Entry-level examples showing core functionality. Start here if you're new to StageManager.

**Examples included:**
1. Basic Classification - Simple input classification
2. Classification with Task Context - Using task stages
3. Custom Classification Rules - Customizing patterns
4. MCP Integration - Caregiver notifications
5. Error Handling - Handling invalid input
6. Stage Boundary Awareness - First/last stage logic

### `advanced_usage.py`

Advanced patterns for building production systems.

**Examples included:**
1. Task Flow System - Complete task navigation system
2. Configuration Management - Loading config from files
3. Working with Data Models - Using TaskContext and Stage classes
4. Error Recovery - Handling various error conditions
5. Unicode Handling - International character support

### `bedrock_usage.py`

AWS Bedrock integration examples.

**Examples included:**
1. Using Bedrock with Configuration - Recommended approach
2. Bedrock with Task Context - Context-aware classification
3. AWS Credentials Management - Different credential methods
4. Error Handling - Graceful error handling with Bedrock

**Prerequisites:**
- AWS credentials configured
- boto3 installed: `pip install boto3`
- IAM permissions for `bedrock:InvokeModel`

### `config.json`

Example configuration file showing all available options.

**Usage:**
```python
import json
from stage_manager.stage_manager import StageManager

with open("examples/config.json", "r") as f:
    config = json.load(f)

manager = StageManager(config=config)
```

## Quick Examples

### Minimal Example

```python
from stage_manager.stage_manager import StageManager

manager = StageManager()
result = manager.classify("continue")
print(result['status'])  # Output: NEXT
```

### With Task Context

```python
from stage_manager.stage_manager import StageManager

manager = StageManager()

task = {
    "task": "tutorial",
    "description": "Tutorial steps",
    "status": "in progress",
    "stages": [
        {"stage": "step1", "description": "First step", "timeout": 300},
        {"stage": "step2", "description": "Second step", "timeout": 300}
    ]
}

result = manager.classify("next", task)
print(result)
```

### Custom Configuration

```python
from stage_manager.stage_manager import StageManager

config = {
    "classification_rules": {
        "NEXT": ["next", "continue", "onward"],
        "CARE": ["worried", "anxious", "stressed"]
    }
}

manager = StageManager(config=config)
result = manager.classify("onward")
print(result['status'])  # Output: NEXT
```

## Testing Examples

You can use these examples to verify your installation:

```bash
# Run all basic examples
python examples/basic_usage.py

# Run all advanced examples
python examples/advanced_usage.py
```

Both scripts should complete without errors and display example outputs.

## Customizing Examples

Feel free to modify these examples to test your own use cases:

1. **Change input patterns**: Edit the `test_inputs` lists
2. **Modify task contexts**: Change stage definitions
3. **Test custom configs**: Create your own configuration dictionaries
4. **Add new examples**: Copy and modify existing example functions

## Example Output

When you run the examples, you'll see:

- Classification results for various inputs
- Status codes and messages
- Task flow progression
- Error handling demonstrations
- Configuration loading examples

## Next Steps

After running the examples:

1. Read the [API Documentation](../docs/API.md)
2. Review the [Configuration Guide](../docs/CONFIGURATION.md)
3. Check the [Quick Start Guide](../docs/QUICKSTART.md)
4. Build your own application using StageManager

## Troubleshooting

### Import Errors

If you get import errors, make sure StageManager is installed:

```bash
pip install -e .
```

### MCP Connection Warnings

It's normal to see MCP connection warnings if you don't have an MCP server running. The examples will still work - they just won't send caregiver notifications.

### Unicode Display Issues

If unicode characters don't display correctly, ensure your terminal supports UTF-8 encoding.

## Contributing Examples

Have a useful example? Consider contributing:

1. Create a new example file
2. Follow the existing format
3. Add documentation
4. Test thoroughly
5. Submit a pull request
