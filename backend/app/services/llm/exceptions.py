class LLMProviderError(Exception):
    """Base exception for all LLM provider errors."""
    def __init__(self, message: str, is_retryable: bool = False, provider: str = "llm"):
        super().__init__(message)
        self.message = message
        self.is_retryable = is_retryable
        self.provider = provider


class LLMAuthenticationError(LLMProviderError):
    """Raised on invalid API keys or missing authorization (401/403). Non-retryable."""
    def __init__(self, message: str = "Invalid or missing LLM API credentials", provider: str = "llm"):
        super().__init__(message, is_retryable=False, provider=provider)


class LLMInvalidRequestError(LLMProviderError):
    """Raised on malformed prompt, unsupported model, or bad parameters (400/422). Non-retryable."""
    def __init__(self, message: str, provider: str = "llm"):
        super().__init__(message, is_retryable=False, provider=provider)


class LLMRateLimitError(LLMProviderError):
    """Raised on rate limits (429). Retryable with backoff."""
    def __init__(self, message: str = "LLM provider rate limit exceeded", provider: str = "llm"):
        super().__init__(message, is_retryable=True, provider=provider)


class LLMTimeoutError(LLMProviderError):
    """Raised on provider network/read timeout. Retryable."""
    def __init__(self, message: str = "LLM provider request timed out", provider: str = "llm"):
        super().__init__(message, is_retryable=True, provider=provider)


class LLMConnectionError(LLMProviderError):
    """Raised on network connection failures. Retryable."""
    def __init__(self, message: str = "Failed to connect to LLM provider", provider: str = "llm"):
        super().__init__(message, is_retryable=True, provider=provider)


class LLMStructuredOutputError(LLMProviderError):
    """Raised when structured JSON parsing/validation fails. Non-retryable."""
    def __init__(self, message: str = "Failed to validate structured JSON response", provider: str = "llm"):
        super().__init__(message, is_retryable=False, provider=provider)
