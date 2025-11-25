#!/usr/bin/env python3
"""
Advanced usage example for StageManager.

This script demonstrates advanced patterns including:
- Building a simple task flow system
- Handling stage transitions
- Custom MCP client implementation
- Configuration management
"""

from stage_manager.stage_manager import StageManager
from stage_manager.models import TaskContext, Stage
from typing import Dict, List, Optional
import json


class TaskFlowManager:
    """
    Example task flow manager that uses StageManager for navigation.
    
    This demonstrates how to build a complete task flow system
    using the StageManager agent.
    """
    
    def __init__(self, task_context: TaskContext, config: Optional[Dict] = None):
        """
        Initialize the task flow manager.
        
        Args:
            task_context: TaskContext object defining the task and stages
            config: Optional configuration for StageManager
        """
        self.task_context = task_context
        self.current_stage_index = 0
        self.manager = StageManager(config=config)
        self.history: List[str] = []
    
    def get_current_stage(self) -> Stage:
        """Get the current stage object."""
        return self.task_context.stages[self.current_stage_index]
    
    def process_input(self, user_input: str) -> Dict:
        """
        Process user input and handle stage transitions.
        
        Args:
            user_input: User's text input
            
        Returns:
            Dictionary with status, message, and current stage info
        """
        # Add current stage to context
        context_dict = self.task_context.to_dict()
        context_dict["current_stage"] = self.get_current_stage().stage
        
        # Classify the input
        result = self.manager.classify(user_input, context_dict)
        
        # Handle stage transitions
        if result["status"] == "NEXT":
            if self.current_stage_index < len(self.task_context.stages) - 1:
                self.current_stage_index += 1
                self.history.append(f"Moved to stage: {self.get_current_stage().stage}")
                result["current_stage"] = self.get_current_stage().stage
            else:
                result["message"] = "Already at the last stage"
        
        elif result["status"] == "PREVIOUS":
            if self.current_stage_index > 0:
                self.current_stage_index -= 1
                self.history.append(f"Moved back to stage: {self.get_current_stage().stage}")
                result["current_stage"] = self.get_current_stage().stage
            else:
                result["message"] = "Already at the first stage"
        
        elif result["status"] == "EXIT":
            self.history.append("Task exited")
            result["task_completed"] = False
        
        return result
    
    def get_progress(self) -> Dict:
        """Get current progress information."""
        return {
            "current_stage": self.get_current_stage().stage,
            "stage_index": self.current_stage_index,
            "total_stages": len(self.task_context.stages),
            "progress_percentage": (self.current_stage_index / len(self.task_context.stages)) * 100,
            "history": self.history
        }


def example_task_flow_system():
    """Demonstrate a complete task flow system."""
    print("=" * 60)
    print("Advanced Example 1: Task Flow System")
    print("=" * 60)
    
    # Create a task context using the data models
    task = TaskContext(
        task="onboarding",
        description="New user onboarding process",
        status="in progress",
        stages=[
            Stage(stage="welcome", description="Welcome message", timeout=60),
            Stage(stage="profile", description="Create user profile", timeout=300),
            Stage(stage="preferences", description="Set preferences", timeout=180),
            Stage(stage="tutorial", description="Complete tutorial", timeout=600),
            Stage(stage="complete", description="Onboarding complete", timeout=30)
        ]
    )
    
    # Create task flow manager
    flow = TaskFlowManager(task)
    
    # Simulate user interactions
    interactions = [
        "hello",
        "I'm ready to continue",
        "next please",
        "wait, go back",
        "okay, continue",
        "help me with this",
        "proceed to the next step"
    ]
    
    for user_input in interactions:
        print(f"\nUser: {user_input}")
        result = flow.process_input(user_input)
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        
        progress = flow.get_progress()
        print(f"Current Stage: {progress['current_stage']} ({progress['stage_index'] + 1}/{progress['total_stages']})")
        print(f"Progress: {progress['progress_percentage']:.1f}%")


