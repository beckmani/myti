"""Integration tests for StageManager agent."""

import pytest
from stage_manager.stage_manager import StageManager
from stage_manager.mcp_client import MCPClient


class TestEndToEndClassificationFlow:
    """Test end-to-end classification flow without task context."""
    
    def test_next_classification_flow(self):
        """Test complete flow for NEXT classification."""
        manager = StageManager()
        
        test_inputs = ["next", "continue", "proceed", "forward", "go on"]
        for user_input in test_inputs:
            result = manager.classify(user_input)
            assert result["status"] == "NEXT"
            assert "message" in result
            assert len(result["message"]) > 0
    
    def test_previous_classification_flow(self):
        """Test complete flow for PREVIOUS classification."""
        manager = StageManager()
        
        test_inputs = ["back", "previous", "return", "go back"]
        for user_input in test_inputs:
            result = manager.classify(user_input)
            assert result["status"] == "PREVIOUS"
            assert "message" in result
            assert len(result["message"]) > 0
    
    def test_exit_classification_flow(self):
        """Test complete flow for EXIT classification."""
        manager = StageManager()
        
        test_inputs = ["exit", "quit", "leave", "stop", "end"]
        for user_input in test_inputs:
            result = manager.classify(user_input)
            assert result["status"] == "EXIT"
            assert "message" in result
            assert len(result["message"]) > 0
    
    def test_help_classification_flow(self):
        """Test complete flow for HELP classification."""
        manager = StageManager()
        
        test_inputs = ["help", "assist", "support", "call"]
        for user_input in test_inputs:
            result = manager.classify(user_input)
            assert result["status"] == "HELP"
            assert "message" in result
            assert len(result["message"]) > 0
    
    def test_hello_classification_flow(self):
        """Test complete flow for HELLO classification."""
        manager = StageManager()
        
        test_inputs = ["hello", "hi", "hey", "greetings"]
        for user_input in test_inputs:
            result = manager.classify(user_input)
            assert result["status"] == "HELLO"
            assert "message" in result
            assert len(result["message"]) > 0
    
    def test_unknown_classification_flow(self):
        """Test complete flow for UNKNOWN classification."""
        manager = StageManager()
        
        test_inputs = ["banana", "xyz123", "random text"]
        for user_input in test_inputs:
            result = manager.classify(user_input)
            assert result["status"] == "UNKNOWN"
            assert "message" in result
            assert len(result["message"]) > 0
    
    def test_response_structure(self):
        """Test that all responses have correct structure."""
        manager = StageManager()
        
        result = manager.classify("next")
        
        # Verify response structure
        assert isinstance(result, dict)
        assert "status" in result
        assert "message" in result
        assert len(result) == 2  # Only status and message
        assert isinstance(result["status"], str)
        assert isinstance(result["message"], str)


class TestClassificationWithTaskContext:
    """Test classification with task context integration."""
    
    def test_classification_with_valid_context(self):
        """Test classification with valid task context."""
        manager = StageManager()
        
        task_context = {
            "task": "daily_routine",
            "description": "Complete daily tasks",
            "status": "in progress",
            "stages": [
                {"stage": "morning", "description": "Morning routine", "timeout": 3600},
                {"stage": "afternoon", "description": "Afternoon tasks", "timeout": 3600},
                {"stage": "evening", "description": "Evening routine", "timeout": 3600}
            ],
            "current_stage": "afternoon"
        }
        
        result = manager.classify("next", task_context)
        assert result["status"] == "NEXT"
        assert "message" in result
    
    def test_previous_at_first_stage(self):
        """Test PREVIOUS classification at first stage boundary."""
        manager = StageManager()
        
        task_context = {
            "task": "daily_routine",
            "description": "Complete daily tasks",
            "status": "in progress",
            "stages": [
                {"stage": "morning", "description": "Morning routine", "timeout": 3600},
                {"stage": "afternoon", "description": "Afternoon tasks", "timeout": 3600}
            ],
            "current_stage": "morning"
        }
        
        result = manager.classify("back", task_context)
        # Should return UNKNOWN at first stage
        assert result["status"] == "UNKNOWN"
    
    def test_next_at_last_stage(self):
        """Test NEXT classification at last stage boundary."""
        manager = StageManager()
        
        task_context = {
            "task": "daily_routine",
            "description": "Complete daily tasks",
            "status": "in progress",
            "stages": [
                {"stage": "morning", "description": "Morning routine", "timeout": 3600},
                {"stage": "evening", "description": "Evening routine", "timeout": 3600}
            ],
            "current_stage": "evening"
        }
        
        result = manager.classify("next", task_context)
        # Should return UNKNOWN at last stage
        assert result["status"] == "UNKNOWN"
    
    def test_stage_extraction_from_input(self):
        """Test that stage information is extracted from user input."""
        manager = StageManager()
        
        task_context = {
            "task": "daily_routine",
            "description": "Complete daily tasks",
            "status": "in progress",
            "stages": [
                {"stage": "morning", "description": "Morning routine", "timeout": 3600},
                {"stage": "afternoon", "description": "Afternoon tasks", "timeout": 3600}
            ],
            "current_stage": "afternoon"
        }
        
        # User input specifies they're at morning stage
        result = manager.classify("at stage morning, go back", task_context)
        # Should recognize they're at first stage and return UNKNOWN
        assert result["status"] == "UNKNOWN"
    
    def test_classification_without_context(self):
        """Test that classification works without task context."""
        manager = StageManager()
        
        # Should work fine without context
        result = manager.classify("next")
        assert result["status"] == "NEXT"
        
        result = manager.classify("back")
        assert result["status"] == "PREVIOUS"
    
    def test_multiple_stages_navigation(self):
        """Test navigation through multiple stages."""
        manager = StageManager()
        
        task_context = {
            "task": "workout",
            "description": "Complete workout routine",
            "status": "in progress",
            "stages": [
                {"stage": "warmup", "description": "Warm up exercises", "timeout": 600},
                {"stage": "cardio", "description": "Cardio exercises", "timeout": 1800},
                {"stage": "strength", "description": "Strength training", "timeout": 1800},
                {"stage": "cooldown", "description": "Cool down", "timeout": 600}
            ],
            "current_stage": "cardio"
        }
        
        # At middle stage, both NEXT and PREVIOUS should work
        result = manager.classify("next", task_context)
        assert result["status"] == "NEXT"
        
        result = manager.classify("back", task_context)
        assert result["status"] == "PREVIOUS"


