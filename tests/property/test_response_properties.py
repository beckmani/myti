"""Property-based tests for ResponseGenerator."""

import pytest
from hypothesis import given, strategies as st
from stage_manager.response_generator import ResponseGenerator


# Feature: task-classifier-agent, Property 5: Response structure validity
# *For any* valid user input, the StageManager should return a JSON response 
# containing exactly one status code from {NEXT, PREVIOUS, EXIT, HELP, CARE, HELLO, UNKNOWN} 
# and a non-empty message field.
# **Validates: Requirements 2.1, 2.9**


# Define valid status codes
VALID_STATUS_CODES = {"NEXT", "PREVIOUS", "EXIT", "HELP", "CARE", "HELLO", "UNKNOWN", "ERROR"}


# Strategy for generating valid status codes
status_code_strategy = st.sampled_from(list(VALID_STATUS_CODES))


# Strategy for generating optional context dictionaries
context_strategy = st.one_of(
    st.none(),
    st.fixed_dictionaries({}),
    st.fixed_dictionaries({
        "mcp_failed": st.booleans()
    }),
    st.fixed_dictionaries({
        "error_message": st.text(min_size=1, max_size=200)
    })
)


class TestResponseStructureProperties:
    """Property-based tests for response structure validity."""
    
    @given(status_code=status_code_strategy, context=context_strategy)
    def test_response_contains_valid_status_code(self, status_code, context):
        """
        Property: Response always contains exactly one valid status code.
        
        For any valid status code and optional context, the response should
        contain a status field with one of the valid status codes.
        """
        response = ResponseGenerator.generate_response(status_code, context)
        
        # Response must be a dictionary
        assert isinstance(response, dict), "Response must be a dictionary"
        
        # Response must have 'status' key
        assert "status" in response, "Response must contain 'status' key"
        
        # Status must be one of the valid status codes
        assert response["status"] in VALID_STATUS_CODES, \
            f"Status '{response['status']}' must be one of {VALID_STATUS_CODES}"
        
        # Status must match the input status code
        assert response["status"] == status_code, \
            f"Response status '{response['status']}' must match input '{status_code}'"
    
    @given(status_code=status_code_strategy, context=context_strategy)
    def test_response_contains_non_empty_message(self, status_code, context):
        """
        Property: Response always contains a non-empty message field.
        
        For any valid status code and optional context, the response should
        contain a message field with a non-empty string.
        """
        response = ResponseGenerator.generate_response(status_code, context)
        
        # Response must have 'message' key
        assert "message" in response, "Response must contain 'message' key"
        
        # Message must be a string
        assert isinstance(response["message"], str), \
            "Message must be a string"
        
        # Message must not be empty
        assert len(response["message"]) > 0, \
            "Message must be non-empty"
    
    @given(status_code=status_code_strategy, context=context_strategy)
    def test_response_has_exactly_two_fields(self, status_code, context):
        """
        Property: Response contains exactly status and message fields.
        
        For any valid status code and optional context, the response should
        contain exactly two fields: 'status' and 'message'.
        """
        response = ResponseGenerator.generate_response(status_code, context)
        
        # Response must have exactly 2 keys
        assert len(response) == 2, \
            f"Response must have exactly 2 fields, got {len(response)}: {list(response.keys())}"
        
        # Response must have 'status' and 'message' keys
        assert set(response.keys()) == {"status", "message"}, \
            f"Response must have 'status' and 'message' keys, got {list(response.keys())}"
    
    @given(status_code=status_code_strategy)
    def test_response_structure_without_context(self, status_code):
        """
        Property: Response structure is valid even without context.
        
        For any valid status code without context, the response should
        still have valid structure with status and non-empty message.
        """
        response = ResponseGenerator.generate_response(status_code, None)
        
        # Verify structure
        assert isinstance(response, dict)
        assert "status" in response
        assert "message" in response
        assert response["status"] in VALID_STATUS_CODES
        assert isinstance(response["message"], str)
        assert len(response["message"]) > 0
        assert len(response) == 2
