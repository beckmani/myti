# Security Best Practices for StageManager

This document outlines security best practices for deploying and using StageManager, with a focus on API key management, data protection, and secure configuration.

## Table of Contents

- [API Key Management](#api-key-management)
- [AWS Credentials Security](#aws-credentials-security)
- [Configuration Security](#configuration-security)
- [Data Protection](#data-protection)
- [Network Security](#network-security)
- [Logging and Monitoring](#logging-and-monitoring)
- [Deployment Security](#deployment-security)

## API Key Management

### Never Hardcode API Keys

**❌ Bad Practice:**
```python
# DON'T DO THIS!
config = {
    "llm": {
        "api_key": "sk-1234567890abcdef",  # Hardcoded API key
        "model": "gpt-4"
    }
}
```

**✅ Good Practice:**
```python
import os

config = {
    "llm": {
        "api_key": os.getenv("LLM_API_KEY"),  # Load from environment
        "model": "gpt-4"
    }
}
```

### Use Environment Variables

Store API keys in environment variables, never in source code:

```bash
# Set environment variables
export LLM_API_KEY="your-api-key-here"
export AWS_ACCESS_KEY_ID="your-aws-access-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
```

For development, use a `.env` file (and add it to `.gitignore`):

```bash
# .env file
LLM_API_KEY=your-api-key-here
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
```

Load environment variables in your application:

```python
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Access environment variables
api_key = os.getenv("LLM_API_KEY")
```

### Use Secret Management Services

For production deployments, use dedicated secret management services:

#### AWS Secrets Manager

```python
import boto3
import json

def get_secret(secret_name):
    """Retrieve secret from AWS Secrets Manager."""
    client = boto3.client('secretsmanager', region_name='us-east-1')
    
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        raise

# Usage
secrets = get_secret('stagemanager/api-keys')
config = {
    "llm": {
        "api_key": secrets['llm_api_key'],
        "model": "gpt-4"
    }
}
```

#### Azure Key Vault

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def get_secret_from_keyvault(vault_url, secret_name):
    """Retrieve secret from Azure Key Vault."""
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)
    
    secret = client.get_secret(secret_name)
    return secret.value

# Usage
api_key = get_secret_from_keyvault(
    "https://your-vault.vault.azure.net/",
    "llm-api-key"
)
```

#### HashiCorp Vault

```python
import hvac

def get_secret_from_vault(vault_url, token, secret_path):
    """Retrieve secret from HashiCorp Vault."""
    client = hvac.Client(url=vault_url, token=token)
    
    secret = client.secrets.kv.v2.read_secret_version(path=secret_path)
    return secret['data']['data']

# Usage
secrets = get_secret_from_vault(
    "http://vault:8200",
    os.getenv("VAULT_TOKEN"),
    "stagemanager/api-keys"
)
```

### Rotate API Keys Regularly

- **Frequency**: Rotate API keys every 90 days minimum
- **Process**: 
  1. Generate new API key
  2. Update secret management system
  3. Deploy updated configuration
  4. Revoke old API key after verification
  5. Monitor for any issues

### Restrict API Key Permissions

Configure API keys with minimum required permissions:

**OpenAI:**
- Use project-specific API keys
- Set usage limits and rate limits
- Monitor usage through dashboard

**Anthropic:**
- Use workspace-specific API keys
- Set spending limits
- Enable usage alerts

**AWS Bedrock:**
- Use IAM roles with least privilege
- Restrict to specific models
- Enable CloudTrail logging

## AWS Credentials Security

### Use IAM Roles (Recommended)

For AWS deployments, use IAM roles instead of access keys:

**EC2 Instance:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "*"
    }
  ]
}
```

**Lambda Function:**
```python
# No credentials needed - Lambda execution role provides access
from stage_manager.stage_manager import StageManager

config = {
    "llm": {
        "api_key": "bedrock",  # Uses Lambda execution role
        "model": "anthropic.claude-v2",
        "region": "us-east-1"
    }
}

manager = StageManager(config=config)
```

### Secure AWS Access Keys

If you must use access keys:

1. **Never commit to version control**
2. **Use temporary credentials** (AWS STS)
3. **Enable MFA** for IAM users
4. **Rotate regularly** (every 90 days)
5. **Monitor usage** with CloudTrail

### AWS Credentials File Permissions

Restrict access to AWS credentials file:

```bash
# Set restrictive permissions
chmod 600 ~/.aws/credentials
chmod 600 ~/.aws/config

# Verify permissions
ls -la ~/.aws/
# Should show: -rw------- (600)
```

## Configuration Security

### Validate Configuration

Always validate configuration before use:

```python
def validate_config(config):
    """Validate configuration for security issues."""
    if not config:
        raise ValueError("Configuration cannot be empty")
    
    # Check for hardcoded secrets
    if "llm" in config:
        api_key = config["llm"].get("api_key", "")
        if api_key and not api_key.startswith("$"):
            # Warn if API key looks hardcoded
            if len(api_key) > 10 and not api_key == "bedrock":
                print("WARNING: API key appears to be hardcoded")
    
    # Validate MCP server URL uses HTTPS in production
    if "mcp_server" in config:
        url = config["mcp_server"].get("url", "")
        if url and not url.startswith("https://") and "localhost" not in url:
            print("WARNING: MCP server URL should use HTTPS in production")
    
    return True

# Usage
validate_config(config)
manager = StageManager(config=config)
```

### Separate Configurations by Environment

Use different configurations for different environments:

```
config/
├── development.json
├── staging.json
└── production.json
```

```python
import os
import json

env = os.getenv("ENVIRONMENT", "development")
config_file = f"config/{env}.json"

with open(config_file, "r") as f:
    config = json.load(f)

# Override sensitive values from environment
if "llm" in config:
    config["llm"]["api_key"] = os.getenv("LLM_API_KEY")

manager = StageManager(config=config)
```

### Encrypt Configuration Files

For sensitive configuration files, use encryption:

```python
from cryptography.fernet import Fernet
import json

def load_encrypted_config(encrypted_file, key):
    """Load and decrypt configuration file."""
    f = Fernet(key)
    
    with open(encrypted_file, "rb") as file:
        encrypted_data = file.read()
    
    decrypted_data = f.decrypt(encrypted_data)
    return json.loads(decrypted_data)

# Usage
encryption_key = os.getenv("CONFIG_ENCRYPTION_KEY")
config = load_encrypted_config("config.encrypted", encryption_key)
```

## Data Protection

### Sanitize User Input

Always sanitize user input to prevent injection attacks:

```python
def sanitize_input(user_input):
    """Sanitize user input to prevent injection attacks."""
    if not user_input:
        return user_input
    
    # Remove control characters
    sanitized = ''.join(char for char in user_input if ord(char) >= 32 or char in '\n\r\t')
    
    # Limit length
    max_length = 1000
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized

# Usage
user_input = sanitize_input(raw_user_input)
result = manager.classify(user_input, task_context)
```

### Protect Sensitive Data in Logs

Never log sensitive information:

```python
import logging
import re

class SensitiveDataFilter(logging.Filter):
    """Filter to redact sensitive data from logs."""
    
    def filter(self, record):
        # Redact API keys
        if hasattr(record, 'msg'):
            record.msg = re.sub(
                r'(api[_-]?key["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9-_]+)',
                r'\1***REDACTED***',
                str(record.msg),
                flags=re.IGNORECASE
            )
        return True

# Configure logging with filter
logger = logging.getLogger()
logger.addFilter(SensitiveDataFilter())
```

### Encrypt Data at Rest

For task contexts containing sensitive information:

```python
from cryptography.fernet import Fernet

class SecureTaskContext:
    """Wrapper for encrypting task context data."""
    
    def __init__(self, encryption_key):
        self.cipher = Fernet(encryption_key)
    
    def encrypt_context(self, task_context):
        """Encrypt task context."""
        json_data = json.dumps(task_context)
        encrypted = self.cipher.encrypt(json_data.encode())
        return encrypted
    
    def decrypt_context(self, encrypted_context):
        """Decrypt task context."""
        decrypted = self.cipher.decrypt(encrypted_context)
        return json.loads(decrypted.decode())

# Usage
encryption_key = Fernet.generate_key()
secure_context = SecureTaskContext(encryption_key)

encrypted = secure_context.encrypt_context(task_context)
# Store encrypted data...

# Later, decrypt when needed
task_context = secure_context.decrypt_context(encrypted)
result = manager.classify(user_input, task_context)
```

## Network Security

### Use HTTPS for All External Connections

Always use HTTPS for LLM and MCP connections:

```python
config = {
    "llm": {
        "api_key": os.getenv("LLM_API_KEY"),
        "model": "gpt-4",
        "endpoint": "https://api.openai.com/v1/chat/completions"  # HTTPS
    },
    "mcp_server": {
        "url": "https://mcp.example.com",  # HTTPS
        "timeout": 30
    }
}
```

### Verify SSL Certificates

Ensure SSL certificate verification is enabled:

```python
import requests

# Good - SSL verification enabled (default)
response = requests.post(url, json=payload, verify=True)

# Bad - SSL verification disabled (DON'T DO THIS in production)
# response = requests.post(url, json=payload, verify=False)
```

### Use Network Segmentation

Deploy StageManager in a secure network segment:

- Use VPC/VNET for cloud deployments
- Restrict inbound/outbound traffic with security groups
- Use private subnets for sensitive components
- Implement network ACLs

### Configure Timeouts

Set appropriate timeouts to prevent resource exhaustion:

```python
config = {
    "llm": {
        "api_key": os.getenv("LLM_API_KEY"),
        "model": "gpt-4",
        "timeout": 30,  # Prevent hanging connections
        "max_retries": 3
    },
    "mcp_server": {
        "url": "https://mcp.example.com",
        "timeout": 30  # Prevent hanging connections
    }
}
```

## Logging and Monitoring

### Enable Security Logging

Log security-relevant events:

```python
import logging

# Configure security logger
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

# Log security events
security_logger.info(f"Classification request from user: {user_id}")
security_logger.warning(f"Invalid input detected: {sanitized_input[:50]}")
security_logger.error(f"Authentication failed for API key: ***")
```

### Monitor for Anomalies

Implement monitoring for suspicious activity:

- Unusual classification patterns
- High error rates
- Repeated authentication failures
- Unexpected API usage spikes
- CARE status frequency

### Audit Trail

Maintain an audit trail for compliance:

```python
import json
from datetime import datetime

def log_audit_event(event_type, user_id, details):
    """Log audit event for compliance."""
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "user_id": user_id,
        "details": details
    }
    
    # Write to audit log
    with open("audit.log", "a") as f:
        f.write(json.dumps(audit_entry) + "\n")

# Usage
log_audit_event(
    "classification",
    user_id="user123",
    details={"status": "CARE", "mcp_notified": True}
)
```

## Deployment Security

### Container Security

When deploying in containers:

```dockerfile
# Use official Python image
FROM python:3.11-slim

# Create non-root user
RUN useradd -m -u 1000 stagemanager

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=stagemanager:stagemanager . .

# Switch to non-root user
USER stagemanager

# Run application
CMD ["python", "app.py"]
```

### Kubernetes Security

For Kubernetes deployments:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: stagemanager
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
  containers:
  - name: stagemanager
    image: stagemanager:latest
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
    env:
    - name: LLM_API_KEY
      valueFrom:
        secretKeyRef:
          name: stagemanager-secrets
          key: llm-api-key
    resources:
      limits:
        memory: "512Mi"
        cpu: "500m"
      requests:
        memory: "256Mi"
        cpu: "250m"
```

### Serverless Security

For AWS Lambda deployments:

```python
import json
import boto3
from stage_manager.stage_manager import StageManager

# Initialize outside handler for reuse
secrets_client = boto3.client('secretsmanager')
secret = secrets_client.get_secret_value(SecretId='stagemanager/config')
config = json.loads(secret['SecretString'])

manager = StageManager(config=config)

def lambda_handler(event, context):
    """Lambda handler for StageManager."""
    try:
        # Extract input from event
        user_input = event.get('user_input', '')
        task_context = event.get('task_context')
        
        # Classify
        result = manager.classify(user_input, task_context)
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

## Security Checklist

Use this checklist before deploying to production:

- [ ] API keys stored in environment variables or secret management service
- [ ] No hardcoded secrets in source code
- [ ] Configuration files not committed to version control
- [ ] HTTPS used for all external connections
- [ ] SSL certificate verification enabled
- [ ] Input validation and sanitization implemented
- [ ] Sensitive data redacted from logs
- [ ] Appropriate timeouts configured
- [ ] Security logging enabled
- [ ] Monitoring and alerting configured
- [ ] IAM roles used instead of access keys (AWS)
- [ ] Least privilege principle applied
- [ ] Regular security audits scheduled
- [ ] Incident response plan documented
- [ ] API key rotation process established

## Incident Response

If you suspect a security incident:

1. **Immediately rotate all API keys and credentials**
2. **Review audit logs for suspicious activity**
3. **Check for unauthorized access or data exfiltration**
4. **Notify relevant stakeholders**
5. **Document the incident**
6. **Implement additional security measures**
7. **Conduct post-incident review**

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [AWS Security Best Practices](https://aws.amazon.com/security/best-practices/)
- [Azure Security Best Practices](https://docs.microsoft.com/en-us/azure/security/fundamentals/best-practices-and-patterns)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)

## Support

For security concerns or to report vulnerabilities, please contact the security team at security@example.com.

**Do not disclose security vulnerabilities publicly until they have been addressed.**