class TestErrorHandlingAcrossComponents:
    """Test error handling across all components."""
    
    def test_empty_input_error(self):
        """Test error handling for empty input."""
        manager = StageManager()
        
        result = manager.classify("")
        assert result["status"] == "ERROR"
        assert "empty" in result["message"].lower() or "whitespace" in result["message"].lower()
    
    def test_whitespace_only_input_error(self):
        """Test error handling for whitespace-only input."""
        manager = StageManager()
        
        test_inputs = ["   ", "\t", "\n", "  \t\n  "]
        for user_input in test_inputs:
            result = manager.classify(user_input)
            assert result["status"] == "ERROR"
            assert "empty" in result["message"].lower() or "whitespace" in result["message"].lower()
    
    def test_invalid_task_context_error(self):
        """Test error handling for invalid task context."""
        manager = StageManager()
        
        # Missing required fields
        invalid_contexts = [
            {"task": "test"},  # Missing description, status, stages
            {"task": "test", "description": "desc"},  # Missing status, stages
            {"task": "test", "description": "desc", "status": "active"},  # Missing stages
            {"task": "test", "description": "desc", "status": "active", "stages": "not_a_list"},  # Invalid stages
        ]
        
        for invalid_context in invalid_contexts:
            result = manager.classify("next", invalid_context)
            assert result["status"] == "ERROR"
            assert "invalid" in result["message"].lower() or "context" in result["message"].lower()
    
    def test_malformed_stage_structure_error(self):
        """Test error handling for malformed stage structure."""
        manager = StageManager()
        
        task_context = {
            "task": "test",
            "description": "Test task",
            "status": "active",
            "stages": [
                {"stage": "step1"},  # Missing description and timeout
            ]
        }
        
        result = manager.classify("next", task_context)
        assert result["status"] == "ERROR"
    
    def test_unicode_input_handling(self):
        """Test that unicode input is handled correctly."""
        manager = StageManager()
        
        unicode_inputs = [
            "next 你好",
            "помощь help",
            "🚀 proceed",
            "café next"
        ]
        
        for user_input in unicode_inputs:
            result = manager.classify(user_input)
            # Should not crash, should return valid response
            assert "status" in result
            assert "message" in result
    
    def test_special_characters_handling(self):
        """Test that special characters are handled correctly."""
        manager = StageManager()
        
        special_inputs = [
            "next!",
            "help???",
            "back...",
            "exit@#$%"
        ]
        
        for user_input in special_inputs:
            result = manager.classify(user_input)
            # Should not crash, should return valid response
            assert "status" in result
            assert "message" in result
    
    def test_very_long_input_handling(self):
        """Test handling of very long input strings."""
        manager = StageManager()
        
        long_input = "next " * 1000  # Very long input
        result = manager.classify(long_input)
        
        # Should handle gracefully
        assert "status" in result
        assert "message" in result
    
    def test_configuration_error_fallback(self):
        """Test that invalid configuration falls back to defaults."""
        # Invalid configuration
        invalid_config = {
            "classification_rules": "not_a_dict"
        }
        
        manager = StageManager(config=invalid_config)
        
        # Should still work with defaults
        result = manager.classify("next")
        assert result["status"] == "NEXT"
    
    def test_custom_configuration_integration(self):
        """Test integration with custom configuration."""
        custom_config = {
            "classification_rules": {
                "NEXT": ["next", "continue", "forward"],
                "PREVIOUS": ["back", "previous"],
                "EXIT": ["exit", "quit"],
                "HELP": ["help"],
                "CARE": ["worried", "anxious"],
                "HELLO": ["hello", "hi"]
            }
        }
        
        manager = StageManager(config=custom_config)
        
        # Test that custom rules work
        result = manager.classify("forward")
        assert result["status"] == "NEXT"
        
        result = manager.classify("worried")
        assert result["status"] == "CARE"


