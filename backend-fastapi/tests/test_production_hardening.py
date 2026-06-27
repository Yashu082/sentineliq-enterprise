import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.rate_limiter import RateLimiter
from core.error_handler import SentinelIQError, ValidationError, AuthenticationError, LLMError
from core.retry import retry_with_backoff, RetryConfig


def test_rate_limiter_initialization():
    """Test that RateLimiter initializes correctly."""
    limiter = RateLimiter(requests_per_minute=60)
    assert limiter.requests_per_minute == 60
    assert limiter.window == 60


def test_rate_limiter_allows_requests_within_limit():
    """Test that RateLimiter allows requests within the limit."""
    limiter = RateLimiter(requests_per_minute=10)
    
    for i in range(10):
        assert limiter.is_allowed("user1") == True


def test_rate_limiter_blocks_requests_over_limit():
    """Test that RateLimiter blocks requests over the limit."""
    limiter = RateLimiter(requests_per_minute=5)
    
    # Make 5 requests (should all be allowed)
    for i in range(5):
        limiter.is_allowed("user1")
    
    # 6th request should be blocked
    assert limiter.is_allowed("user1") == False


def test_rate_limiter_different_users():
    """Test that RateLimiter tracks limits per user."""
    limiter = RateLimiter(requests_per_minute=3)
    
    # User1 makes 3 requests
    for i in range(3):
        limiter.is_allowed("user1")
    
    # User1 should be blocked
    assert limiter.is_allowed("user1") == False
    
    # User2 should still be allowed
    assert limiter.is_allowed("user2") == True


def test_rate_limiter_remaining_requests():
    """Test that RateLimiter correctly calculates remaining requests."""
    limiter = RateLimiter(requests_per_minute=10)
    
    assert limiter.get_remaining_requests("user1") == 10
    
    limiter.is_allowed("user1")
    assert limiter.get_remaining_requests("user1") == 9


def test_sentinel_error_base():
    """Test base SentinelIQError."""
    error = SentinelIQError("Test error", code="TEST_ERROR")
    assert error.message == "Test error"
    assert error.code == "TEST_ERROR"
    assert error.details == {}


def test_validation_error():
    """Test ValidationError."""
    error = ValidationError("Invalid input", details={"field": "email"})
    assert error.code == "VALIDATION_ERROR"
    assert error.details == {"field": "email"}


def test_authentication_error():
    """Test AuthenticationError."""
    error = AuthenticationError()
    assert error.code == "AUTHENTICATION_ERROR"
    assert error.message == "Authentication failed"


def test_llm_error():
    """Test LLMError."""
    error = LLMError("LLM failed", details={"model": "gemini"})
    assert error.code == "LLM_ERROR"
    assert error.details == {"model": "gemini"}


def test_retry_config_initialization():
    """Test RetryConfig initialization."""
    config = RetryConfig(max_attempts=5, initial_delay=0.5)
    assert config.max_attempts == 5
    assert config.initial_delay == 0.5
    assert config.max_delay == 10.0
    assert config.exponential_base == 2.0


def test_retry_with_backoff_success():
    """Test retry decorator succeeds on first attempt."""
    call_count = 0
    
    @retry_with_backoff(config=RetryConfig(max_attempts=3))
    def failing_function():
        nonlocal call_count
        call_count += 1
        return "success"
    
    result = failing_function()
    assert result == "success"
    assert call_count == 1


def test_retry_with_backoff_retries():
    """Test retry decorator retries on failure."""
    call_count = 0
    
    @retry_with_backoff(config=RetryConfig(max_attempts=3, initial_delay=0.1))
    def failing_function():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ValueError("Temporary failure")
        return "success"
    
    result = failing_function()
    assert result == "success"
    assert call_count == 2


def test_retry_with_backoff_exhausts():
    """Test retry decorator exhausts attempts."""
    call_count = 0
    
    @retry_with_backoff(config=RetryConfig(max_attempts=3, initial_delay=0.1))
    def always_failing_function():
        nonlocal call_count
        call_count += 1
        raise ValueError("Always fails")
    
    try:
        always_failing_function()
        assert False, "Should have raised ValueError"
    except ValueError:
        assert call_count == 3
