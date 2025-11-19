"""Data models for StageManager."""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import json
import logging


logger = logging.getLogger(__name__)


@dataclass
class Stage:
    """
    Represents a stage within a task flow.
    
    Attributes:
        stage: Stage name/identifier
        description: Stage description
        timeout: Timeout in seconds for the stage
    """
    stage: str
    description: str
    timeout: int
    
    def validate(self) -> bool:
        """
        Validate the stage data.
        
        Returns:
            True if stage is valid, False otherwise
        """
        if not isinstance(self.stage, str) or not self.stage:
            logger.warning("Stage name must be a non-empty string")
            return False
        
        if not isinstance(self.description, str):
            logger.warning("Stage description must be a string")
            return False
        
        if not isinstance(self.timeout, (int, float)) or self.timeout < 0:
            logger.warning("Stage timeout must be a non-negative number")
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stage to dictionary."""
        return asdict(self)


@dataclass
class TaskContext:
    """
    Represents the context of a task with multiple stages.
    
    Attributes:
        task: Task name/identifier
        description: Task description
        status: Task status (e.g., "not started", "in progress", "completed")
        stages: List of Stage objects
    """
    task: str
    description: str
    status: str
    stages: List[Stage] = field(default_factory=list)
    
    def validate(self) -> bool:
        """
        Validate the task context data.
        
        Returns:
            True if task context is valid, False otherwise
        """
        if not isinstance(self.task, str) or not self.task:
            logger.warning("Task name must be a non-empty string")
            return False
        
        if not isinstance(self.description, str):
            logger.warning("Task description must be a string")
            return False
        
        if not isinstance(self.status, str) or not self.status:
            logger.warning("Task status must be a non-empty string")
            return False
        
        if not isinstance(self.stages, list):
            logger.warning("Stages must be a list")
            return False
        
        # Validate each stage
        for idx, stage in enumerate(self.stages):
            if not isinstance(stage, Stage):
                logger.warning(f"Stage at index {idx} is not a Stage object")
                return False
            
            if not stage.validate():
                logger.warning(f"Stage at index {idx} failed validation")
                return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task context to dictionary."""
        return {
            "task": self.task,
            "description": self.description,
            "status": self.status,
            "stages": [stage.to_dict() for stage in self.stages]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional['TaskContext']:
        """
        Create TaskContext from dictionary.
        
        Args:
            data: Dictionary containing task context data
            
        Returns:
            TaskContext object if successful, None if data is invalid
        """
        try:
            stages = [
                Stage(
                    stage=s["stage"],
                    description=s["description"],
                    timeout=s["timeout"]
                )
                for s in data.get("stages", [])
            ]
            
            return cls(
                task=data["task"],
                description=data["description"],
                status=data["status"],
                stages=stages
            )
        except (KeyError, TypeError) as e:
            logger.error(f"Failed to create TaskContext from dict: {e}")
            return None


@dataclass
class ClassificationResponse:
    """
    Represents the response from classification.
    
    Attributes:
        status: Status code (NEXT, PREVIOUS, EXIT, HELP, CARE, HELLO, UNKNOWN, ERROR)
        message: Free text message providing context or explanation
    """
    status: str
    message: str
    
    def validate(self) -> bool:
        """
        Validate the classification response.
        
        Returns:
            True if response is valid, False otherwise
        """
        valid_statuses = {"NEXT", "PREVIOUS", "EXIT", "HELP", "CARE", "HELLO", "UNKNOWN", "ERROR"}
        
        if not isinstance(self.status, str) or self.status not in valid_statuses:
            logger.warning(f"Invalid status code: {self.status}")
            return False
        
        if not isinstance(self.message, str) or not self.message:
            logger.warning("Message must be a non-empty string")
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, str]:
        """Convert response to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """
        Serialize response to JSON string.
        
        Returns:
            JSON string representation of the response
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> Optional['ClassificationResponse']:
        """
        Create ClassificationResponse from dictionary.
        
        Args:
            data: Dictionary containing status and message
            
        Returns:
            ClassificationResponse object if successful, None if data is invalid
        """
        try:
            return cls(
                status=data["status"],
                message=data["message"]
            )
        except (KeyError, TypeError) as e:
            logger.error(f"Failed to create ClassificationResponse from dict: {e}")
            return None
