# Implementation Plan

- [ ] 1. Set up project structure and dependencies
  - Create directory structure for the StageManager agent
  - Set up Python package with pyproject.toml or setup.py
  - Install dependencies (Hypothesis for property testing)
  - Install LLM client libraries (openai, anthropic, or requests for custom endpoints)
  - Create basic module structure: stage_manager/, tests/
  - _Requirements: 3.1_

- [x] 2. Implement input validation module
  - Create InputValidator class with validation methods
  - Implement validate_user_input() for string validation
  - Implement validate_task_context() for JSON structure validation
  - Implement parse_task_context() for JSON parsing
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 4.1, 4.4_

- [x] 2.1 Write property test for input validation
  - **Property 1: Input acceptance**
  - **Property 2: Whitespace rejection**
  - **Property 3: Input immutability**
  - **Property 4: Unicode handling**
  - **Validates: Requirements 1.1, 1.2, 1.3, 1.4**

- [x] 3. Implement data models
  - Create TaskContext dataclass for task structure
  - Create Stage dataclass for stage information
  - Create ClassificationResponse dataclass for response structure
  - Add validation methods to data models
  - _Requirements: 4.1, 4.2_

- [x] 3.1 Write unit tests for data models
  - Test TaskContext creation and validation
  - Test Stage creation and validation
  - Test ClassificationResponse serialization to JSON
  - _Requirements: 4.1, 4.2_

- [x] 4. Implement LLM client module
  - Create LLMClient class
  - Implement initialization with API key, model, endpoint, and timeout
  - Implement classify() method to send prompts to LLM
  - Implement response parsing to extract status code and message
  - Add error handling for connection failures, timeouts, and invalid responses
  - Implement retry logic with exponential backoff
  - Add is_available() method to check LLM service availability
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 9.1, 9.2, 9.3, 9.4_

- [ ]* 4.1 Write unit tests for LLM client
  - Test successful LLM connection and classification
  - Test LLM timeout handling
  - Test invalid response parsing
  - Test retry logic for failed calls
  - Test API key validation
  - Mock LLM API responses for predictable testing
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 9.3, 9.4_

- [x] 5. Implement classification engine with LLM integration
  - Create ClassificationEngine class
  - Implement initialization with LLM client
  - Implement _build_llm_prompt() method to construct prompts with context
  - Implement classify_intent() method using LLM client
  - Add fallback to UNKNOWN for invalid LLM responses
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 7.2, 7.3, 9.1, 9.2, 9.3, 9.4_

- [x] 5.1 Write property test for LLM prompt construction
  - **Property 12: LLM prompt includes user input**
  - **Property 13: LLM prompt includes task context**
  - **Validates: Requirements 10.1, 10.2, 10.3**

- [ ]* 5.2 Write unit tests for classification with mocked LLM
  - Test NEXT classification with mocked LLM response
  - Test PREVIOUS classification with mocked LLM response
  - Test EXIT classification with mocked LLM response
  - Test HELP classification with mocked LLM response
  - Test CARE classification with mocked LLM response
  - Test HELLO classification with mocked LLM response
  - Test UNKNOWN classification with mocked LLM response
  - Test prompt construction includes all required information
  - _Requirements: 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 9.1, 9.2, 9.3, 9.4_

- [x] 5.3 Write property test for LLM response parsing
  - **Property 14: LLM response parsing**
  - **Validates: Requirements 8.3**

- [x] 5.4 Write property test for LLM unavailability
  - **Property 15: LLM unavailability handling**
  - **Validates: Requirements 8.4**

- [ ]* 5.5 Write property test for LLM timeout handling
  - **Property 16: LLM timeout handling**
  - **Validates: Requirements 9.3**

- [ ]* 5.6 Write property test for LLM retry behavior
  - **Property 17: LLM retry behavior**
  - **Validates: Requirements 9.4**

- [ ]* 5.7 Write property test for invalid LLM response handling
  - **Property 18: Invalid LLM response handling**
  - **Validates: Requirements 8.5**

- [ ]* 5.8 Write property test for ambiguous input handling
  - **Property 19: Ambiguous input handling**
  - **Validates: Requirements 7.1, 7.2, 7.3**

