"""Classification engine for determining user intent."""

from typing import Dict, Optional, List
import re
import logging


# Configure logger for this module
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class ClassificationEngine:
    """Core classification logic with LLM integration and context awareness."""
    
    def __init__(self, config: Optional[Dict] = None, llm_client=None):
        """
        Initialize with optional configuration and LLM client.
        
        Args:
            config: Optional configuration dictionary for classification rules
            llm_client: Optional LLM client for classification
        """
        try:
            self.config = config or self._get_default_config()
            self.llm_client = llm_client
            classification_rules = self.config.get("classification_rules", self._get_default_classificartion_rules())
            
            # Validate classification_rules is a dict, fall back to defaults if not
            if not isinstance(classification_rules, dict):
                logger.warning("Classification rules is not a dictionary, using defaults")
                default_config = self._get_default_classificartion_rules()
                self.classification_rules = default_config["classification_rules"]
            else:
                self.classification_rules = classification_rules
                logger.info("Classification engine initialized with custom rules")
            
            if self.llm_client:
                logger.info("Classification engine initialized with LLM client")
            else:
                logger.info("Classification engine initialized without LLM client (pattern-based only)")
                
        except Exception as e:
            logger.error(f"Error initializing classification engine: {e}", exc_info=True)
            # Fall back to default configuration
            default_config = self._get_default_config()
            self.config = default_config
            self.classification_rules = default_config["classification_rules"]
            logger.info("Fell back to default configuration")
    
    def _get_default_classificartion_rules(self) -> Dict:
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
        Determine the status code from user input and context using LLM.
        
        Args:
            user_input: User's text input
            task_context: Optional task context with stages
            
        Returns:
            One of: NEXT, PREVIOUS, EXIT, HELP, CARE, HELLO, UNKNOWN
        """
        try:
            if not user_input:
                logger.warning("Empty user input provided to classify_intent")
                return "UNKNOWN"
            
            logger.debug(f"Classifying input: '{user_input[:50]}...'")
            
            # If LLM client is available, use it for classification
            if self.llm_client:
                try:
                    logger.debug("Using LLM for classification")
                    prompt = self._build_llm_prompt(user_input, task_context)
                    response = self.llm_client.classify(prompt)
                    
                    # Extract status from LLM response
                    status = response.get("status", "UNKNOWN")
                    
                    # Validate status is one of the valid codes
                    valid_statuses = {"NEXT", "PREVIOUS", "EXIT", "HELP", "CARE", "HELLO", "UNKNOWN"}
                    if status not in valid_statuses:
                        logger.warning(f"LLM returned invalid status '{status}', falling back to UNKNOWN")
                        return "UNKNOWN"
                    
                    logger.info(f"LLM classified as {status}")
                    return status
                    
                except Exception as e:
                    logger.error(f"LLM classification failed: {e}, falling back to pattern matching")
                    # Fall through to pattern-based classification
            
            # Fall back to pattern-based classification if LLM is not available or fails
            normalized_input = user_input.lower().strip()
            
            # Extract stage information (prioritizes user input over context)
            current_stage = self.extract_stage_info(user_input, task_context)
            if current_stage:
                logger.debug(f"Current stage identified: {current_stage}")
            
            # Check each status code pattern
            for status_code, patterns in self.classification_rules.items():
                if not isinstance(patterns, list):
                    logger.warning(f"Patterns for {status_code} is not a list, skipping")
                    continue
                    
                for pattern in patterns:
                    if not isinstance(pattern, str):
                        logger.warning(f"Pattern {pattern} for {status_code} is not a string, skipping")
                        continue
                        
                    if pattern in normalized_input:
                        logger.debug(f"Pattern '{pattern}' matched for status code {status_code}")
                        
                        # Apply stage-aware logic for PREVIOUS and NEXT
                        if status_code == "PREVIOUS" and task_context and current_stage:
                            # If at first stage, don't allow PREVIOUS
                            if self.is_at_first_stage(task_context, current_stage):
                                logger.info("PREVIOUS requested at first stage, returning UNKNOWN")
                                return "UNKNOWN"
                        
                        if status_code == "NEXT" and task_context and current_stage:
                            # If at last stage, don't allow NEXT
                            if self.is_at_last_stage(task_context, current_stage):
                                logger.info("NEXT requested at last stage, returning UNKNOWN")
                                return "UNKNOWN"
                        
                        logger.info(f"Classified as {status_code}")
                        return status_code
            
            # Default to UNKNOWN if no pattern matches
            logger.info("No pattern matched, returning UNKNOWN")
            return "UNKNOWN"
            
        except Exception as e:
            logger.error(f"Error during intent classification: {e}", exc_info=True)
            # Fail gracefully by returning UNKNOWN
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
        try:
            # Try to extract stage from user input first
            # Look for patterns like "at stage X" or "stage X"
            if user_input:
                stage_pattern = r'(?:at\s+)?stage\s+(\w+)'
                match = re.search(stage_pattern, user_input.lower())
                if match:
                    stage_name = match.group(1)
                    logger.debug(f"Extracted stage from user input: {stage_name}")
                    return stage_name
            
            # Fall back to task context if available
            if task_context and isinstance(task_context, dict):
                if "current_stage" in task_context:
                    stage_name = task_context["current_stage"]
                    logger.debug(f"Using stage from task context: {stage_name}")
                    return stage_name
            
            logger.debug("No stage information found")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting stage info: {e}", exc_info=True)
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
        try:
            if not task_context or not isinstance(task_context, dict):
                logger.debug("Task context is None or not a dict")
                return False
            
            if "stages" not in task_context:
                logger.debug("Task context missing 'stages' field")
                return False
            
            stages = task_context["stages"]
            if not stages or not isinstance(stages, list):
                logger.debug("Stages is empty or not a list")
                return False
            
            first_stage = stages[0].get("stage") if isinstance(stages[0], dict) else None
            is_first = first_stage == current_stage
            logger.debug(f"Is at first stage: {is_first} (current: {current_stage}, first: {first_stage})")
            return is_first
            
        except Exception as e:
            logger.error(f"Error checking if at first stage: {e}", exc_info=True)
            return False
    
    def is_at_last_stage(self, task_context: Dict, current_stage: str) -> bool:
        """
        Check if current stage is the last stage.
        
        Args:
            task_context: Task context with stages
            current_stage: Current stage name
            
        Returns:
            True if at last stage, False otherwise
        """
        try:
            if not task_context or not isinstance(task_context, dict):
                logger.debug("Task context is None or not a dict")
                return False
            
            if "stages" not in task_context:
                logger.debug("Task context missing 'stages' field")
                return False
            
            stages = task_context["stages"]
            if not stages or not isinstance(stages, list):
                logger.debug("Stages is empty or not a list")
                return False
            
            last_stage = stages[-1].get("stage") if isinstance(stages[-1], dict) else None
            is_last = last_stage == current_stage
            logger.debug(f"Is at last stage: {is_last} (current: {current_stage}, last: {last_stage})")
            return is_last
            
        except Exception as e:
            logger.error(f"Error checking if at last stage: {e}", exc_info=True)
            return False
    
    def _build_llm_prompt(self, user_input: str, task_context: Optional[Dict] = None) -> str:
        """
        Build the prompt for LLM classification.
        
        Includes user input, task context, stage information, and classification instructions.
        
        Args:
            user_input: User's text input
            task_context: Optional task context with stages
            
        Returns:
            Formatted prompt string for LLM
        """
        try:
            # Start with base instructions
            prompt = """You are a task navigation assistant. Classify the user's intent into one of these status codes:

