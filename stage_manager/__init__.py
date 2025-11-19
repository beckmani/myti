"""
StageManager - A classifier agent for task stage navigation.

This package provides a stage manager classifier agent built using the strends
library. The agent classifies user text input into status codes (NEXT, PREVIOUS,
EXIT, HELP, CARE, HELLO, UNKNOWN) to help users navigate through multi-stage tasks.
"""

__version__ = "0.1.0"

from .stage_manager import StageManager
from .input_validator import InputValidator
from .classification_engine import ClassificationEngine
from .response_generator import ResponseGenerator
from .mcp_client import MCPClient
from .models import Stage, TaskContext, ClassificationResponse

__all__ = [
    "StageManager",
    "InputValidator",
    "ClassificationEngine",
    "ResponseGenerator",
    "MCPClient",
    "Stage",
    "TaskContext",
    "ClassificationResponse",
]
