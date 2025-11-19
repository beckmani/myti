"""Input validation module for StageManager."""

import json
import logging
from typing import Dict, Any, Optional


logger = logging.getLogger(__name__)


class InputValidator:
    """
    Validates and sanitizes user input and task context.
    
    This class provides static methods for validating user text input
    and task context JSON structures according to the requirements.
    """
    
    @staticmethod
    def validate_user_input(user_input: str) -> bool:
        """
        Validate user text input is not empty or whitespace-only.
        
        Args:
            user_input: User's text input string
            
        Returns:
            True if input is valid (non-empty and not whitespace-only),
            False otherwise
            
        Requirements: 1.1, 1.2
        """
        if user_input is None:
            return False
        
        if not isinstance(user_input, str):
            return False
        
        # Check if string is empty or contains only whitespace
        if not user_input or user_input.isspace():
            return False
        
        return True
    
    @staticmethod
    def validate_task_context(task_context: Dict[str, Any]) -> bool:
        """
        Validate task context has required fields: task, description, status, stages.
        
        Args:
            task_context: Dictionary containing task context information
            
        Returns:
            True if task context is valid with all required fields,
            False otherwise
            
        Requirements: 4.1, 4.2, 4.4
        """
        if task_context is None:
            return False
        
        if not isinstance(task_context, dict):
            return False
        
        # Check for required top-level fields
        required_fields = ["task", "description", "status", "stages"]
        for field in required_fields:
            if field not in task_context:
                logger.warning(f"Task context missing required field: {field}")
                return False
        
        # Validate stages is a list
        if not isinstance(task_context["stages"], list):
            logger.warning("Task context 'stages' field must be a list")
            return False
        
        # Validate each stage has required fields
        for idx, stage in enumerate(task_context["stages"]):
            if not isinstance(stage, dict):
                logger.warning(f"Stage at index {idx} is not a dictionary")
                return False
            
            stage_required_fields = ["stage", "description", "timeout"]
            for field in stage_required_fields:
                if field not in stage:
                    logger.warning(f"Stage at index {idx} missing required field: {field}")
                    return False
            
            # Validate timeout is a number
            if not isinstance(stage["timeout"], (int, float)):
                logger.warning(f"Stage at index {idx} has invalid timeout type")
                return False
        
        return True
    
    @staticmethod
    def parse_task_context(task_json: str) -> Optional[Dict[str, Any]]:
        """
        Parse JSON string to task context dictionary.
        
        Args:
            task_json: JSON string representation of task context
            
        Returns:
            Parsed dictionary if successful, None if parsing fails
            
        Raises:
            json.JSONDecodeError: If JSON is malformed
            
        Requirements: 4.1, 4.4
        """
        if task_json is None:
            return None
        
        if not isinstance(task_json, str):
            return None
        
        try:
            parsed = json.loads(task_json)
            return parsed
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse task context JSON: {e}")
            raise
