"""Main StageManager agent implementation."""

import logging
from typing import Dict, Optional

from .input_validator import InputValidator
from .classification_engine import ClassificationEngine
from .response_generator import ResponseGenerator
from .mcp_client import MCPClient


logger = logging.getLogger(__name__)


class StageManager:
    """
    Main classifier agent for task stage navigation.
    
    The StageManager classifies user text input into status codes
    (NEXT, PREVIOUS, EXIT, HELP, CARE, HELLO, UNKNOWN) to help users
    navigate through multi-stage tasks.
    """
    
    def __init__(self, config: Optional[Dict] = None, mcp_client: Optional[MCPClient] = None):
        """
        Initialize the StageManager agent.
        
        Args:
            config: Optional configuration dictionary for classification rules
            mcp_client: Optional MCP client for caregiver service integration
        """
        self.config = config or {}
        self.validator = InputValidator()
        self.engine = ClassificationEngine(config)
        self.response_generator = ResponseGenerator()
        
        # Initialize MCP client
        self.mcp_client = mcp_client
        if self.mcp_client is None and "mcp_server" in self.config:
            mcp_config = self.config["mcp_server"]
            self.mcp_client = MCPClient(
                server_url=mcp_config.get("url", "http://localhost:8080"),
                timeout=mcp_config.get("timeout", 30)
            )
            # Try to connect, but don't fail if connection fails
            if not self.mcp_client.connect():
                logger.warning("MCP server unavailable during initialization")
    
    def classify(self, user_input: str, task_context: Optional[Dict] = None) -> Dict:
        """
        Classify user input and return status code with message.
        
        Args:
            user_input: User's text input
            task_context: Optional JSON task context with stages
            
        Returns:
            Dictionary with 'status' and 'message' keys
            
        Raises:
            ValueError: If input is invalid
        """
        # Validate user input
        if not self.validator.validate_user_input(user_input):
            return self.response_generator.generate_response(
                "ERROR",
                {"error_message": "Input cannot be empty or whitespace-only"}
            )
        
        # Validate task context if provided
        if task_context is not None:
            if not self.validator.validate_task_context(task_context):
                return self.response_generator.generate_response(
                    "ERROR",
                    {"error_message": "Invalid task context structure"}
                )
        
        # Classify the intent
        try:
            status_code = self.engine.classify_intent(user_input, task_context)
            
            # Handle CARE status with MCP integration
            if status_code == "CARE":
                mcp_success = False
                if self.mcp_client and self.mcp_client.is_connected():
                    mcp_success = self.mcp_client.call_caregiver(user_input, task_context)
                
                context = {"mcp_failed": not mcp_success} if not mcp_success else None
                return self.response_generator.generate_response(status_code, context)
            
            # Generate response for other status codes
            return self.response_generator.generate_response(status_code)
            
        except Exception as e:
            logger.error(f"Error during classification: {e}")
            return self.response_generator.generate_response(
                "ERROR",
                {"error_message": f"Classification error: {str(e)}"}
            )
