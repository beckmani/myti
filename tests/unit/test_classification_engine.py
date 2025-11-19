"""Unit tests for ClassificationEngine."""

import pytest
from stage_manager.classification_engine import ClassificationEngine


class TestClassificationEngineBasic:
    """Unit tests for basic classification functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = ClassificationEngine()
    
    def test_next_classification_next(self):
        """Test NEXT classification with 'next'."""
        result = self.engine.classify_intent("next")
        assert result == "NEXT"
    
    def test_next_classification_continue(self):
        """Test NEXT classification with 'continue'."""
        result = self.engine.classify_intent("continue")
        assert result == "NEXT"
    
    def test_next_classification_proceed(self):
        """Test NEXT classification with 'proceed'."""
        result = self.engine.classify_intent("proceed")
        assert result == "NEXT"
    
    def test_previous_classification_back(self):
        """Test PREVIOUS classification with 'back'."""
        result = self.engine.classify_intent("back")
        assert result == "PREVIOUS"
    
    def test_previous_classification_previous(self):
        """Test PREVIOUS classification with 'previous'."""
        result = self.engine.classify_intent("previous")
        assert result == "PREVIOUS"
    
    def test_exit_classification_quit(self):
        """Test EXIT classification with 'quit'."""
        result = self.engine.classify_intent("quit")
        assert result == "EXIT"
    
    def test_exit_classification_exit(self):
        """Test EXIT classification with 'exit'."""
        result = self.engine.classify_intent("exit")
        assert result == "EXIT"
    
    def test_help_classification_help(self):
        """Test HELP classification with 'help'."""
        result = self.engine.classify_intent("help")
        assert result == "HELP"
    
    def test_help_classification_call_my_mom(self):
        """Test HELP classification with 'call my mom'."""
        result = self.engine.classify_intent("call my mom")
        assert result == "HELP"
    
    def test_care_classification_worried(self):
        """Test CARE classification with 'worried'."""
        result = self.engine.classify_intent("worried")
        assert result == "CARE"
    
    def test_care_classification_anxious(self):
        """Test CARE classification with 'anxious'."""
        result = self.engine.classify_intent("anxious")
        assert result == "CARE"
    
    def test_hello_classification_hello(self):
        """Test HELLO classification with 'hello'."""
        result = self.engine.classify_intent("hello")
        assert result == "HELLO"
    
    def test_hello_classification_hi(self):
        """Test HELLO classification with 'hi'."""
        result = self.engine.classify_intent("hi")
        assert result == "HELLO"
    
    def test_unknown_classification_banana(self):
        """Test UNKNOWN classification with 'banana'."""
        result = self.engine.classify_intent("banana")
        assert result == "UNKNOWN"
    
    def test_unknown_classification_maybe_ill_eat(self):
        """Test UNKNOWN classification with 'maybe I'll eat'."""
        result = self.engine.classify_intent("maybe I'll eat")
        assert result == "UNKNOWN"


class TestClassificationEngineConfiguration:
    """Unit tests for classification engine configuration."""
    
    def test_initialization_with_default_config(self):
        """Test initialization without configuration uses defaults."""
        engine = ClassificationEngine()
        
        assert engine.config is not None
        assert "classification_rules" in engine.config
        assert "NEXT" in engine.classification_rules
        assert "PREVIOUS" in engine.classification_rules
        assert "EXIT" in engine.classification_rules
        assert "HELP" in engine.classification_rules
        assert "CARE" in engine.classification_rules
        assert "HELLO" in engine.classification_rules
    
    def test_initialization_with_custom_config(self):
        """Test initialization with custom configuration."""
        custom_config = {
            "classification_rules": {
                "NEXT": ["forward", "onward"],
                "EXIT": ["bye", "goodbye"]
            }
        }
        
        engine = ClassificationEngine(config=custom_config)
        
        assert engine.config == custom_config
        assert engine.classification_rules["NEXT"] == ["forward", "onward"]
        assert engine.classification_rules["EXIT"] == ["bye", "goodbye"]
    
    def test_custom_patterns_classification(self):
        """Test classification with custom patterns."""
        custom_config = {
            "classification_rules": {
                "NEXT": ["forward", "onward"],
                "EXIT": ["bye"]
            }
        }
        
        engine = ClassificationEngine(config=custom_config)
        
        assert engine.classify_intent("forward") == "NEXT"
        assert engine.classify_intent("onward") == "NEXT"
        assert engine.classify_intent("bye") == "EXIT"
        assert engine.classify_intent("next") == "UNKNOWN"  # Default pattern not in custom config


