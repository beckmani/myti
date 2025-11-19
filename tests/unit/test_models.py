"""Unit tests for data models."""

import pytest
import json
from stage_manager.models import Stage, TaskContext, ClassificationResponse


class TestStage:
    """Unit tests for Stage dataclass."""
    
    def test_stage_creation(self):
        """Test creating a valid Stage object."""
        stage = Stage(
            stage="Stage 1",
            description="First stage of the task",
            timeout=300
        )
        
        assert stage.stage == "Stage 1"
        assert stage.description == "First stage of the task"
        assert stage.timeout == 300
    
    def test_stage_validation_valid(self):
        """Test validation of a valid Stage."""
        stage = Stage(
            stage="Stage 1",
            description="First stage",
            timeout=300
        )
        
        assert stage.validate() is True
    
    def test_stage_validation_empty_name(self):
        """Test validation fails for empty stage name."""
        stage = Stage(
            stage="",
            description="First stage",
            timeout=300
        )
        
        assert stage.validate() is False
    
    def test_stage_validation_negative_timeout(self):
        """Test validation fails for negative timeout."""
        stage = Stage(
            stage="Stage 1",
            description="First stage",
            timeout=-10
        )
        
        assert stage.validate() is False
    
    def test_stage_to_dict(self):
        """Test converting Stage to dictionary."""
        stage = Stage(
            stage="Stage 1",
            description="First stage",
            timeout=300
        )
        
        stage_dict = stage.to_dict()
        
        assert isinstance(stage_dict, dict)
        assert stage_dict["stage"] == "Stage 1"
        assert stage_dict["description"] == "First stage"
        assert stage_dict["timeout"] == 300


class TestTaskContext:
    """Unit tests for TaskContext dataclass."""
    
    def test_task_context_creation(self):
        """Test creating a valid TaskContext object."""
        stages = [
            Stage(stage="Stage 1", description="First stage", timeout=300),
            Stage(stage="Stage 2", description="Second stage", timeout=600)
        ]
        
        task_context = TaskContext(
            task="Sample Task",
            description="A sample task for testing",
            status="in progress",
            stages=stages
        )
        
        assert task_context.task == "Sample Task"
        assert task_context.description == "A sample task for testing"
        assert task_context.status == "in progress"
        assert len(task_context.stages) == 2
        assert task_context.stages[0].stage == "Stage 1"
    
    def test_task_context_validation_valid(self):
        """Test validation of a valid TaskContext."""
        stages = [
            Stage(stage="Stage 1", description="First stage", timeout=300)
        ]
        
        task_context = TaskContext(
            task="Sample Task",
            description="A sample task",
            status="not started",
            stages=stages
        )
        
        assert task_context.validate() is True
    
    def test_task_context_validation_empty_task_name(self):
        """Test validation fails for empty task name."""
        task_context = TaskContext(
            task="",
            description="A sample task",
            status="not started",
            stages=[]
        )
        
        assert task_context.validate() is False
    
    def test_task_context_validation_empty_status(self):
        """Test validation fails for empty status."""
        task_context = TaskContext(
            task="Sample Task",
            description="A sample task",
            status="",
            stages=[]
        )
        
        assert task_context.validate() is False
    
    def test_task_context_validation_invalid_stage(self):
        """Test validation fails when a stage is invalid."""
        stages = [
            Stage(stage="", description="Invalid stage", timeout=300)
        ]
        
        task_context = TaskContext(
            task="Sample Task",
            description="A sample task",
            status="in progress",
            stages=stages
        )
        
        assert task_context.validate() is False
    
    def test_task_context_to_dict(self):
        """Test converting TaskContext to dictionary."""
        stages = [
            Stage(stage="Stage 1", description="First stage", timeout=300),
            Stage(stage="Stage 2", description="Second stage", timeout=600)
        ]
        
        task_context = TaskContext(
            task="Sample Task",
            description="A sample task",
            status="in progress",
            stages=stages
        )
        
        context_dict = task_context.to_dict()
        
        assert isinstance(context_dict, dict)
        assert context_dict["task"] == "Sample Task"
        assert context_dict["description"] == "A sample task"
        assert context_dict["status"] == "in progress"
        assert len(context_dict["stages"]) == 2
        assert context_dict["stages"][0]["stage"] == "Stage 1"
    
    def test_task_context_from_dict_valid(self):
        """Test creating TaskContext from valid dictionary."""
        data = {
            "task": "Sample Task",
            "description": "A sample task",
            "status": "in progress",
            "stages": [
                {"stage": "Stage 1", "description": "First stage", "timeout": 300},
                {"stage": "Stage 2", "description": "Second stage", "timeout": 600}
            ]
        }
        
        task_context = TaskContext.from_dict(data)
        
        assert task_context is not None
        assert task_context.task == "Sample Task"
        assert task_context.description == "A sample task"
        assert task_context.status == "in progress"
        assert len(task_context.stages) == 2
        assert task_context.stages[0].stage == "Stage 1"
        assert task_context.stages[1].timeout == 600
    
    def test_task_context_from_dict_missing_field(self):
        """Test creating TaskContext from dictionary with missing field."""
        data = {
            "task": "Sample Task",
            "description": "A sample task",
            # Missing "status" field
            "stages": []
        }
        
        task_context = TaskContext.from_dict(data)
        
        assert task_context is None
    
    def test_task_context_from_dict_invalid_stage(self):
        """Test creating TaskContext from dictionary with invalid stage."""
        data = {
            "task": "Sample Task",
            "description": "A sample task",
            "status": "in progress",
            "stages": [
                {"stage": "Stage 1", "description": "First stage"}  # Missing timeout
            ]
        }
        
        task_context = TaskContext.from_dict(data)
        
        assert task_context is None


