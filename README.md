# StageManager

A stage manager classifier agent built using the strends library in Python.

## Overview

The StageManager helps users navigate through multi-stage tasks by classifying their text input into one of seven status codes:
- **NEXT**: Proceed to the next stage
- **PREVIOUS**: Go back to the previous stage
- **EXIT**: Exit the task flow
- **HELP**: Request assistance
- **CARE**: Express need for support (triggers caregiver notification)
- **HELLO**: Greeting or introduction
- **UNKNOWN**: Unclear or ambiguous input

## Installation

```bash
pip install -e .
```

For development with testing dependencies:

```bash
pip install -e ".[dev]"
```

## Usage

```python
from stage_manager import StageManager

# Initialize the agent
manager = StageManager()

# Classify user input
result = manager.classify("I want to continue")
print(result)  # {"status": "NEXT", "message": "..."}

# Classify with task context
task_context = {
    "task": "morning_routine",
    "description": "Daily morning routine",
    "status": "in progress",
    "stages": [
        {"stage": "wake_up", "description": "Wake up", "timeout": 300},
        {"stage": "breakfast", "description": "Eat breakfast", "timeout": 600}
    ]
}

result = manager.classify("go back", task_context)
print(result)  # {"status": "PREVIOUS", "message": "..."}
```

## Development

Run tests:

```bash
pytest
```

Run property-based tests:

```bash
pytest tests/property/
```

## Requirements

- Python >= 3.8
- strends >= 0.1.0
- hypothesis >= 6.0.0 (for property-based testing)
