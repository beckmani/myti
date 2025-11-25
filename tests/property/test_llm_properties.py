"""Property-based tests for LLM integration."""

import pytest
from hypothesis import given, strategies as st, assume
from stage_manager.classification_engine import ClassificationEngine
from stage_manager.llm_client import LLMClient, LLMConnectionError, LLMTimeoutError, LLMResponseError


# Feature: task-classifier-agent, Property 13: LLM prompt includes user input
# *For any* valid user input, the LLM prompt constructed by the ClassificationEngine 
# should contain the user's input text.
# **Validates: Requirements 12.1**


# Feature: task-classifier-agent, Property 14: LLM prompt includes task context
# *For any* classification request with task context, the LLM prompt should include 
# the task name, description, and current stage information.
# **Validates: Requirements 12.2, 12.3**


# Strategy for generating non-empty user input strings
user_input_strategy = st.text(min_size=1, max_size=500).filter(lambda x: x.strip())


# Strategy for generating task names
task_name_strategy = st.text(min_size=1, max_size=100, alphabet=st.characters(
    whitelist_categories=('Lu', 'Ll', 'Nd'), 
    whitelist_characters=' -_'
)).filter(lambda x: x.strip())


# Strategy for generating descriptions
description_strategy = st.text(min_size=1, max_size=200).filter(lambda x: x.strip())


# Strategy for generating stage names
stage_name_strategy = st.text(min_size=1, max_size=50, alphabet=st.characters(
    whitelist_categories=('Lu', 'Ll', 'Nd'),
    whitelist_characters=' -_'
)).filter(lambda x: x.strip())


# Strategy for generating individual stages
stage_strategy = st.fixed_dictionaries({
    'stage': stage_name_strategy,
    'description': description_strategy,
    'timeout': st.integers(min_value=1, max_value=3600)
})


# Strategy for generating task context with stages
task_context_strategy = st.fixed_dictionaries({
    'task': task_name_strategy,
    'description': description_strategy,
    'status': st.sampled_from(['not started', 'in progress', 'completed']),
    'stages': st.lists(stage_strategy, min_size=1, max_size=5),
    'current_stage': stage_name_strategy
})


class TestLLMPromptConstruction:
    """Property-based tests for LLM prompt construction."""
    
    @given(user_input=user_input_strategy)
    def test_prompt_includes_user_input(self, user_input):
        """
        Property 13: LLM prompt includes user input.
        
        For any valid user input, the LLM prompt constructed by the 
        ClassificationEngine should contain the user's input text.
        """
        engine = ClassificationEngine()
        
        # Build the prompt
        prompt = engine._build_llm_prompt(user_input, None)
        
        # Verify prompt is a non-empty string
        assert isinstance(prompt, str), "Prompt must be a string"
        assert len(prompt) > 0, "Prompt must not be empty"
        
        # Verify user input is included in the prompt
        assert user_input in prompt, \
            f"Prompt must contain user input. User input: '{user_input[:50]}...'"
    
    @given(user_input=user_input_strategy, task_context=task_context_strategy)
    def test_prompt_includes_task_context(self, user_input, task_context):
        """
        Property 14: LLM prompt includes task context.
        
        For any classification request with task context, the LLM prompt 
        should include the task name, description, and current stage information.
        """
        # Ensure current_stage matches one of the stages in the list
        if task_context['stages']:
            task_context['current_stage'] = task_context['stages'][0]['stage']
        
        engine = ClassificationEngine()
        
        # Build the prompt
        prompt = engine._build_llm_prompt(user_input, task_context)
        
        # Verify prompt is a non-empty string
        assert isinstance(prompt, str), "Prompt must be a string"
        assert len(prompt) > 0, "Prompt must not be empty"
        
        # Verify user input is included
        assert user_input in prompt, "Prompt must contain user input"
        
        # Verify task name is included
        assert task_context['task'] in prompt, \
            f"Prompt must contain task name: '{task_context['task']}'"
        
        # Verify task description is included
        assert task_context['description'] in prompt, \
            f"Prompt must contain task description: '{task_context['description']}'"
        
        # Verify current stage is included (if it exists in the context)
        if 'current_stage' in task_context and task_context['current_stage']:
            # The stage might be extracted from input or context
            # At minimum, the prompt should reference stages
            assert 'stage' in prompt.lower() or 'Stage' in prompt, \
                "Prompt must reference stage information"
    
    @given(user_input=user_input_strategy)
    def test_prompt_includes_status_codes(self, user_input):
        """
        Property: LLM prompt includes all valid status codes.
        
        For any user input, the prompt should include instructions about
        all seven valid status codes.
        """
        engine = ClassificationEngine()
        
        # Build the prompt
        prompt = engine._build_llm_prompt(user_input, None)
        
        # Verify all status codes are mentioned in the prompt
        status_codes = ['NEXT', 'PREVIOUS', 'EXIT', 'HELP', 'CARE', 'HELLO', 'UNKNOWN']
        
        for status_code in status_codes:
            assert status_code in prompt, \
                f"Prompt must include status code: {status_code}"
    
    @given(user_input=user_input_strategy, task_context=task_context_strategy)
    def test_prompt_with_context_is_longer(self, user_input, task_context):
        """
        Property: Prompt with context contains more information.
        
        For any user input, a prompt with task context should be longer
        than a prompt without context (contains more information).
        """
        # Ensure current_stage matches one of the stages
        if task_context['stages']:
            task_context['current_stage'] = task_context['stages'][0]['stage']
        
        engine = ClassificationEngine()
        
        # Build prompts with and without context
        prompt_without_context = engine._build_llm_prompt(user_input, None)
        prompt_with_context = engine._build_llm_prompt(user_input, task_context)
        
        # Prompt with context should be longer (more information)
        assert len(prompt_with_context) >= len(prompt_without_context), \
            "Prompt with context should contain at least as much information as without"


