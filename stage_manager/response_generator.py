"""Response generation module for StageManager."""

from typing import Dict, Optional


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
        messages = {
            "NEXT": "Moving forward to the next stage.",
            "PREVIOUS": "Going back to the previous stage.",
            "EXIT": "Exiting the task flow.",
            "HELP": "Help is on the way. What do you need assistance with?",
            "CARE": "I understand you need support. A caregiver has been notified.",
            "HELLO": "Hello! How can I help you today?",
            "UNKNOWN": "I'm not sure what you mean. Could you rephrase that?",
            "ERROR": "An error occurred while processing your request."
        }
        
        message = messages.get(status_code, messages["UNKNOWN"])
        
        # Customize message based on context if provided
        if context:
            if status_code == "CARE" and context.get("mcp_failed"):
                message = "I understand you need support, but I couldn't reach the caregiver service."
            elif status_code == "ERROR" and "error_message" in context:
                message = context["error_message"]
        
        return {
            "status": status_code,
            "message": message
        }