def example_configuration_management():
    """Demonstrate configuration management patterns."""
    print("\n" + "=" * 60)
    print("Advanced Example 2: Configuration Management")
    print("=" * 60)
    
    import os
    
    # Load configuration from dictionary (could be from file)
    # Note: StageManager only supports Bedrock for LLM integration
    # Pass bedrock_model parameter directly instead of config
    config = {
        "classification_rules": {
            "NEXT": ["next", "continue", "proceed", "forward", "go on", "advance"],
            "PREVIOUS": ["back", "previous", "return", "go back", "rewind"],
            "EXIT": ["exit", "quit", "leave", "stop", "end", "cancel"],
            "HELP": ["help", "assist", "support", "call", "guide", "info"],
            "CARE": ["worried", "anxious", "scared", "concerned", "upset", "stressed"],
            "HELLO": ["hello", "hi", "hey", "greetings", "howdy"]
        },
        "mcp_server": {
            "url": "http://localhost:8080",
            "timeout": 30
        }
    }
    
    # Save configuration to file
    config_file = "examples/config.json"
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    print(f"\nConfiguration saved to: {config_file}")
    
    # Load configuration from file
    with open(config_file, "r") as f:
        loaded_config = json.load(f)
    
    # Initialize with loaded configuration
    manager = StageManager(config=loaded_config)
    
    # Test with custom patterns
    print("\nTesting with custom configuration:")
    test_inputs = ["advance", "rewind", "cancel", "guide"]
    
    for user_input in test_inputs:
        result = manager.classify(user_input)
        print(f"  '{user_input}' -> {result['status']}")


def example_data_models():
    """Demonstrate using the data models."""
    print("\n" + "=" * 60)
    print("Advanced Example 3: Working with Data Models")
    print("=" * 60)
    
    # Create stages
    stages = [
        Stage(stage="planning", description="Plan the project", timeout=1800),
        Stage(stage="execution", description="Execute the plan", timeout=3600),
        Stage(stage="review", description="Review the results", timeout=900)
    ]
    
    # Validate stages
    print("\nValidating stages:")
    for stage in stages:
        is_valid = stage.validate()
        print(f"  {stage.stage}: {'✓ Valid' if is_valid else '✗ Invalid'}")
    
    # Create task context
    task = TaskContext(
        task="project_workflow",
        description="Standard project workflow",
        status="not started",
        stages=stages
    )
    
    # Validate task context
    print(f"\nTask context validation: {'✓ Valid' if task.validate() else '✗ Invalid'}")
    
    # Convert to dictionary
    task_dict = task.to_dict()
    print(f"\nTask as dictionary:")
    print(json.dumps(task_dict, indent=2))
    
    # Create from dictionary
    reconstructed = TaskContext.from_dict(task_dict)
    print(f"\nReconstructed from dictionary: {'✓ Success' if reconstructed else '✗ Failed'}")


def example_error_recovery():
    """Demonstrate error recovery patterns."""
    print("\n" + "=" * 60)
    print("Advanced Example 4: Error Recovery")
    print("=" * 60)
    
    manager = StageManager()
    
    # Test various error conditions
    error_cases = [
        ("", "Empty input"),
        ("   \n\t  ", "Whitespace-only input"),
        (None, "None input (will be caught by type system)")
    ]
    
    for user_input, description in error_cases:
        print(f"\n{description}:")
        try:
            if user_input is None:
                print("  Skipping None input (type error)")
                continue
            result = manager.classify(user_input)
            print(f"  Status: {result['status']}")
            print(f"  Message: {result['message']}")
        except Exception as e:
            print(f"  Exception caught: {e}")
    
    # Test with malformed task context
    print("\nMalformed task context:")
    malformed_contexts = [
        ({"task": "test"}, "Missing required fields"),
        ({"task": "test", "description": "desc", "status": "active", "stages": "not_a_list"}, "Invalid stages type"),
        ({"task": "", "description": "desc", "status": "active", "stages": []}, "Empty task name")
    ]
    
    for context, description in malformed_contexts:
        print(f"\n  {description}:")
        result = manager.classify("continue", context)
        print(f"    Status: {result['status']}")
        print(f"    Message: {result['message']}")


def example_unicode_handling():
    """Demonstrate unicode and special character handling."""
    print("\n" + "=" * 60)
    print("Advanced Example 5: Unicode and Special Characters")
    print("=" * 60)
    
    manager = StageManager()
    
    # Test with various unicode inputs
    unicode_inputs = [
        "继续",  # Chinese for "continue"
        "помощь",  # Russian for "help"
        "مساعدة",  # Arabic for "help"
        "next 👍",  # Emoji
        "I'm worried 😟",  # Emoji with CARE keyword
        "hello! 🎉",  # Greeting with emoji
    ]
    
    print("\nTesting unicode and special characters:")
    for user_input in unicode_inputs:
        result = manager.classify(user_input)
        print(f"\n  Input: {user_input}")
        print(f"  Status: {result['status']}")
        print(f"  Message: {result['message'][:50]}...")


def main():
    """Run all advanced examples."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 12 + "StageManager Advanced Examples" + " " * 15 + "║")
    print("╚" + "=" * 58 + "╝")
    
    try:
        example_task_flow_system()
        example_configuration_management()
        example_data_models()
        example_error_recovery()
        example_unicode_handling()
        
        print("\n" + "=" * 60)
        print("All advanced examples completed successfully!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
