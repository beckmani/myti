"""Property-based tests for input validation."""

import pytest
from hypothesis import given, strategies as st, assume
from stage_manager.input_validator import InputValidator


# Feature: task-classifier-agent, Property 1: Input acceptance
# *For any* non-empty, non-whitespace string, the StageManager should accept 
# it as valid input without raising an exception.
# **Validates: Requirements 1.1**


# Feature: task-classifier-agent, Property 2: Whitespace rejection
# *For any* string composed entirely of whitespace characters (spaces, tabs, newlines), 
# the StageManager should reject the input and return an error response.
# **Validates: Requirements 1.2**


# Feature: task-classifier-agent, Property 3: Input immutability
# *For any* valid user input string, after processing by the StageManager, 
# the original input string should remain unchanged.
# **Validates: Requirements 1.3**


# Feature: task-classifier-agent, Property 4: Unicode handling
# *For any* string containing unicode characters or special characters, 
# the StageManager should process it without raising encoding errors or exceptions.
# **Validates: Requirements 1.4**


# Strategy for generating non-empty, non-whitespace strings
valid_input_strategy = st.text(min_size=1, max_size=1000).filter(lambda x: x.strip())


# Strategy for generating whitespace-only strings
whitespace_strategy = st.text(
    alphabet=st.sampled_from([' ', '\t', '\n', '\r', '\v', '\f']),
    min_size=1,
    max_size=100
)


# Strategy for generating unicode strings
unicode_strategy = st.text(
    alphabet=st.characters(
        blacklist_categories=('Cs',),  # Exclude surrogates
        min_codepoint=0x0000,
        max_codepoint=0x10FFFF
    ),
    min_size=1,
    max_size=500
).filter(lambda x: x.strip())  # Ensure not whitespace-only


# Strategy for generating strings with special characters
special_char_strategy = st.text(
    alphabet=st.sampled_from([
        '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', 
        '-', '_', '=', '+', '[', ']', '{', '}', '|', '\\',
        ';', ':', "'", '"', ',', '.', '<', '>', '/', '?',
        '~', '`', '€', '£', '¥', '©', '®', '™', '§', '¶'
    ]),
    min_size=1,
    max_size=100
)


class TestInputAcceptance:
    """Property-based tests for input acceptance."""
    
    @given(user_input=valid_input_strategy)
    def test_accepts_non_empty_non_whitespace_strings(self, user_input):
        """
        Property 1: Input acceptance.
        
        For any non-empty, non-whitespace string, the InputValidator 
        should accept it as valid input without raising an exception.
        """
        # Should not raise an exception
        result = InputValidator.validate_user_input(user_input)
        
        # Should return True for valid input
        assert result is True, \
            f"Should accept non-empty, non-whitespace input: '{user_input[:50]}...'"
    
    @given(user_input=valid_input_strategy)
    def test_accepts_strings_with_leading_trailing_spaces(self, user_input):
        """
        Property 1: Input acceptance with surrounding whitespace.
        
        For any non-empty string with leading/trailing spaces but non-whitespace content,
        the InputValidator should accept it as valid.
        """
        # Add leading and trailing spaces
        padded_input = f"  {user_input}  "
        
        # Should accept input with surrounding whitespace as long as content exists
        result = InputValidator.validate_user_input(padded_input)
        
        # Should return True since there's non-whitespace content
        assert result is True, \
            f"Should accept input with surrounding whitespace: '{padded_input[:50]}...'"


class TestWhitespaceRejection:
    """Property-based tests for whitespace rejection."""
    
    @given(whitespace_input=whitespace_strategy)
    def test_rejects_whitespace_only_strings(self, whitespace_input):
        """
        Property 2: Whitespace rejection.
        
        For any string composed entirely of whitespace characters,
        the InputValidator should reject the input.
        """
        # Verify the input is indeed whitespace-only
        assume(whitespace_input.isspace() or whitespace_input == '')
        
        # Should reject whitespace-only input
        result = InputValidator.validate_user_input(whitespace_input)
        
        # Should return False for whitespace-only input
        assert result is False, \
            f"Should reject whitespace-only input: {repr(whitespace_input[:50])}"
    
    def test_rejects_empty_string(self):
        """
        Property 2: Empty string rejection.
        
        The InputValidator should reject empty strings.
        """
        result = InputValidator.validate_user_input("")
        
        assert result is False, "Should reject empty string"
    
    @given(whitespace_count=st.integers(min_value=1, max_value=100))
    def test_rejects_various_whitespace_combinations(self, whitespace_count):
        """
        Property 2: Various whitespace combinations rejection.
        
        For any combination of whitespace characters, the InputValidator
        should reject the input.
        """
        # Generate various whitespace combinations
        whitespace_chars = [' ', '\t', '\n', '\r']
        whitespace_input = ''.join(
            whitespace_chars[i % len(whitespace_chars)] 
            for i in range(whitespace_count)
        )
        
        result = InputValidator.validate_user_input(whitespace_input)
        
        assert result is False, \
            f"Should reject whitespace combination: {repr(whitespace_input[:50])}"


