# StageManager Quick Start Guide

Get up and running with StageManager in 5 minutes.

## Installation

```bash
pip install -e .
```

## Basic Usage

### 1. Simple Classification

```python
from stage_manager.stage_manager import StageManager

# Create a manager
manager = StageManager()

# Classify user input
result = manager.classify("I want to continue")
print(result)
# Output: {"status": "NEXT", "message": "Moving forward to the next stage."}
```

### 2. With Task Context

```python
from stage_manager.stage_manager import StageManager

manager = StageManager()

# Define your task
task_context = {
    "task": "morning_routine",
    "description": "Daily morning routine",
    "status": "in progress",
    "current_stage": "breakfast",
    "stages": [
        {"stage": "wake_up", "description": "Wake up", "timeout": 300},
        {"stage": "breakfast", "description": "Eat breakfast", "timeout": 600},
        {"stage": "exercise", "description": "Exercise", "timeout": 900}
    ]
}

# Classify with context
result = manager.classify("go back", task_context)
print(result)
# Output: {"status": "PREVIOUS", "message": "Going back to the previous stage."}
```

### 3. Custom Configuration

```python
from stage_manager.stage_manager import StageManager

# Customize classification patterns
config = {
    "classification_rules": {
        "NEXT": ["next", "continue", "proceed", "onward"],
        "PREVIOUS": ["back", "previous", "rewind"],
        "CARE": ["worried", "anxious", "stressed", "overwhelmed"]
    }
}

manager = StageManager(config=config)

result = manager.classify("onward!")
print(result['status'])  # Output: NEXT
```

## Status Codes

| Code | Meaning | Example Input |
|------|---------|---------------|
| NEXT | Move forward | "continue", "next", "proceed" |
| PREVIOUS | Go back | "back", "previous", "return" |
| EXIT | Exit task | "quit", "exit", "stop" |
| HELP | Need help | "help", "assist", "support" |
| CARE | Need support | "worried", "anxious", "scared" |
| HELLO | Greeting | "hello", "hi", "hey" |
| UNKNOWN | Unclear | Anything else |

## Common Patterns

### Building a Task Flow

```python
from stage_manager.stage_manager import StageManager
from stage_manager.models import TaskContext, Stage

# Create task with data models
task = TaskContext(
    task="onboarding",
    description="User onboarding",
    status="in progress",
    stages=[
        Stage(stage="welcome", description="Welcome", timeout=60),
        Stage(stage="profile", description="Create profile", timeout=300),
        Stage(stage="complete", description="Complete", timeout=30)
    ]
)

manager = StageManager()

# Process user input
result = manager.classify("next please", task.to_dict())
```

### Error Handling

```python
manager = StageManager()

# Empty input returns error
result = manager.classify("")
print(result)
# Output: {"status": "ERROR", "message": "Input cannot be empty or whitespace-only"}

# Invalid context returns error
result = manager.classify("next", {"task": "test"})  # Missing fields
print(result)
# Output: {"status": "ERROR", "message": "Invalid task context structure"}
```

### MCP Integration

```python
config = {
    "mcp_server": {
        "url": "http://localhost:8080",
        "timeout": 30
    }
}

manager = StageManager(config=config)

# CARE status triggers caregiver notification
result = manager.classify("I'm feeling anxious")
# Caregiver is automatically notified via MCP
```

## Next Steps

- **Examples**: Check out `examples/basic_usage.py` and `examples/advanced_usage.py`
- **API Reference**: See `docs/API.md` for detailed API documentation
- **Configuration**: Read `docs/CONFIGURATION.md` for configuration options
- **Full Documentation**: See `README.md` for comprehensive guide

## Common Issues

### "Input cannot be empty"

Make sure your input is not empty or whitespace-only:

```python
# Wrong
result = manager.classify("")

# Correct
result = manager.classify("next")
```

### "Invalid task context structure"

Ensure your task context has all required fields:

```python
# Wrong
task_context = {"task": "test"}

# Correct
task_context = {
    "task": "test",
    "description": "Test task",
    "status": "active",
    "stages": [
        {"stage": "step1", "description": "First step", "timeout": 300}
    ]
}
```

### MCP Connection Failed

This is expected if MCP server is not running. StageManager continues to work without MCP:

```python
# MCP unavailable - logs warning but continues
manager = StageManager(config={"mcp_server": {"url": "http://localhost:8080"}})
# Still works for classification, just no caregiver notifications
```

## Getting Help

- Run examples: `python examples/basic_usage.py`
- Check logs: StageManager uses Python logging
- Read docs: See `docs/` directory for detailed documentation
