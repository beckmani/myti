#!/usr/bin/env python3
"""
AWS Bedrock usage example for StageManager.

This script demonstrates how to use the StageManager agent with AWS Bedrock
for LLM-powered classification using various Bedrock models.

Prerequisites:
- AWS credentials configured (via environment variables, ~/.aws/credentials, or IAM role)
- boto3 installed: pip install boto3

- Appropriate IAM permissions for bedrock:InvokeModel
"""

import os
import sys
import logging

# Add parent directory to path to import local modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stage_manager.stage_manager import StageManager

# Configure logging to see what's happening (DEBUG mode for detailed output)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Note: This example uses AWS Bedrock through configuration
# No need to import BedrockModel directly


def example_bedrock_with_config():
    """Demonstrate using AWS Bedrock through configuration (recommended method)."""
    print("=" * 60)
    print("Example 1: AWS Bedrock with Configuration (Recommended)")
    print("=" * 60)
    
    try:
        # Configure Bedrock through config dictionary
        # This uses AWS credentials from environment or ~/.aws/credentials
        config = {
            "llm": {
                "api_key": "bedrock",  # Special value to use AWS credentials
                "model": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",  # Inference profile ID
                "region": "us-west-2",
                "timeout": 30,
                "max_retries": 3
            }
        }
        
        print(f"\nConfigured Bedrock model: {config['llm']['model']}")
        print(f"Region: {config['llm']['region']}")
        print("Note: Using Claude Sonnet 4.5 via cross-region inference profile")
        
        # Create StageManager with config
        manager = StageManager(config=config)
        
        # Test various inputs
        test_inputs = [
            "I want to continue with the next step",
            "Can we go back to the previous stage?",
            "I need some help understanding this",
            "I'm feeling anxious about this task",
            "Hello, I'm ready to start",
            "I think I want to quit"
        ]
        
        print("\nTesting classification with Bedrock:")
        for user_input in test_inputs:
            result = manager.classify(user_input)
            print(f"\n  Input: '{user_input}'")
            print(f"  Status: {result['status']}")
            print(f"  Message: {result['message'][:60]}...")
        
        print("\n✓ Bedrock with config example completed successfully")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure AWS credentials are configured:")
        print("   - Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables")
        print("   - Or configure ~/.aws/credentials")
        print("2. Check IAM permissions - your user/role needs:")
        print("   - bedrock:InvokeModel")
        print("   - bedrock:InvokeModelWithResponseStream (optional)")
        print("3. Model availability varies by region and account type:")
        print("   - Amazon Titan models: Usually available by default")
        print("   - Anthropic Claude: May require AWS support request")
        print("   - Try different regions: us-east-1, us-west-2")
        print("4. Alternative models to try:")
        print("   - amazon.titan-text-express-v1 (default)")
        print("   - amazon.titan-text-lite-v1")
        print("   - anthropic.claude-v2 (if available)")
        print("5. Ensure boto3 is installed: pip install boto3")
        print("\nNote: If Bedrock is not available, use OpenAI instead:")
        print("      export OPENAI_API_KEY='your-key'")
        print("      python examples/basic_usage.py")


def example_bedrock_with_task_context():
    """Demonstrate using AWS Bedrock with task context."""
    print("\n" + "=" * 60)
    print("Example 2: AWS Bedrock with Task Context")
    print("=" * 60)
    
    try:
        # Configure Bedrock through config dictionary
        config = {
            "llm": {
                "api_key": "bedrock",  # Special value to use AWS credentials
                "model": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",  # Inference profile ID
                "region": "us-west-2",
                "timeout": 30,
                "max_retries": 3
            }
        }
        
        print(f"\nConfigured Bedrock model: {config['llm']['model']}")
        print(f"Region: {config['llm']['region']}")
        print("Note: Using Claude Sonnet 4.5 via cross-region inference profile")
        
        # Create StageManager with config
        manager = StageManager(config=config)
        
        # Test with task context
        task_context = {
            "task": "patient_care",
            "description": "Patient care workflow",
            "status": "in progress",
            "current_stage": "assessment",
            "stages": [
                {"stage": "intake", "description": "Patient intake", "timeout": 300},
                {"stage": "assessment", "description": "Initial assessment", "timeout": 600},
                {"stage": "treatment", "description": "Treatment plan", "timeout": 900}
            ]
        }
        
        test_cases = [
            ("Let's move to the next stage", "With context"),
            ("I need to go back", "With context"),
            ("This patient seems distressed", "CARE detection")
        ]
        
        print("\nTesting with task context:")
        for user_input, description in test_cases:
            result = manager.classify(user_input, task_context)
            print(f"\n  {description}")
            print(f"  Input: '{user_input}'")
            print(f"  Status: {result['status']}")
            print(f"  Message: {result['message'][:60]}...")
        
        print("\n✓ Bedrock with task context example completed successfully")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure boto3 is installed: pip install boto3")
        print("2. Configure AWS credentials")
        print("3. Check IAM permissions")


def main():
    """Run all Bedrock examples."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 12 + "StageManager AWS Bedrock Examples" + " " * 13 + "║")
    print("╚" + "=" * 58 + "╝")
    
    print("\nThese examples demonstrate using StageManager with AWS Bedrock")
    print("for LLM-powered classification.\n")
    
    try:
        example_bedrock_with_config()
        example_bedrock_with_task_context()
        
        print("\n" + "=" * 60)
        print("All Bedrock examples completed!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