- NEXT: User wants to proceed to the next stage
- PREVIOUS: User wants to go back to the previous stage
- EXIT: User wants to quit or leave the task
- HELP: User needs assistance or information
- CARE: User expresses concern, emotion, or needs support
- HELLO: User is greeting or introducing themselves
- UNKNOWN: Intent is unclear or doesn't match other categories

"""
            
            # Add task context if available
            if task_context and isinstance(task_context, dict):
                prompt += "Task Context:\n"
                
                # Add task name
                if "task" in task_context:
                    prompt += f"- Task: {task_context['task']}\n"
                
                # Add task description
                if "description" in task_context:
                    prompt += f"- Description: {task_context['description']}\n"
                
                # Extract and add current stage information
                current_stage = self.extract_stage_info(user_input, task_context)
                if current_stage:
                    prompt += f"- Current Stage: {current_stage}\n"
                    
                    # Add stage description if available
                    if "stages" in task_context and isinstance(task_context["stages"], list):
                        for stage in task_context["stages"]:
                            if isinstance(stage, dict) and stage.get("stage") == current_stage:
                                if "description" in stage:
                                    prompt += f"  ({stage['description']})\n"
                                break
                        
                        # Add stage position information
                        if self.is_at_first_stage(task_context, current_stage):
                            prompt += "- Stage Position: First stage (cannot go back)\n"
                        elif self.is_at_last_stage(task_context, current_stage):
                            prompt += "- Stage Position: Last stage (cannot go forward)\n"
                        else:
                            prompt += "- Stage Position: Middle stage\n"
                
                prompt += "\n"
            
            # Add user input
            prompt += f'User Input: "{user_input}"\n\n'
            
            # Add response format instructions
            prompt += "Respond with ONLY the status code (one word) followed by a brief explanation.\n"
            prompt += "Format: STATUS_CODE: explanation"
            
            logger.debug(f"Built LLM prompt with {len(prompt)} characters")
            return prompt
            
        except Exception as e:
            logger.error(f"Error building LLM prompt: {e}", exc_info=True)
            # Return a minimal prompt if there's an error
            return f'Classify this user input into one of: NEXT, PREVIOUS, EXIT, HELP, CARE, HELLO, UNKNOWN\n\nUser Input: "{user_input}"\n\nRespond with: STATUS_CODE: explanation'
