"""Input validation module for StageManager."""

import json
import logging
from typing import Dict, Any, Optional


# Configure logger for this module
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


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
        try:
            if user_input is None:
                logger.warning("User input is None")
                return False
            
            if not isinstance(user_input, str):
                logger.warning(f"User input is not a string, got type: {type(user_input)}")
                return False
            
            # Check if string is empty or contains only whitespace
            if not user_input or user_input.isspace():
                logger.warning("User input is empty or whitespace-only")
                return False
            
            logger.debug(f"User input validated successfully: '{user_input[:50]}...'")
            return True
            
        except Exception as e:
            logger.error(f"Unexpected error during user input validation: {e}", exc_info=True)
            return False
    
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
        try:
            if task_context is None:
                logger.warning("Task context is None")
                return False
            
            if not isinstance(task_context, dict):
                logger.warning(f"Task context is not a dictionary, got type: {type(task_context)}")
                return False
            
            # Check for required top-level fields
            required_fields = ["task", "description", "status", "stages"]
            for field in required_fields:
                if field not in task_context:
                    logger.warning(f"Task context missing required field: {field}")
                    return False
            
            # Validate stages is a list
            if not isinstance(task_context["stages"], list):
                logger.warning(f"Task context 'stages' field must be a list, got type: {type(task_context['stages'])}")
                return False
            
            # Validate each stage has required fields
            for idx, stage in enumerate(task_context["stages"]):
                if not isinstance(stage, dict):
                    logger.warning(f"Stage at index {idx} is not a dictionary, got type: {type(stage)}")
                    return False
                
                stage_required_fields = ["stage", "description", "timeout"]
                for field in stage_required_fields:
                    if field not in stage:
                        logger.warning(f"Stage at index {idx} missing required field: {field}")
                        return False
                
                # Validate timeout is a number
                if not isinstance(stage["timeout"], (int, float)):
                    logger.warning(f"Stage at index {idx} has invalid timeout type: {type(stage['timeout'])}")
                    return False
                
                # Validate timeout is non-negative
                if stage["timeout"] < 0:
                    logger.warning(f"Stage at index {idx} has negative timeout: {stage['timeout']}")
                    return False
            
            logger.debug(f"Task context validated successfully for task: {task_context.get('task')}")
            return True
            
        except Exception as e:
            logger.error(f"Unexpected error during task context validation: {e}", exc_info=True)
            return False
    
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
        try:
            if task_json is None:
                logger.warning("Task JSON is None")
                return None
            
            if not isinstance(task_json, str):
                logger.warning(f"Task JSON is not a string, got type: {type(task_json)}")
                return None
            
            if not task_json.strip():
                logger.warning("Task JSON is empty or whitespace-only")
                return None
            
            parsed = json.loads(task_json)
            logger.debug("Task context JSON parsed successfully")
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse task context JSON: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error during JSON parsing: {e}", exc_info=True)
            return None
