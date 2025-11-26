# StageManager Documentation Index

Welcome to the StageManager documentation. This index helps you find the right documentation for your needs.

## Getting Started

- **[Quick Start Guide](QUICKSTART.md)** - Get up and running in 5 minutes
- **[README](../README.md)** - Comprehensive overview and installation guide
- **[Examples](../examples/README.md)** - Working code examples

## Documentation

### Core Documentation

- **[API Reference](API.md)** - Detailed API documentation for all classes and methods
- **[Configuration Guide](CONFIGURATION.md)** - Complete guide to configuring StageManager
- **[Security Best Practices](SECURITY.md)** - Security guidelines and API key management

### Examples

- **[Basic Usage Examples](../examples/basic_usage.py)** - Fundamental features and patterns
- **[Advanced Usage Examples](../examples/advanced_usage.py)** - Advanced integration patterns
- **[AWS Bedrock Examples](../examples/bedrock_usage.py)** - AWS Bedrock integration examples
- **[Example Configuration](../examples/config.json)** - Sample configuration file

## Documentation by Topic

### Installation & Setup

- [Installation](../README.md#installation) - How to install StageManager
- [Requirements](../README.md#requirements) - System requirements and dependencies
- [Development Setup](../README.md#development) - Setting up for development

### Basic Usage

- [Quick Start](QUICKSTART.md) - Fastest way to get started
- [Basic Classification](../README.md#basic-classification) - Simple input classification
- [Status Codes](../README.md#overview) - Understanding the seven status codes

### Advanced Features

- [Task Context](../README.md#task-context) - Using task context for intelligent classification
- [Custom Configuration](CONFIGURATION.md#classification-rules) - Customizing classification patterns
- [MCP Integration](../README.md#mcp-integration) - Caregiver notification setup
- [Data Models](API.md#data-models) - Working with TaskContext and Stage classes

### Configuration

- [Configuration Structure](CONFIGURATION.md#configuration-structure) - Overall config format
- [LLM Configuration](CONFIGURATION.md#llm-configuration) - LLM setup and providers
- [Classification Rules](CONFIGURATION.md#classification-rules) - Customizing patterns
- [MCP Server Config](CONFIGURATION.md#mcp-server-configuration) - MCP server setup
- [Loading Configuration](CONFIGURATION.md#loading-configuration) - Different ways to load config
- [Best Practices](CONFIGURATION.md#best-practices) - Configuration recommendations

### Security

- [API Key Management](SECURITY.md#api-key-management) - Secure API key handling
- [AWS Credentials Security](SECURITY.md#aws-credentials-security) - AWS security best practices
- [Configuration Security](SECURITY.md#configuration-security) - Secure configuration
- [Data Protection](SECURITY.md#data-protection) - Protecting sensitive data
- [Network Security](SECURITY.md#network-security) - Secure network configuration
- [Deployment Security](SECURITY.md#deployment-security) - Secure deployment practices

### API Reference

- [StageManager](API.md#stagemanager) - Main agent class
- [InputValidator](API.md#inputvalidator) - Input validation utilities
- [ClassificationEngine](API.md#classificationengine) - Core classification logic
- [ResponseGenerator](API.md#responsegenerator) - Response formatting
- [MCPClient](API.md#mcpclient) - MCP server integration
- [Data Models](API.md#data-models) - Stage, TaskContext, ClassificationResponse

### Testing

- [Testing Overview](../README.md#testing) - Running tests
- [Unit Tests](../README.md#run-unit-tests-only) - Component-level tests
- [Property Tests](../README.md#run-property-based-tests-only) - Property-based tests
- [Integration Tests](../README.md#run-integration-tests-only) - End-to-end tests

### Examples

- [Basic Examples](../examples/README.md#basic-usagepy) - Entry-level examples
- [Advanced Examples](../examples/README.md#advanced-usagepy) - Production patterns
- [Running Examples](../examples/README.md#running-examples) - How to run examples

## Documentation by Role

### For New Users

Start here if you're new to StageManager:

1. [Quick Start Guide](QUICKSTART.md) - 5-minute introduction
2. [Basic Examples](../examples/basic_usage.py) - Run working examples
3. [README](../README.md) - Comprehensive overview

### For Developers

Building applications with StageManager:

1. [API Reference](API.md) - Detailed API documentation
2. [Configuration Guide](CONFIGURATION.md) - Customization options
3. [Advanced Examples](../examples/advanced_usage.py) - Integration patterns
4. [Data Models](API.md#data-models) - Type-safe models

### For System Administrators

Deploying and configuring StageManager:

1. [Installation](../README.md#installation) - Installation instructions
2. [Configuration Guide](CONFIGURATION.md) - Configuration options
3. [MCP Server Config](CONFIGURATION.md#mcp-server-configuration) - MCP setup
4. [Best Practices](CONFIGURATION.md#best-practices) - Deployment recommendations

### For Contributors

Contributing to StageManager:

1. [Development Setup](../README.md#development) - Dev environment setup
2. [Testing](../README.md#testing) - Running tests
3. [Code Style](../README.md#code-style) - Coding standards
4. [Contributing](../README.md#contributing) - Contribution guidelines

## Quick Reference

### Status Codes

| Code | Purpose | Example |
|------|---------|---------|
| NEXT | Move forward | "continue", "next" |
| PREVIOUS | Go back | "back", "previous" |
| EXIT | Exit task | "quit", "exit" |
| HELP | Get help | "help", "assist" |
| CARE | Need support | "worried", "anxious" |
| HELLO | Greeting | "hello", "hi" |
| UNKNOWN | Unclear | Anything else |

### Common Tasks

- **Classify input**: `manager.classify("user input")`
- **With context**: `manager.classify("input", task_context)`
- **Custom config**: `StageManager(config=config_dict)`
- **Load from file**: `json.load(f)` then pass to constructor

### File Locations

```
stage-manager/
├── README.md                    # Main documentation
├── docs/
│   ├── INDEX.md                # This file
│   ├── QUICKSTART.md           # Quick start guide
│   ├── API.md                  # API reference
│   └── CONFIGURATION.md        # Configuration guide
├── examples/
│   ├── README.md               # Examples overview
│   ├── basic_usage.py          # Basic examples
│   ├── advanced_usage.py       # Advanced examples
│   └── config.json             # Example config
├── stage_manager/              # Source code
└── tests/                      # Test suite
```

## Getting Help

- **Examples not working?** Check [Troubleshooting](../examples/README.md#troubleshooting)
- **Configuration issues?** See [Configuration Troubleshooting](CONFIGURATION.md#troubleshooting)
- **API questions?** Check [API Reference](API.md)
- **General questions?** See [README](../README.md)

## External Resources

- **Hypothesis** (Property-based testing): https://hypothesis.readthedocs.io/
- **Python Type Hints**: https://docs.python.org/3/library/typing.html
- **Python Logging**: https://docs.python.org/3/library/logging.html

## Version Information

This documentation is for StageManager version 0.1.0.

## Contributing to Documentation

Found an error or want to improve the documentation?

1. Documentation is in Markdown format
2. Follow existing structure and style
3. Test all code examples
4. Submit a pull request

## License

StageManager is licensed under the MIT License. See LICENSE file for details.