class TestCAREFlowIntegration:
    """Test CARE detection and MCP integration."""
    
    def test_care_with_connected_mcp_client(self):
        """Test CARE flow when MCP client is connected."""
        # Create MCP client and manually set it as connected
        # (simulating a successful connection without needing a real server)
        mcp_client = MCPClient(server_url="http://localhost:8080")
        mcp_client._connected = True  # Simulate successful connection
        
        # Mock the call_caregiver method to return success
        original_call_caregiver = mcp_client.call_caregiver
        mcp_client.call_caregiver = lambda user_input, task_context: True
        
        # Create StageManager with MCP client
        manager = StageManager(mcp_client=mcp_client)
        
        # Classify CARE input
        result = manager.classify("I'm worried about this")
        
        # Restore original method
        mcp_client.call_caregiver = original_call_caregiver
        
        # Verify response
        assert result["status"] == "CARE"
        assert "caregiver" in result["message"].lower()
        assert "notified" in result["message"].lower()
    
    def test_care_without_mcp_client(self):
        """Test CARE flow when MCP client is not configured."""
        # Create StageManager without MCP client
        manager = StageManager()
        
        # Classify CARE input
        result = manager.classify("I'm anxious")
        
        # Verify response - should still return CARE but indicate failure
        assert result["status"] == "CARE"
        assert "couldn't reach" in result["message"].lower() or "support" in result["message"].lower()
    
    def test_care_with_disconnected_mcp_client(self):
        """Test CARE flow when MCP client is not connected."""
        # Create MCP client with valid URL but don't connect
        mcp_client = MCPClient(server_url="http://localhost:9999")
        # Explicitly set to disconnected state without calling connect()
        mcp_client._connected = False
        
        # Create StageManager with disconnected MCP client
        manager = StageManager(mcp_client=mcp_client)
        
        # Classify CARE input
        result = manager.classify("I'm scared")
        
        # Verify response - should return CARE but indicate failure
        assert result["status"] == "CARE"
        assert "couldn't reach" in result["message"].lower() or "support" in result["message"].lower()
    
    def test_care_with_task_context(self):
        """Test CARE flow with task context provided."""
        # Create MCP client and connect
        mcp_client = MCPClient(server_url="http://localhost:8080")
        mcp_client.connect()
        
        # Create StageManager with MCP client
        manager = StageManager(mcp_client=mcp_client)
        
        # Create task context
        task_context = {
            "task": "daily_routine",
            "description": "Complete daily tasks",
            "status": "in progress",
            "stages": [
                {"stage": "morning", "description": "Morning routine", "timeout": 3600},
                {"stage": "afternoon", "description": "Afternoon tasks", "timeout": 3600}
            ],
            "current_stage": "morning"
        }
        
        # Classify CARE input with context
        result = manager.classify("I'm concerned about this task", task_context)
        
        # Verify response
        assert result["status"] == "CARE"
        assert "caregiver" in result["message"].lower()
    
    def test_non_care_status_does_not_trigger_mcp(self):
        """Test that non-CARE statuses don't trigger MCP calls."""
        # Create MCP client and connect
        mcp_client = MCPClient(server_url="http://localhost:8080")
        mcp_client.connect()
        
        # Create StageManager with MCP client
        manager = StageManager(mcp_client=mcp_client)
        
        # Test various non-CARE inputs
        test_cases = [
            ("next", "NEXT"),
            ("go back", "PREVIOUS"),
            ("quit", "EXIT"),
            ("help me", "HELP"),
            ("hello", "HELLO"),
            ("banana", "UNKNOWN")
        ]
        
        for user_input, expected_status in test_cases:
            result = manager.classify(user_input)
            assert result["status"] == expected_status
            # Verify message doesn't mention caregiver
            assert "caregiver" not in result["message"].lower()
    
    def test_care_with_mcp_config_in_config_dict(self):
        """Test CARE flow when MCP is configured via config dictionary."""
        # Create config with MCP server settings and classification rules
        config = {
            "classification_rules": {
                "NEXT": ["next", "continue", "proceed", "forward", "go on"],
                "PREVIOUS": ["back", "previous", "return", "go back"],
                "EXIT": ["exit", "quit", "leave", "stop", "end"],
                "HELP": ["help", "assist", "support", "call"],
                "CARE": ["worried", "anxious", "scared", "concerned", "upset"],
                "HELLO": ["hello", "hi", "hey", "greetings"]
            },
            "mcp_server": {
                "url": "http://localhost:8080",
                "timeout": 30
            }
        }
        
        # Create StageManager with config
        manager = StageManager(config=config)
        
        # Classify CARE input
        result = manager.classify("I'm upset")
        
        # Verify response
        assert result["status"] == "CARE"
        # Should have attempted to notify caregiver
        assert "caregiver" in result["message"].lower()
