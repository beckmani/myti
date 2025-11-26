"""LLM Client for classification using Large Language Models."""

import logging
import time
import json
import re
from typing import Dict, Optional, Any
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError, BotoCoreError
import requests


logger = logging.getLogger(__name__)


class LLMConnectionError(Exception):
    """Raised when connection to LLM service fails."""
    pass


class LLMTimeoutError(Exception):
    """Raised when LLM request times out."""
    pass


class LLMResponseError(Exception):
    """Raised when LLM response is invalid or unparseable."""
    pass


class LLMClient:
    """
    Client for communicating with Large Language Model APIs.
    
    Supports multiple LLM providers including OpenAI, Anthropic, and custom endpoints.
    Implements retry logic with exponential backoff for resilience.
    """
    
    # Valid status codes that can be returned
    VALID_STATUS_CODES = {"NEXT", "PREVIOUS", "EXIT", "HELP", "CARE", "HELLO", "UNKNOWN"}
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        endpoint: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: int = 1,
        region: Optional[str] = None
    ):
        """
        Initialize LLM client.
        
        Args:
            api_key: API key for LLM service (or AWS access key for Bedrock)
            model: Model name to use (e.g., "gpt-4", "claude-3-opus", "anthropic.claude-v2")
            endpoint: Optional custom API endpoint
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries in seconds (exponential backoff)
            region: AWS region for Bedrock (e.g., "us-east-1")
            
        Raises:
            ValueError: If api_key is empty or None
        """
        if not api_key:
            raise ValueError("API key cannot be empty")
        
        self.api_key = api_key
        self.model = model
        self.endpoint = endpoint
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.region = region or "us-east-1"
        self._available = None  # Cache availability status
        self._bedrock_client = None
        
        # Determine provider from model name or endpoint
        self.provider = self._detect_provider()
        
        # Initialize Bedrock client if needed
        if self.provider == "bedrock":
            self._init_bedrock_client()
        
        logger.info(
            f"LLM client initialized: provider={self.provider}, "
            f"model={model}, timeout={timeout}s"
        )
    
    def _detect_provider(self) -> str:
        """
        Detect LLM provider from model name or endpoint.
        
        Returns:
            Provider name: "openai", "anthropic", "bedrock", or "custom"
        """
        if self.endpoint:
            # Custom endpoint
            if "bedrock" in self.endpoint.lower() or "amazonaws.com" in self.endpoint.lower():
                return "bedrock"
            elif "anthropic" in self.endpoint.lower():
                return "anthropic"
            elif "openai" in self.endpoint.lower():
                return "openai"
            return "custom"
        
        # Detect from model name
        model_lower = self.model.lower()
        
        # AWS Bedrock model IDs typically have format: provider.model-name
        if "." in model_lower and any(provider in model_lower for provider in ["anthropic", "amazon", "ai21", "cohere", "meta"]):
            return "bedrock"
        elif "gpt" in model_lower or "davinci" in model_lower:
            return "openai"
        elif "claude" in model_lower and "anthropic." not in model_lower:
            return "anthropic"
        
        return "custom"
    
    def _init_bedrock_client(self):
        """Initialize AWS Bedrock client."""
        try:
            # For Bedrock, api_key can be AWS access key or use default credentials
            if self.api_key and self.api_key != "bedrock":
                # Use provided credentials
                self._bedrock_client = boto3.client(
                    service_name='bedrock-runtime',
                    region_name=self.region,
                    aws_access_key_id=self.api_key,
                    aws_secret_access_key=self.api_key  # This should be passed separately in production
                )
            else:
                # Use default AWS credentials from environment/config
                self._bedrock_client = boto3.client(
                    service_name='bedrock-runtime',
                    region_name=self.region
                )
            logger.info(f"Bedrock client initialized for region {self.region}")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            raise LLMConnectionError(f"Failed to initialize AWS Bedrock client: {e}")
    
    def classify(self, prompt: str) -> Dict[str, str]:
        """
        Send classification request to LLM with retry logic.
        
        Args:
            prompt: The constructed prompt for classification
            
        Returns:
            Dictionary with 'status' and 'message' keys
            
        Raises:
            LLMConnectionError: If connection to LLM service fails after retries
            LLMTimeoutError: If request times out after retries
            LLMResponseError: If response is invalid or unparseable
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"LLM classification attempt {attempt + 1}/{self.max_retries}")
                
                # Make the actual API call
                response = self._make_api_call(prompt)
                
                # Parse and validate the response
                result = self._parse_response(response)
                
                logger.info(f"LLM classification successful: status={result['status']}")
                return result
                
            except (LLMConnectionError, LLMTimeoutError) as e:
                last_exception = e
                logger.warning(
                    f"LLM request failed (attempt {attempt + 1}/{self.max_retries}): {e}"
                )
                
                # Don't retry on the last attempt
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    delay = self.retry_delay * (2 ** attempt)
                    logger.debug(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"All {self.max_retries} retry attempts failed")
                    raise
            
            except LLMResponseError as e:
                # Don't retry on response parsing errors
                logger.error(f"LLM response parsing failed: {e}")
                raise
        
        # Should not reach here, but just in case
        if last_exception:
            raise last_exception
        raise LLMConnectionError("Failed to classify after all retries")
    
    def _make_api_call(self, prompt: str) -> str:
        """
        Make the actual API call to the LLM service.
        
        Args:
            prompt: The prompt to send
            
        Returns:
            Raw response text from the LLM
            
        Raises:
            LLMConnectionError: If connection fails
            LLMTimeoutError: If request times out
        """
        logger.debug(f"Making API call to {self.provider} with model {self.model}")
        
        try:
            if self.provider == "bedrock":
                return self._call_bedrock(prompt)
            elif self.provider == "openai":
                return self._call_openai(prompt)
            elif self.provider == "anthropic":
                return self._call_anthropic(prompt)
            else:
                return self._call_custom(prompt)
                
        except Exception as e:
            # Handle requests exceptions
            if isinstance(e, requests.exceptions.Timeout):
                logger.error(f"API call timed out after {self.timeout}s")
                raise LLMTimeoutError(f"Request timed out after {self.timeout} seconds")
            elif isinstance(e, requests.exceptions.ConnectionError):
                logger.error(f"Connection error: {e}")
                raise LLMConnectionError(f"Failed to connect to LLM service: {e}")
            
            # Handle boto3 exceptions
            if isinstance(e, (ClientError, BotoCoreError)):
                logger.error(f"AWS Bedrock error: {e}")
                raise LLMConnectionError(f"AWS Bedrock error: {e}")
            
            logger.error(f"API call failed: {e}")
            raise LLMConnectionError(f"Failed to connect to LLM service: {e}")
    
    def _call_bedrock(self, prompt: str) -> str:
        """Call AWS Bedrock API using Converse API (Messages API) or legacy InvokeModel API."""
        if not self._bedrock_client:
            raise LLMConnectionError("Bedrock client not initialized")
        
        try:
            # Check if this is a Claude 3+ model that requires Converse API
            # Claude 3+ models include: claude-3-opus, claude-3-sonnet, claude-3-haiku, claude-3-5-sonnet, etc.
            uses_converse_api = (
                "anthropic" in self.model.lower() and 
                ("claude-3" in self.model.lower() or "sonnet-4" in self.model.lower() or "opus-4" in self.model.lower())
            )
            
            if uses_converse_api:
                # Use Converse API for Claude 3+ models
                logger.debug(f"Using Converse API for model: {self.model}")
                response = self._bedrock_client.converse(
                    modelId=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": [{"text": prompt}]
                        }
                    ],
                    system=[{"text": "You are a task navigation assistant."}],
                    inferenceConfig={
                        "maxTokens": 150,
                        "temperature": 0.3
                        # Note: Claude models don't allow both temperature and topP
                    }
                )
                
                # Extract text from Converse API response
                output = response.get("output", {})
                message = output.get("message", {})
                content = message.get("content", [])
                
                if content and len(content) > 0:
                    return content[0].get("text", "")
                
                raise LLMResponseError(f"Could not extract text from Converse API response: {response}")
            
            else:
                # Use legacy InvokeModel API for older models
                logger.debug(f"Using InvokeModel API for model: {self.model}")
                
                # Prepare the request body based on model provider
                if "anthropic" in self.model.lower():
                    # Anthropic Claude 2 models on Bedrock (legacy format)
                    body = json.dumps({
                        "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                        "max_tokens_to_sample": 150,
                        "temperature": 0.3,
                        "top_p": 0.9,
                    })
                elif "amazon" in self.model.lower():
                    # Amazon Titan models
                    body = json.dumps({
                        "inputText": prompt,
                        "textGenerationConfig": {
                            "maxTokenCount": 150,
                            "temperature": 0.3,
                            "topP": 0.9,
                        }
                    })
                else:
                    # Generic format
                    body = json.dumps({
                        "prompt": prompt,
                        "max_tokens": 150,
                        "temperature": 0.3,
                    })
                
                # Invoke the model
                response = self._bedrock_client.invoke_model(
                    modelId=self.model,
                    body=body,
                    contentType="application/json",
                    accept="application/json"
                )
                
                # Parse the response
                response_body = json.loads(response['body'].read())
                
                # Extract text based on model provider
                if "anthropic" in self.model.lower():
                    return response_body.get("completion", "")
                elif "amazon" in self.model.lower():
                    results = response_body.get("results", [])
                    if results:
                        return results[0].get("outputText", "")
                else:
                    # Try common response fields
                    return response_body.get("text", response_body.get("completion", str(response_body)))
                
                raise LLMResponseError(f"Could not extract text from Bedrock response: {response_body}")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"Bedrock ClientError: {error_code} - {error_message}")
            raise LLMConnectionError(f"AWS Bedrock error: {error_code} - {error_message}")
        except Exception as e:
            logger.error(f"Bedrock API call failed: {e}")
            raise LLMConnectionError(f"Failed to call AWS Bedrock: {e}")
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API."""
        endpoint = self.endpoint or "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a task navigation assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 150
        }
        
        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            raise LLMConnectionError(
                f"OpenAI API returned status {response.status_code}: {response.text}"
            )
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API."""
        endpoint = self.endpoint or "https://api.anthropic.com/v1/messages"
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 150,
            "temperature": 0.3
        }
        
        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            raise LLMConnectionError(
                f"Anthropic API returned status {response.status_code}: {response.text}"
            )
        
        data = response.json()
        return data["content"][0]["text"]
    
    def _call_custom(self, prompt: str) -> str:
        """Call custom endpoint."""
        if not self.endpoint:
            raise LLMConnectionError("Custom endpoint not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens": 150,
            "temperature": 0.3
        }
        
        response = requests.post(
            self.endpoint,
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            raise LLMConnectionError(
                f"Custom API returned status {response.status_code}: {response.text}"
            )
        
        data = response.json()
        # Try common response formats
        if "response" in data:
            return data["response"]
        elif "text" in data:
            return data["text"]
        elif "content" in data:
            return data["content"]
        else:
            raise LLMResponseError(f"Unexpected response format: {data}")
    
    def _parse_response(self, response: str) -> Dict[str, str]:
        """
        Parse LLM response to extract status code and message.
        
        Expected format: "STATUS_CODE: message"
        or JSON: {"status": "STATUS_CODE", "message": "message"}
        
        Args:
            response: Raw response from LLM
            
        Returns:
            Dictionary with 'status' and 'message' keys
            
        Raises:
            LLMResponseError: If response cannot be parsed or is invalid
        """
        if not response or not isinstance(response, str):
            raise LLMResponseError("Response is empty or not a string")
        
        response = response.strip()
        
        # Try to parse as JSON first
        try:
            data = json.loads(response)
            if isinstance(data, dict) and "status" in data and "message" in data:
                status = data["status"].upper()
                message = data["message"]
                
                if status in self.VALID_STATUS_CODES:
                    return {"status": status, "message": message}
                else:
                    logger.warning(f"Invalid status code in JSON response: {status}")
                    return {"status": "UNKNOWN", "message": message}
        except (json.JSONDecodeError, KeyError, AttributeError):
            # Not JSON or invalid JSON, try text parsing
            pass
        
        # Try to parse as "STATUS: message" format
        match = re.match(r'^([A-Z]+)\s*:\s*(.+)$', response, re.DOTALL)
        if match:
            status = match.group(1).upper()
            message = match.group(2).strip()
            
            if status in self.VALID_STATUS_CODES:
                return {"status": status, "message": message}
            else:
                logger.warning(f"Invalid status code in text response: {status}")
                return {"status": "UNKNOWN", "message": message}
        
        # Try to extract status code from the beginning of the response
        words = response.split()
        if words:
            first_word = words[0].upper().rstrip(':,.')
            if first_word in self.VALID_STATUS_CODES:
                # Use first word as status, rest as message
                message = ' '.join(words[1:]) if len(words) > 1 else response
                return {"status": first_word, "message": message.strip()}
        
        # If we can't parse it, return UNKNOWN
        logger.warning(f"Could not parse LLM response format: {response[:100]}")
        return {
            "status": "UNKNOWN",
            "message": f"Unable to parse LLM response: {response[:200]}"
        }
    
    def is_available(self) -> bool:
        """
        Check if LLM service is available.
        
        Makes a lightweight test request to verify connectivity.
        Caches the result to avoid repeated checks.
        
        Returns:
            True if service is available, False otherwise
        """
        # Return cached result if available
        if self._available is not None:
            return self._available
        
        try:
            logger.debug("Checking LLM service availability")
            
            # Try a simple test request with minimal prompt
            test_prompt = "Test connection. Respond with: HELLO: Service available"
            
            # Use a shorter timeout for availability check
            original_timeout = self.timeout
            self.timeout = 5
            
            try:
                result = self.classify(test_prompt)
                self._available = True
                logger.info("LLM service is available")
            finally:
                self.timeout = original_timeout
            
            return True
            
        except (LLMConnectionError, LLMTimeoutError, LLMResponseError) as e:
            logger.warning(f"LLM service is not available: {e}")
            self._available = False
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking LLM availability: {e}")
            self._available = False
            return False
