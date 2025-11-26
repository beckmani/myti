"""Main StageManager agent implementation."""

import logging
from typing import Dict, Optional, Any

# No external agent library needed - using plain Python class

from .input_validator import InputValidator
from .classification_engine import ClassificationEngine
from .response_generator import ResponseGenerator
from .llm_client import LLMClient


# Configure logger for this module
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class StageManager:
    """
    Main classifier agent for task stage navigation.
    
    The StageManager classifies user text input into status codes
    (NEXT, PREVIOUS, EXIT, HELP, CARE, HELLO, UNKNOWN) to help users
    navigate through multi-stage tasks.
    """
    
    def __init__(self, config: Optional[Dict] = None, bedrock_model: Optional[Any] = None):
        """
        Initialize the StageManager agent.
        
        Args:
            config: Optional configuration dictionary for classification rules and MCP settings
            bedrock_model: Optional BedrockModel instance for AWS Bedrock integration
            
        Requirements: 5.1, 5.2, 5.3, 11.1, 11.2, 11.3, 11.4
        """
        
        try:
            logger.info("Initializing StageManager agent")
            
            self.config = config or {}
            self.validator = InputValidator()
            self.bedrock_model = bedrock_model
            
            # Initialize Bedrock client wrapper if BedrockModel is provided
            llm_client = None
            
            if self.bedrock_model is not None:
                logger.info("Using provided BedrockModel instance")
                # Wrap BedrockModel in LLMClient-compatible interface
                llm_client = self._create_bedrock_llm_client(self.bedrock_model)
            else:
                logger.info("No BedrockModel provided, using pattern-based classification")
            
            # Initialize classification engine with config and Bedrock client (Requirement 5.1)
            self.engine = ClassificationEngine(config, llm_client)
            self.response_generator = ResponseGenerator()
            
            logger.info("StageManager agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Critical error initializing StageManager: {e}", exc_info=True)
            raise
    
    def _create_bedrock_llm_client(self, bedrock_model: Any):
        """
        Create an LLM client wrapper for BedrockModel.
        
        Args:
            bedrock_model: BedrockModel instance
            
        Returns:
            LLM client wrapper
        """
        class BedrockLLMWrapper:
            """Wrapper to make BedrockModel compatible with LLMClient interface."""
            
            def __init__(self, model):
                self.model = model
                self.provider = "bedrock"
            
            def classify(self, prompt: str) -> Dict[str, str]:
                """Call Bedrock model and parse response."""
                try:
                    response_text = self.model.invoke(
                        prompt=prompt,
                        system_prompt="You are a task navigation assistant."
                    )
                    
                    # Parse response using same logic as LLMClient
                    return self._parse_response(response_text)
                    
                except Exception as e:
                    logger.error(f"Bedrock model invocation failed: {e}")
                    return {"status": "UNKNOWN", "message": f"Bedrock error: {str(e)}"}
            
            def _parse_response(self, response: str) -> Dict[str, str]:
                """Parse Bedrock response to extract status and message."""
                import re
                import json
                
                if not response:
                    return {"status": "UNKNOWN", "message": "Empty response"}
                
                response = response.strip()
                valid_statuses = {"NEXT", "PREVIOUS", "EXIT", "HELP", "CARE", "HELLO", "UNKNOWN"}
                
                # Try JSON format
                try:
                    data = json.loads(response)
                    if isinstance(data, dict) and "status" in data:
                        status = data["status"].upper()
                        message = data.get("message", response)
                        if status in valid_statuses:
                            return {"status": status, "message": message}
                except:
                    pass
                
                # Try "STATUS: message" format
                match = re.match(r'^([A-Z]+)\s*:\s*(.+)$', response, re.DOTALL)
                if match:
                    status = match.group(1).upper()
                    message = match.group(2).strip()
                    if status in valid_statuses:
                        return {"status": status, "message": message}
                
                # Try first word as status
                words = response.split()
                if words:
                    first_word = words[0].upper().rstrip(':,.')
                    if first_word in valid_statuses:
                        message = ' '.join(words[1:]) if len(words) > 1 else response
                        return {"status": first_word, "message": message.strip()}
                
                return {"status": "UNKNOWN", "message": response}
            
            def is_available(self) -> bool:
                """Check if Bedrock model is available."""
                return True
        
        return BedrockLLMWrapper(bedrock_model)
    
    def process_message(self, message: Any) -> Any:
        """
        Process an incoming message (required by Agent base class).
        
        Args:
            message: The message to process (expected to be a dict with 'user_input' and optional 'task_context')
            
        Returns:
            Classification response
        """
        if isinstance(message, dict):
            user_input = message.get('user_input', '')
            task_context = message.get('task_context')
            return self.classify(user_input, task_context)
        elif isinstance(message, str):
            return self.classify(message)
        else:
            return self.handle_error(ValueError(f"Invalid message type: {type(message)}"))
    
    def classify(self, user_input: str, task_context: Optional[Dict] = None) -> Dict:
        """
        Classify user input and return status code with message.
        
        Args:
            user_input: User's text input
            task_context: Optional JSON task context with stages
            
        Returns:
            Dictionary with 'status' and 'message' keys
            
        Requirements: 1.2, 4.4, 7.2, 7.3, 8.3, 8.4
        """
        try:
            logger.info("Processing classification request")
            logger.debug(f"User input length: {len(user_input) if user_input else 0}")
            
            # Validate user input (Requirement 1.2)
            if not self.validator.validate_user_input(user_input):
                logger.warning("User input validation failed")
                return self.response_generator.generate_response(
                    "ERROR",
                    {"error_message": "Input cannot be empty or whitespace-only"}
                )
            
            # Validate task context if provided (Requirement 4.4)
            if task_context is not None:
                if not self.validator.validate_task_context(task_context):
                    logger.warning("Task context validation failed")
                    return self.response_generator.generate_response(
                        "ERROR",
                        {"error_message": "Invalid task context structure"}
                    )
            
            # Classify the intent
            try:
                status_code = self.engine.classify_intent(user_input, task_context)
                logger.info(f"Classification result: {status_code}")
                
                # Generate response for the classified status code
                return self.response_generator.generate_response(status_code)
                
            except Exception as classification_error:
                logger.error(f"Error during intent classification: {classification_error}", exc_info=True)
                return self.response_generator.generate_response(
                    "ERROR",
                    {"error_message": f"Classification error: {str(classification_error)}"}
                )
                
        except Exception as e:
            # Catch-all error handler - ensure we always return a valid JSON response
            logger.error(f"Unexpected error in classify method: {e}", exc_info=True)
            return self.response_generator.generate_response(
                "ERROR",
                {"error_message": f"An unexpected error occurred: {str(e)}"}
            )