class TestInputImmutability:
    """Property-based tests for input immutability."""
    
    @given(user_input=valid_input_strategy)
    def test_input_remains_unchanged_after_validation(self, user_input):
        """
        Property 3: Input immutability.
        
        For any valid user input string, after processing by the InputValidator,
        the original input string should remain unchanged.
        """
        # Store original input
        original_input = user_input
        original_id = id(user_input)
        
        # Validate the input
        InputValidator.validate_user_input(user_input)
        
        # Verify input hasn't changed
        assert user_input == original_input, \
            "Input string should remain unchanged after validation"
        
        # Verify it's the same object (strings are immutable in Python)
        assert id(user_input) == original_id, \
            "Input string object should remain the same"
    
    @given(user_input=valid_input_strategy)
    def test_input_immutability_with_multiple_validations(self, user_input):
        """
        Property 3: Input immutability across multiple validations.
        
        For any valid input, multiple validation calls should not modify
        the original input string.
        """
        original_input = user_input
        
        # Validate multiple times
        for _ in range(5):
            InputValidator.validate_user_input(user_input)
        
        # Verify input hasn't changed
        assert user_input == original_input, \
            "Input should remain unchanged after multiple validations"


class TestUnicodeHandling:
    """Property-based tests for unicode handling."""
    
    @given(unicode_input=unicode_strategy)
    def test_handles_unicode_characters_without_errors(self, unicode_input):
        """
        Property 4: Unicode handling.
        
        For any string containing unicode characters, the InputValidator
        should process it without raising encoding errors or exceptions.
        """
        # Should not raise an exception
        try:
            result = InputValidator.validate_user_input(unicode_input)
            
            # Should return True for valid unicode input
            assert result is True, \
                f"Should accept unicode input: '{unicode_input[:50]}...'"
        except UnicodeError as e:
            pytest.fail(f"Should not raise UnicodeError for unicode input: {e}")
        except Exception as e:
            pytest.fail(f"Should not raise exception for unicode input: {e}")
    
    @given(special_chars=special_char_strategy)
    def test_handles_special_characters_without_errors(self, special_chars):
        """
        Property 4: Special character handling.
        
        For any string containing special characters, the InputValidator
        should process it without raising exceptions.
        """
        # Should not raise an exception
        try:
            result = InputValidator.validate_user_input(special_chars)
            
            # Should return True for valid special character input
            assert result is True, \
                f"Should accept special character input: '{special_chars[:50]}...'"
        except Exception as e:
            pytest.fail(f"Should not raise exception for special characters: {e}")
    
    @given(
        text=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
        emoji=st.sampled_from(['😀', '🎉', '❤️', '🚀', '✨', '🔥', '💯', '🌟'])
    )
    def test_handles_emoji_without_errors(self, text, emoji):
        """
        Property 4: Emoji handling.
        
        For any string containing emoji characters, the InputValidator
        should process it without raising exceptions.
        """
        emoji_input = f"{text} {emoji}"
        
        try:
            result = InputValidator.validate_user_input(emoji_input)
            
            # Should return True for valid emoji input
            assert result is True, \
                f"Should accept emoji input: '{emoji_input}'"
        except Exception as e:
            pytest.fail(f"Should not raise exception for emoji: {e}")
    
    @given(
        text=st.text(
            alphabet=st.characters(
                whitelist_categories=('Lo',),  # Other letters (e.g., Chinese, Arabic)
                min_codepoint=0x4E00,  # CJK Unified Ideographs start
                max_codepoint=0x9FFF   # CJK Unified Ideographs end
            ),
            min_size=1,
            max_size=50
        )
    )
    def test_handles_cjk_characters_without_errors(self, text):
        """
        Property 4: CJK character handling.
        
        For any string containing CJK (Chinese, Japanese, Korean) characters,
        the InputValidator should process it without raising exceptions.
        """
        try:
            result = InputValidator.validate_user_input(text)
            
            # Should return True for valid CJK input
            assert result is True, \
                f"Should accept CJK input: '{text[:20]}...'"
        except Exception as e:
            pytest.fail(f"Should not raise exception for CJK characters: {e}")
    
    @given(
        base_text=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        combining_chars=st.text(
            alphabet=st.characters(
                whitelist_categories=('Mn', 'Mc'),  # Combining marks
                min_codepoint=0x0300,
                max_codepoint=0x036F
            ),
            min_size=1,
            max_size=10
        )
    )
    def test_handles_combining_characters_without_errors(self, base_text, combining_chars):
        """
        Property 4: Combining character handling.
        
        For any string containing combining characters (accents, diacritics),
        the InputValidator should process it without raising exceptions.
        """
        combined_input = base_text + combining_chars
        
        try:
            result = InputValidator.validate_user_input(combined_input)
            
            # Should return True for valid combined character input
            assert result is True, \
                f"Should accept combined character input: '{combined_input[:50]}...'"
        except Exception as e:
            pytest.fail(f"Should not raise exception for combining characters: {e}")


class TestInputValidationEdgeCases:
    """Additional edge case tests for input validation."""
    
    def test_rejects_none_input(self):
        """
        Edge case: None input should be rejected.
        """
        result = InputValidator.validate_user_input(None)
        
        assert result is False, "Should reject None input"
    
    @given(non_string=st.one_of(
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False),
        st.booleans(),
        st.lists(st.text()),
        st.dictionaries(st.text(), st.text())
    ))
    def test_rejects_non_string_input(self, non_string):
        """
        Edge case: Non-string input should be rejected.
        
        For any non-string input, the InputValidator should reject it.
        """
        result = InputValidator.validate_user_input(non_string)
        
        assert result is False, \
            f"Should reject non-string input of type {type(non_string)}"
    
    @given(length=st.integers(min_value=1, max_value=10000))
    def test_handles_very_long_strings(self, length):
        """
        Edge case: Very long strings should be handled.
        
        For any very long string, the InputValidator should process it
        without errors.
        """
        long_input = 'a' * length
        
        try:
            result = InputValidator.validate_user_input(long_input)
            
            assert result is True, \
                f"Should accept very long input of length {length}"
        except Exception as e:
            pytest.fail(f"Should not raise exception for long input: {e}")