class TestClassificationEngineStageExtraction:
    """Unit tests for stage extraction functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = ClassificationEngine()
    
    def test_extract_stage_from_input_with_at(self):
        """Test extracting stage from input with 'at stage X'."""
        result = self.engine.extract_stage_info("I'm at stage 2")
        assert result == "2"
    
    def test_extract_stage_from_input_without_at(self):
        """Test extracting stage from input with 'stage X'."""
        result = self.engine.extract_stage_info("stage 3 is difficult")
        assert result == "3"
    
    def test_extract_stage_from_context(self):
        """Test extracting stage from task context."""
        task_context = {
            "current_stage": "Stage 1"
        }
        
        result = self.engine.extract_stage_info("help me", task_context)
        assert result == "Stage 1"
    
    def test_extract_stage_input_priority_over_context(self):
        """Test that input stage takes priority over context stage."""
        task_context = {
            "current_stage": "Stage 1"
        }
        
        result = self.engine.extract_stage_info("I'm at stage 2", task_context)
        assert result == "2"
    
    def test_extract_stage_no_stage_info(self):
        """Test extracting stage when no stage info is available."""
        result = self.engine.extract_stage_info("help me")
        assert result is None


class TestClassificationEngineStageBoundaries:
    """Unit tests for stage boundary awareness."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = ClassificationEngine()
    
    def test_is_at_first_stage_true(self):
        """Test is_at_first_stage returns True for first stage."""
        task_context = {
            "stages": [
                {"stage": "Stage 1", "description": "First", "timeout": 300},
                {"stage": "Stage 2", "description": "Second", "timeout": 300}
            ]
        }
        
        result = self.engine.is_at_first_stage(task_context, "Stage 1")
        assert result is True
    
    def test_is_at_first_stage_false(self):
        """Test is_at_first_stage returns False for non-first stage."""
        task_context = {
            "stages": [
                {"stage": "Stage 1", "description": "First", "timeout": 300},
                {"stage": "Stage 2", "description": "Second", "timeout": 300}
            ]
        }
        
        result = self.engine.is_at_first_stage(task_context, "Stage 2")
        assert result is False
    
    def test_is_at_first_stage_empty_stages(self):
        """Test is_at_first_stage with empty stages."""
        task_context = {"stages": []}
        
        result = self.engine.is_at_first_stage(task_context, "Stage 1")
        assert result is False
    
    def test_is_at_first_stage_no_stages_key(self):
        """Test is_at_first_stage with no stages key."""
        task_context = {}
        
        result = self.engine.is_at_first_stage(task_context, "Stage 1")
        assert result is False
    
    def test_is_at_last_stage_true(self):
        """Test is_at_last_stage returns True for last stage."""
        task_context = {
            "stages": [
                {"stage": "Stage 1", "description": "First", "timeout": 300},
                {"stage": "Stage 2", "description": "Second", "timeout": 300}
            ]
        }
        
        result = self.engine.is_at_last_stage(task_context, "Stage 2")
        assert result is True
    
    def test_is_at_last_stage_false(self):
        """Test is_at_last_stage returns False for non-last stage."""
        task_context = {
            "stages": [
                {"stage": "Stage 1", "description": "First", "timeout": 300},
                {"stage": "Stage 2", "description": "Second", "timeout": 300}
            ]
        }
        
        result = self.engine.is_at_last_stage(task_context, "Stage 1")
        assert result is False
    
    def test_is_at_last_stage_empty_stages(self):
        """Test is_at_last_stage with empty stages."""
        task_context = {"stages": []}
        
        result = self.engine.is_at_last_stage(task_context, "Stage 2")
        assert result is False
    
    def test_is_at_last_stage_no_stages_key(self):
        """Test is_at_last_stage with no stages key."""
        task_context = {}
        
        result = self.engine.is_at_last_stage(task_context, "Stage 2")
        assert result is False


