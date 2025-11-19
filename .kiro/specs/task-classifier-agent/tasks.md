# Implementation Plan

- [ ] 1. Set up project structure and dependencies
  - Create directory structure for the StageManager agent
  - Set up Python package with pyproject.toml or setup.py
  - Install strends library and dependencies (Hypothesis for property testing)
  - Create basic module structure: stage_manager/, tests/
  - _Requirements: 3.1_

- [ ] 2. Implement input validation module
  - Create InputValidator class with validation methods
  - Implement validate_user_input() for string validation
  - Implement validate_task_context() for JSON structure validation
  - Implement parse_task_context() for JSON parsing
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 4.1, 4.4_

- [ ]* 2.1 Write property test for input validation
  - **Property 1: Input acceptance**
  - **Property 2: Whitespace rejection**
  - **Property 3: Input immutability**
  - **Property 4: Unicode handling**
  - **Validates: Requirements 1.1, 1.2, 1.3, 1.4**

- [ ] 3. Implement data models
  - Create TaskContext dataclass for task structure
  - Create Stage dataclass for stage information
  - Create ClassificationResponse dataclass for response structure
  - Add validation methods to data models
  - _Requirements: 4.1, 4.2_

- [ ] 3.1 Write unit tests for data models
  - Test TaskContext creation and validation
  - Test Stage creation and validation
  - Test ClassificationResponse serialization to JSON
  - _Requirements: 4.1, 4.2_

- [ ] 4. Implement classification engine core
  - Create ClassificationEngine class
  - Implement pattern matching for status codes
  - Implement default classification rules
  - Implement classify_intent() method
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8_

- [ ] 4.1 Write unit tests for basic classification
  - Test NEXT classification with examples ("next", "continue", "proceed")
  - Test PREVIOUS classification with examples ("back", "previous")
  - Test EXIT classification with examples ("quit", "exit")
  - Test HELP classification with examples ("help", "call my mom")
  - Test CARE classification with examples ("worried", "anxious")
  - Test HELLO classification with examples ("hello", "hi")
  - Test UNKNOWN classification with examples ("banana", "maybe I'll eat")
  - _Requirements: 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8_

- [ ] 5. Implement configuration support
  - Add configuration loading in ClassificationEngine
  - Implement load_config() method
  - Implement default configuration fallback
  - Support custom classification rules from config
  - _Requirements: 5.1, 5.2, 5.3_

- [ ]* 5.1 Write property test for configuration
  - **Property 9: Configuration loading**
  - **Validates: Requirements 5.1, 5.2**

- [ ] 5.2 Write unit test for default configuration
  - Test initialization without configuration uses defaults
  - _Requirements: 5.3_

- [ ] 6. Implement context-aware classification
  - Add extract_stage_info() method to extract stage from input
  - Add is_at_first_stage() and is_at_last_stage() helper methods
  - Integrate task context into classify_intent() logic
  - Implement stage-aware classification decisions
  - _Requirements: 4.3, 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ]* 6.1 Write property test for context parsing
  - **Property 6: Task context parsing**
  - **Property 7: Context influences classification**
  - **Property 8: Malformed context handling**
  - **Validates: Requirements 4.1, 4.2, 4.3, 4.4**

- [ ]* 6.2 Write property test for stage extraction
  - **Property 10: Stage extraction from input**
  - **Property 11: Stage boundary awareness**
  - **Validates: Requirements 9.1, 9.4, 9.5**

- [ ]* 6.3 Write unit tests for context-aware classification
  - Test stage extraction from user input
  - Test priority of input stage over context stage
  - Test fallback to context stage when input has no stage
  - Test PREVIOUS at first stage boundary
  - Test NEXT at last stage boundary
  - _Requirements: 9.2, 9.3, 9.4, 9.5_

- [ ] 7. Implement response generator
  - Create ResponseGenerator class
  - Implement generate_response() method
  - Generate contextual messages for each status code
  - Format responses as JSON with status and message fields
  - _Requirements: 2.1, 2.9_

- [ ] 7.1 Write property test for response structure
  - **Property 5: Response structure validity**
  - **Validates: Requirements 2.1, 2.9**

- [ ] 8. Implement MCP client module
  - Create MCPClient class
  - Implement connect() method for MCP server connection
  - Implement call_caregiver() method
  - Implement is_connected() status check
  - Add error handling for connection failures
  - _Requirements: 7.1, 7.2, 7.3_

- [ ]* 8.1 Write unit tests for MCP client
  - Test successful connection to MCP server
  - Test connection failure handling
  - Test successful caregiver call
  - Test failed caregiver call
  - Test timeout handling
  - _Requirements: 7.1, 7.2, 7.3_

- [ ] 9. Integrate MCP client with CARE flow
  - Add MCP client integration to StageManager
  - Implement CARE detection and MCP call before response
  - Handle MCP unavailable gracefully
  - Add logging for MCP interactions
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [ ]* 9.1 Write property test for CARE flow
  - **Property 12: CARE triggers MCP call**
  - **Validates: Requirements 8.1**

- [ ]* 9.2 Write unit tests for CARE flow scenarios
  - Test CARE with successful MCP call
  - Test CARE with failed MCP call
  - Test CARE with unavailable MCP server
  - _Requirements: 8.2, 8.3, 8.4_

- [ ] 10. Implement main StageManager agent using strends
  - Create StageManager class using strends agent patterns
  - Integrate all components (validator, engine, response generator, MCP client)
  - Implement classify() main method
  - Add strends message handling
  - Add strends state management for configuration and MCP connection
  - _Requirements: 3.1, 3.2, 3.3_

- [ ]* 10.1 Write integration tests for StageManager
  - Test end-to-end classification flow
  - Test classification with task context
  - Test CARE flow with MCP integration
  - Test error handling across components
  - _Requirements: All_

- [ ] 11. Add error handling and logging
  - Implement comprehensive error handling for all error types
  - Add logging throughout the application
  - Ensure all errors return proper JSON responses
  - Add fallback behavior for external service failures
  - _Requirements: 1.2, 4.4, 7.2, 7.3, 8.3, 8.4_

- [ ] 12. Create example usage and documentation
  - Create example script demonstrating StageManager usage
  - Add docstrings to all public methods
  - Create README with installation and usage instructions
  - Document configuration format and options
  - _Requirements: All_

- [ ] 13. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
