#!/usr/bin/env python3
"""
Basic usage example for StageManager.

This script demonstrates how to use the StageManager agent to classify
user input and navigate through multi-stage tasks.
"""

from stage_manager.stage_manager import StageManager
import json


def example_basic_classification():
    """Demonstrate basic classification without task context."""
    print("=" * 60)
    print("Example 1: Basic Classification")
    print("=" * 60)
    
    # Initialize the StageManager
    manager = StageManager()
    
    # Test various inputs
    test_inputs = [
        "I want to continue",
        "go back please",
        "I need help",
        "hello there",
        "I'm feeling worried",
        "quit this task",
        "banana smoothie"
    ]
    
    for user_input in test_inputs:
        result = manager.classify(user_input)
        print(f"\nInput: '{user_input}'")
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")


def example_with_task_context():
    """Demonstrate classification with task context."""
    print("\n" + "=" * 60)
    print("Example 2: Classification with Task Context")
    print("=" * 60)
    
    # Define a task context
    task_context = {
        "task": "morning_routine",
        "description": "Daily morning routine tasks",
        "status": "in progress",
        "current_stage": "breakfast",
        "stages": [
            {
                "stage": "wake_up",
                "description": "Wake up and get out of bed",
                "timeout": 300
            },
            {
                "stage": "breakfast",
                "description": "Eat a healthy breakfast",
                "timeout": 600
            },
            {
                "stage": "exercise",
                "description": "Do morning exercises",
                "timeout": 900
            }
        ]
    }
    
    manager = StageManager()
    
    # Test with context
    test_cases = [
        ("next please", "Should move to next stage"),
        ("go back", "Should go to previous stage"),
        ("I'm at stage wake_up and want to continue", "Stage from input overrides context")
    ]
    
    for user_input, description in test_cases:
        result = manager.classify(user_input, task_context)
        print(f"\n{description}")
        print(f"Input: '{user_input}'")
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")


def example_with_custom_config():
    """Demonstrate using custom classification rules."""
    print("\n" + "=" * 60)
    print("Example 3: Custom Classification Rules")
    print("=" * 60)
    
    # Define custom configuration
    custom_config = {
        "classification_rules": {
            "NEXT": ["next", "continue", "proceed", "forward", "onward"],
            "PREVIOUS": ["back", "previous", "return", "rewind"],
            "EXIT": ["exit", "quit", "leave", "stop", "done"],
            "HELP": ["help", "assist", "support", "guide"],
            "CARE": ["worried", "anxious", "scared", "stressed", "overwhelmed"],
            "HELLO": ["hello", "hi", "hey", "greetings", "howdy"]
        }
    }
    
    manager = StageManager(config=custom_config)
    
    # Test custom patterns
    test_inputs = [
        "onward!",  # Custom NEXT pattern
        "rewind",   # Custom PREVIOUS pattern
        "I'm overwhelmed"  # Custom CARE pattern
    ]
    
    for user_input in test_inputs:
        result = manager.classify(user_input)
        print(f"\nInput: '{user_input}'")
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")


def example_with_bedrock():
    """Demonstrate Bedrock integration."""
    print("\n" + "=" * 60)
    print("Example 3b: AWS Bedrock Integration")
    print("=" * 60)
    
    print("\nNote: To use AWS Bedrock integration, pass a BedrockModel instance:")
    print("  from your_bedrock_module import BedrockModel")
    print("  bedrock_model = BedrockModel(model_id='us.anthropic.claude-sonnet-4-5-20250929-v1:0')")
    print("  manager = StageManager(bedrock_model=bedrock_model)")
    print("\nWithout Bedrock, StageManager uses pattern-based classification.")
    print("See examples/bedrock_usage.py for complete Bedrock examples.")


def example_error_handling():
    """Demonstrate error handling."""
    print("\n" + "=" * 60)
    print("Example 5: Error Handling")
    print("=" * 60)
    
    manager = StageManager()
    
    # Test invalid inputs
    print("\n1. Empty input:")
    result = manager.classify("")
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    
    print("\n2. Whitespace-only input:")
    result = manager.classify("   ")
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    
    print("\n3. Invalid task context:")
    invalid_context = {"task": "test"}  # Missing required fields
    result = manager.classify("continue", invalid_context)
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")


def example_stage_boundary_awareness():
    """Demonstrate stage boundary awareness."""
    print("\n" + "=" * 60)
    print("Example 6: Stage Boundary Awareness")
    print("=" * 60)
    
    task_context = {
        "task": "tutorial",
        "description": "Tutorial steps",
        "status": "in progress",
        "current_stage": "step1",
        "stages": [
            {"stage": "step1", "description": "First step", "timeout": 300},
            {"stage": "step2", "description": "Second step", "timeout": 300},
            {"stage": "step3", "description": "Third step", "timeout": 300}
        ]
    }
    
    manager = StageManager()
    
    # Test at first stage
    print("\nAt first stage (step1):")
    result = manager.classify("go back", task_context)
    print(f"Input: 'go back'")
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    print("Note: PREVIOUS at first stage returns UNKNOWN")
    
    # Test at last stage
    task_context["current_stage"] = "step3"
    print("\nAt last stage (step3):")
    result = manager.classify("continue", task_context)
    print(f"Input: 'continue'")
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    print("Note: NEXT at last stage returns UNKNOWN")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "StageManager Examples" + " " * 22 + "║")
    print("╚" + "=" * 58 + "╝")
    
    try:
        example_basic_classification()
        example_with_task_context()
        example_with_custom_config()
        example_with_bedrock()
        example_error_handling()
        example_stage_boundary_awareness()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
