"""Response generation module for StageManager."""

from typing import Dict, Optional
import logging


# Configure logger for this module
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class ResponseGenerator:
    """Generates JSON responses with status codes and contextual messages."""
    
    @staticmethod
    def generate_response(status_code: str, context: Optional[Dict] = None) -> Dict:
        """
        Generate JSON response with status code and message.
        
        Args:
            status_code: One of the seven status codes
            context: Optional context for generating appropriate message
            
        Returns:
            Dictionary with 'status' and 'message' keys
        """
        try:
            messages = {
                "NEXT": "Moving forward to the next stage.",
                "PREVIOUS": "Going back to the previous stage.",
                "EXIT": "Exiting the task flow.",
                "HELP": "Help is on the way. What do you need assistance with?",
                "CARE": "I understand you need support.",
                "HELLO": "Hello! How can I help you today?",
                "UNKNOWN": "I'm not sure what you mean. Could you rephrase that?",
                "ERROR": "An error occurred while processing your request."
            }
            
            # Validate status code
            if not status_code or not isinstance(status_code, str):
                logger.warning(f"Invalid status code: {status_code}, using UNKNOWN")
                status_code = "UNKNOWN"
            
            message = messages.get(status_code, messages["UNKNOWN"])
            
            # Customize message based on context if provided
            if context and isinstance(context, dict):
                if status_code == "ERROR" and "error_message" in context:
                    message = context["error_message"]
                    logger.info(f"Generated ERROR response: {message}")
            
            response = {
                "status": status_code,
                "message": message
            }
            
            logger.debug(f"Generated response for status {status_code}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            # Return a safe fallback response
            return {
                "status": "ERROR",
                "message": "An unexpected error occurred while generating the response."
            }
