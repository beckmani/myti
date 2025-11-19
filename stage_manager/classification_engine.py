"""Classification engine for determining user intent."""

from typing import Dict, Optional, List
import re


class ClassificationEngine:
    """Core classification logic with pattern matching and context awareness."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize with optional classification rules configuration.
        
        Args:
            config: Optional configuration dictionary for classification rules
        """
        self.config = config or self._get_default_config()
        self.classification_rules = self.config.get("classification_rules", {})
    
    def _get_default_config(self) -> Dict:
        """Get default classification configuration."""
        return {
            "classification_rules": {
                "NEXT": ["next", "continue", "proceed", "forward", "go on"],
                "PREVIOUS": ["back", "previous", "return", "go back"],
                "EXIT": ["exit", "quit", "leave", "stop", "end"],
                "HELP": ["help", "assist", "support", "call"],
                "CARE": ["worried", "anxious", "scared", "concerned", "upset"],
                "HELLO": ["hello", "hi", "hey", "greetings"]
            }
        }
    
    def classify_intent(self, user_input: str, task_context: Optional[Dict] = None) -> str:
        """
        Determine the status code from user input and context.
        
        Args:
            user_input: User's text input
            task_context: Optional task context with stages
            
        Returns:
            One of: NEXT, PREVIOUS, EXIT, HELP, CARE, HELLO, UNKNOWN
        """
        normalized_input = user_input.lower().strip()
        
        # Extract stage information (prioritizes user input over context)
        current_stage = self.extract_stage_info(user_input, task_context)
        
        # Check each status code pattern
        for status_code, patterns in self.classification_rules.items():
            for pattern in patterns:
                if pattern in normalized_input:
                    # Apply stage-aware logic for PREVIOUS and NEXT
                    if status_code == "PREVIOUS" and task_context and current_stage:
                        # If at first stage, don't allow PREVIOUS
                        if self.is_at_first_stage(task_context, current_stage):
                            return "UNKNOWN"
                    
                    if status_code == "NEXT" and task_context and current_stage:
                        # If at last stage, don't allow NEXT
                        if self.is_at_last_stage(task_context, current_stage):
                            return "UNKNOWN"
                    
                    return status_code
        
        # Default to UNKNOWN if no pattern matches
        return "UNKNOWN"
    
    def extract_stage_info(self, user_input: str, task_context: Optional[Dict] = None) -> Optional[str]:
        """
        Extract current stage information from input or context.
        
        Args:
            user_input: User's text input
            task_context: Optional task context
            
        Returns:
            Stage name if found, None otherwise
        """
        # Try to extract stage from user input first
        # Look for patterns like "at stage X" or "stage X"
        stage_pattern = r'(?:at\s+)?stage\s+(\w+)'
        match = re.search(stage_pattern, user_input.lower())
        if match:
            return match.group(1)
        
        # Fall back to task context if available
        if task_context and "current_stage" in task_context:
            return task_context["current_stage"]
        
        return None
    
    def is_at_first_stage(self, task_context: Dict, current_stage: str) -> bool:
        """
        Check if current stage is the first stage.
        
        Args:
            task_context: Task context with stages
            current_stage: Current stage name
            
        Returns:
            True if at first stage, False otherwise
        """
        if not task_context or "stages" not in task_context:
            return False
        
        stages = task_context["stages"]
        if not stages:
            return False
        
        return stages[0].get("stage") == current_stage
    
    def is_at_last_stage(self, task_context: Dict, current_stage: str) -> bool:
        """
        Check if current stage is the last stage.
        
        Args:
            task_context: Task context with stages
            current_stage: Current stage name
            
        Returns:
            True if at last stage, False otherwise
        """
        if not task_context or "stages" not in task_context:
            return False
        
        stages = task_context["stages"]
        if not stages:
            return False
        
        return stages[-1].get("stage") == current_stage