class TestClassificationResponse:
    """Unit tests for ClassificationResponse dataclass."""
    
    def test_classification_response_creation(self):
        """Test creating a valid ClassificationResponse object."""
        response = ClassificationResponse(
            status="NEXT",
            message="Proceeding to the next stage"
        )
        
        assert response.status == "NEXT"
        assert response.message == "Proceeding to the next stage"
    
    def test_classification_response_validation_valid(self):
        """Test validation of valid ClassificationResponse."""
        response = ClassificationResponse(
            status="HELP",
            message="How can I assist you?"
        )
        
        assert response.validate() is True
    
    def test_classification_response_validation_invalid_status(self):
        """Test validation fails for invalid status code."""
        response = ClassificationResponse(
            status="INVALID",
            message="This should fail"
        )
        
        assert response.validate() is False
    
    def test_classification_response_validation_empty_message(self):
        """Test validation fails for empty message."""
        response = ClassificationResponse(
            status="NEXT",
            message=""
        )
        
        assert response.validate() is False
    
    def test_classification_response_to_dict(self):
        """Test converting ClassificationResponse to dictionary."""
        response = ClassificationResponse(
            status="EXIT",
            message="Exiting the task"
        )
        
        response_dict = response.to_dict()
        
        assert isinstance(response_dict, dict)
        assert response_dict["status"] == "EXIT"
        assert response_dict["message"] == "Exiting the task"
    
    def test_classification_response_to_json(self):
        """Test serializing ClassificationResponse to JSON."""
        response = ClassificationResponse(
            status="CARE",
            message="I understand you need support"
        )
        
        json_str = response.to_json()
        
        assert isinstance(json_str, str)
        
        # Parse back to verify it's valid JSON
        parsed = json.loads(json_str)
        assert parsed["status"] == "CARE"
        assert parsed["message"] == "I understand you need support"
    
    def test_classification_response_from_dict_valid(self):
        """Test creating ClassificationResponse from valid dictionary."""
        data = {
            "status": "HELLO",
            "message": "Hello! How can I help you today?"
        }
        
        response = ClassificationResponse.from_dict(data)
        
        assert response is not None
        assert response.status == "HELLO"
        assert response.message == "Hello! How can I help you today?"
    
    def test_classification_response_from_dict_missing_field(self):
        """Test creating ClassificationResponse from dictionary with missing field."""
        data = {
            "status": "NEXT"
            # Missing "message" field
        }
        
        response = ClassificationResponse.from_dict(data)
        
        assert response is None
    
    def test_classification_response_all_valid_statuses(self):
        """Test all valid status codes."""
        valid_statuses = ["NEXT", "PREVIOUS", "EXIT", "HELP", "CARE", "HELLO", "UNKNOWN", "ERROR"]
        
        for status in valid_statuses:
            response = ClassificationResponse(
                status=status,
                message=f"Testing {status}"
            )
            assert response.validate() is True