class TestClassificationEngineContextAware:
    """Unit tests for context-aware classification."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = ClassificationEngine()
    
    def test_previous_at_first_stage_boundary(self):
        """Test PREVIOUS at first stage returns UNKNOWN."""
        task_context = {
            "current_stage": "Stage 1",
            "stages": [
                {"stage": "Stage 1", "description": "First", "timeout": 300},
                {"stage": "Stage 2", "description": "Second", "timeout": 300},
                {"stage": "Stage 3", "description": "Third", "timeout": 300}
            ]
        }
        
        result = self.engine.classify_intent("go back", task_context)
        assert result == "UNKNOWN"
    
    def test_next_at_last_stage_boundary(self):
        """Test NEXT at last stage returns UNKNOWN."""
        task_context = {
            "current_stage": "Stage 3",
            "stages": [
                {"stage": "Stage 1", "description": "First", "timeout": 300},
                {"stage": "Stage 2", "description": "Second", "timeout": 300},
                {"stage": "Stage 3", "description": "Third", "timeout": 300}
            ]
        }
        
        result = self.engine.classify_intent("next", task_context)
        assert result == "UNKNOWN"
    
    def test_previous_at_middle_stage_allowed(self):
        """Test PREVIOUS at middle stage is allowed."""
        task_context = {
            "current_stage": "Stage 2",
            "stages": [
                {"stage": "Stage 1", "description": "First", "timeout": 300},
                {"stage": "Stage 2", "description": "Second", "timeout": 300},
                {"stage": "Stage 3", "description": "Third", "timeout": 300}
            ]
        }
        
        result = self.engine.classify_intent("go back", task_context)
        assert result == "PREVIOUS"
    
    def test_next_at_middle_stage_allowed(self):
        """Test NEXT at middle stage is allowed."""
        task_context = {
            "current_stage": "Stage 2",
            "stages": [
                {"stage": "Stage 1", "description": "First", "timeout": 300},
                {"stage": "Stage 2", "description": "Second", "timeout": 300},
                {"stage": "Stage 3", "description": "Third", "timeout": 300}
            ]
        }
        
        result = self.engine.classify_intent("next", task_context)
        assert result == "NEXT"
    
    def test_stage_extraction_from_input_overrides_context(self):
        """Test that stage from input takes priority over context."""
        task_context = {
            "current_stage": "Stage 1",
            "stages": [
                {"stage": "Stage 1", "description": "First", "timeout": 300},
                {"stage": "Stage 2", "description": "Second", "timeout": 300},
                {"stage": "Stage 3", "description": "Third", "timeout": 300}
            ]
        }
        
        # User says they're at stage 2, even though context says stage 1
        result = self.engine.classify_intent("I'm at stage 2, go back", task_context)
        assert result == "PREVIOUS"  # Should be allowed since stage 2 is not first
    
    def test_fallback_to_context_stage_when_no_input_stage(self):
        """Test fallback to context stage when input has no stage."""
        task_context = {
            "current_stage": "Stage 1",
            "stages": [
                {"stage": "Stage 1", "description": "First", "timeout": 300},
                {"stage": "Stage 2", "description": "Second", "timeout": 300}
            ]
        }
        
        result = self.engine.classify_intent("previous", task_context)
        assert result == "UNKNOWN"  # Should use context stage (Stage 1) and block PREVIOUS
    
    def test_classification_without_context(self):
        """Test classification works without task context."""
        result = self.engine.classify_intent("next")
        assert result == "NEXT"
        
        result = self.engine.classify_intent("previous")
        assert result == "PREVIOUS"
