"""Custom exceptions for Gemini service."""

from typing import Optional


class GeminiServiceError(Exception):
    """Base exception for Gemini service errors."""

    pass


class GeminiRateLimitError(GeminiServiceError):
    """Raised when API rate limit is exceeded."""

    def __init__(self, message: str, retry_after_seconds: Optional[int] = None):
        super().__init__(message)
        self.retry_after_seconds = retry_after_seconds


class GeminiQuotaExceededError(GeminiServiceError):
    """Raised when API quota is exceeded."""

    def __init__(self, message: str, quota_type: Optional[str] = None):
        super().__init__(message)
        self.quota_type = quota_type


class GeminiAPIError(GeminiServiceError):
    """Raised when API returns an error."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class GeminiConfigurationError(GeminiServiceError):
    """Raised when service configuration is invalid."""

    pass