- [ ]* 5.9 Write property test for LLM classification flow
  - **Property 20: LLM classification flow**
  - **Validates: Requirements 8.1, 8.2**

- [ ]* 5.10 Write property test for LLM prompt instructions
  - **Property 21: LLM prompt instructions**
  - **Validates: Requirements 10.4**

- [x] 6. Implement configuration support
  - Add configuration loading in StageManager and ClassificationEngine
  - Implement LLM configuration loading (API key, model, endpoint, timeout, retries)
  - Implement default configuration fallback for LLM settings
  - Support custom LLM configuration from config dictionary
  - _Requirements: 6.1, 6.2, 6.3, 9.1, 9.2_

- [ ]* 6.1 Write property test for configuration
  - **Property 9: Configuration loading**
  - **Validates: Requirements 6.1, 6.2, 9.1, 9.2**

- [ ]* 6.2 Write unit test for default configuration
  - Test initialization without configuration uses defaults
  - Test LLM configuration with custom values
  - Test LLM configuration with missing values uses defaults
  - _Requirements: 6.3, 9.2_

- [x] 7. Implement context-aware classification with LLM
  - Add extract_stage_info() method to extract stage from input
  - Add is_at_first_stage() and is_at_last_stage() helper methods
  - Integrate task context into LLM prompt construction
  - Include stage boundary information in LLM prompts
  - Implement stage-aware classification decisions
  - _Requirements: 4.3, 5.1, 5.2, 5.3, 5.4, 5.5, 10.2, 10.3_

- [ ]* 7.1 Write property test for context parsing
  - **Property 6: Task context parsing**
  - **Property 7: Context influences classification**
  - **Property 8: Malformed context handling**
  - **Validates: Requirements 4.1, 4.2, 4.3, 4.4**

- [ ]* 7.2 Write property test for stage extraction
  - **Property 10: Stage extraction from input**
  - **Property 11: Stage boundary awareness**
  - **Validates: Requirements 5.1, 5.4, 5.5**

- [ ]* 7.3 Write unit tests for context-aware classification
  - Test stage extraction from user input
  - Test priority of input stage over context stage
  - Test fallback to context stage when input has no stage
  - Test PREVIOUS at first stage boundary with LLM
  - Test NEXT at last stage boundary with LLM
  - Test LLM prompt includes stage boundary information
  - _Requirements: 5.2, 5.3, 5.4, 5.5, 10.3_

- [x] 8. Implement response generator
  - Create ResponseGenerator class
  - Implement generate_response() method
  - Generate contextual messages for each status code
  - Format responses as JSON with status and message fields
  - Handle LLM-generated messages in responses
  - _Requirements: 2.1, 2.9_

- [x] 8.1 Write property test for response structure
  - **Property 5: Response structure validity**
  - **Validates: Requirements 2.1, 2.9**

- [x] 9. Implement main StageManager agent
  - Create StageManager class following component-based design patterns
  - Integrate all components (validator, LLM client, engine, response generator)
  - Implement classify() main method with LLM integration
  - Add clear message handling patterns
  - Add state management for configuration and LLM client
  - _Requirements: 3.1, 3.2, 3.3_

- [ ]* 9.1 Write integration tests for StageManager with LLM
  - Test end-to-end classification flow with mocked LLM
  - Test classification with task context and LLM
  - Test error handling across components including LLM failures
  - Test LLM timeout and retry scenarios
  - _Requirements: All_

- [ ] 10. Add error handling and logging
  - Implement comprehensive error handling for all error types including LLM errors
  - Add logging throughout the application including LLM interactions
  - Ensure all errors return proper JSON responses
  - Add fallback behavior for LLM service failures
  - Implement prompt injection prevention
  - Add API key protection in logging
  - _Requirements: 1.2, 4.4, 8.4, 8.5_

- [x] 11. Create example usage and documentation
  - Create example script demonstrating StageManager usage with LLM
  - Add docstrings to all public methods including LLM client
  - Create README with installation and usage instructions
  - Document LLM configuration format and options
  - Document supported LLM providers (OpenAI, Anthropic, custom)
  - Add security best practices for API key management
  - _Requirements: All_

- [x] 12. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