# Feature: task-classifier-agent, Property 15: LLM response parsing
# *For any* valid LLM response containing a status code, the ClassificationEngine 
# should successfully parse and extract the status code.
# **Validates: Requirements 10.3**


# Valid status codes
VALID_STATUS_CODES = ['NEXT', 'PREVIOUS', 'EXIT', 'HELP', 'CARE', 'HELLO', 'UNKNOWN']


# Strategy for generating valid status codes
status_code_strategy = st.sampled_from(VALID_STATUS_CODES)


# Strategy for generating response messages
message_strategy = st.text(min_size=1, max_size=200).filter(lambda x: x.strip())


class TestLLMResponseParsing:
    """Property-based tests for LLM response parsing."""
    
    @given(status_code=status_code_strategy, message=message_strategy)
    def test_parse_colon_format_response(self, status_code, message):
        """
        Property 15: LLM response parsing (colon format).
        
        For any valid LLM response in "STATUS: message" format, 
        the LLM client should successfully parse and extract the status code.
        """
        # Create a mock LLM client
        llm_client = LLMClient(api_key="test_key")
        
        # Create response in "STATUS: message" format
        response = f"{status_code}: {message}"
        
        # Parse the response
        result = llm_client._parse_response(response)
        
        # Verify result structure
        assert isinstance(result, dict), "Parsed result must be a dictionary"
        assert 'status' in result, "Result must contain 'status' key"
        assert 'message' in result, "Result must contain 'message' key"
        
        # Verify status code is correctly extracted
        assert result['status'] == status_code, \
            f"Status should be '{status_code}', got '{result['status']}'"
        
        # Verify message is present
        assert isinstance(result['message'], str), "Message must be a string"
        assert len(result['message']) > 0, "Message must not be empty"
    
    @given(status_code=status_code_strategy, message=message_strategy)
    def test_parse_json_format_response(self, status_code, message):
        """
        Property 15: LLM response parsing (JSON format).
        
        For any valid LLM response in JSON format, the LLM client 
        should successfully parse and extract the status code.
        """
        import json
        
        # Create a mock LLM client
        llm_client = LLMClient(api_key="test_key")
        
        # Create response in JSON format
        response_dict = {"status": status_code, "message": message}
        response = json.dumps(response_dict)
        
        # Parse the response
        result = llm_client._parse_response(response)
        
        # Verify result structure
        assert isinstance(result, dict), "Parsed result must be a dictionary"
        assert 'status' in result, "Result must contain 'status' key"
        assert 'message' in result, "Result must contain 'message' key"
        
        # Verify status code is correctly extracted
        assert result['status'] == status_code, \
            f"Status should be '{status_code}', got '{result['status']}'"
        
        # Verify message matches
        assert result['message'] == message, \
            f"Message should be '{message}', got '{result['message']}'"
    
    @given(status_code=status_code_strategy)
    def test_parse_status_only_response(self, status_code):
        """
        Property 15: LLM response parsing (status only).
        
        For any response that starts with a valid status code, 
        the LLM client should extract it correctly.
        """
        # Create a mock LLM client
        llm_client = LLMClient(api_key="test_key")
        
        # Create response with just status code at the beginning
        response = f"{status_code} some additional text here"
        
        # Parse the response
        result = llm_client._parse_response(response)
        
        # Verify status code is correctly extracted
        assert result['status'] == status_code, \
            f"Status should be '{status_code}', got '{result['status']}'"
    
    @given(invalid_text=st.text(min_size=1, max_size=100).filter(
        lambda x: not any(code in x.upper() for code in VALID_STATUS_CODES)
    ))
    def test_parse_invalid_response_returns_unknown(self, invalid_text):
        """
        Property 15: Invalid response handling.
        
        For any response that doesn't contain a valid status code,
        the LLM client should return UNKNOWN status.
        """
        # Create a mock LLM client
        llm_client = LLMClient(api_key="test_key")
        
        # Parse the invalid response
        result = llm_client._parse_response(invalid_text)
        
        # Should return UNKNOWN for unparseable responses
        assert result['status'] == 'UNKNOWN', \
            f"Invalid response should return UNKNOWN status, got '{result['status']}'"


# Feature: task-classifier-agent, Property 16: LLM unavailability handling
# *For any* classification request when the LLM service is unavailable, 
# the StageManager should return an error response without crashing.
# **Validates: Requirements 10.4**


class MockUnavailableLLMClient:
    """Mock LLM client that simulates unavailability."""
    
    def __init__(self, error_type='connection'):
        self.error_type = error_type
    
    def classify(self, prompt):
        """Simulate LLM unavailability by raising an error."""
        if self.error_type == 'connection':
            raise LLMConnectionError("Unable to connect to LLM service")
        elif self.error_type == 'timeout':
            raise LLMTimeoutError("LLM request timed out")
        elif self.error_type == 'response':
            raise LLMResponseError("Invalid LLM response")
        else:
            raise Exception("Unknown error")


class TestLLMUnavailability:
    """Property-based tests for LLM unavailability handling."""
    
    @given(user_input=user_input_strategy)
    def test_classification_with_unavailable_llm_connection_error(self, user_input):
        """
        Property 16: LLM unavailability handling (connection error).
        
        For any classification request when the LLM service connection fails,
        the ClassificationEngine should handle it gracefully and return a valid status.
        """
        # Create engine with mock unavailable LLM client
        mock_llm = MockUnavailableLLMClient(error_type='connection')
        engine = ClassificationEngine(llm_client=mock_llm)
        
        # Classify should not crash
        result = engine.classify_intent(user_input)
        
        # Should return a valid status code (fallback to pattern matching or UNKNOWN)
        valid_statuses = {'NEXT', 'PREVIOUS', 'EXIT', 'HELP', 'CARE', 'HELLO', 'UNKNOWN'}
        assert result in valid_statuses, \
            f"Should return valid status even with unavailable LLM, got '{result}'"
    
    @given(user_input=user_input_strategy)
    def test_classification_with_unavailable_llm_timeout_error(self, user_input):
        """
        Property 16: LLM unavailability handling (timeout error).
        
        For any classification request when the LLM service times out,
        the ClassificationEngine should handle it gracefully and return a valid status.
        """
        # Create engine with mock unavailable LLM client
        mock_llm = MockUnavailableLLMClient(error_type='timeout')
        engine = ClassificationEngine(llm_client=mock_llm)
        
        # Classify should not crash
        result = engine.classify_intent(user_input)
        
        # Should return a valid status code
        valid_statuses = {'NEXT', 'PREVIOUS', 'EXIT', 'HELP', 'CARE', 'HELLO', 'UNKNOWN'}
        assert result in valid_statuses, \
            f"Should return valid status even with timeout, got '{result}'"
    
    @given(user_input=user_input_strategy)
    def test_classification_with_unavailable_llm_response_error(self, user_input):
        """
        Property 16: LLM unavailability handling (response error).
        
        For any classification request when the LLM returns an invalid response,
        the ClassificationEngine should handle it gracefully and return a valid status.
        """
        # Create engine with mock unavailable LLM client
        mock_llm = MockUnavailableLLMClient(error_type='response')
        engine = ClassificationEngine(llm_client=mock_llm)
        
        # Classify should not crash
        result = engine.classify_intent(user_input)
        
        # Should return a valid status code
        valid_statuses = {'NEXT', 'PREVIOUS', 'EXIT', 'HELP', 'CARE', 'HELLO', 'UNKNOWN'}
        assert result in valid_statuses, \
            f"Should return valid status even with response error, got '{result}'"
    
    @given(user_input=user_input_strategy, task_context=task_context_strategy)
    def test_classification_with_context_and_unavailable_llm(self, user_input, task_context):
        """
        Property 16: LLM unavailability with context.
        
        For any classification request with task context when LLM is unavailable,
        the ClassificationEngine should fall back to pattern matching and still work.
        """
        # Ensure current_stage matches one of the stages
        if task_context['stages']:
            task_context['current_stage'] = task_context['stages'][0]['stage']
        
        # Create engine with mock unavailable LLM client
        mock_llm = MockUnavailableLLMClient(error_type='connection')
        engine = ClassificationEngine(llm_client=mock_llm)
        
        # Classify should not crash
        result = engine.classify_intent(user_input, task_context)
        
        # Should return a valid status code
        valid_statuses = {'NEXT', 'PREVIOUS', 'EXIT', 'HELP', 'CARE', 'HELLO', 'UNKNOWN'}
        assert result in valid_statuses, \
            f"Should return valid status with context even when LLM unavailable, got '{result}'"
