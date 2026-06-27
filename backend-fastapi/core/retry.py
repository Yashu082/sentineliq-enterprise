from __future__ import annotations

import time
from functools import wraps
from typing import Any, Callable


class RetryConfig:
    """Configuration for retry logic."""

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 10.0,
        exponential_base: float = 2.0,
    ) -> None:
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base


def retry_with_backoff(
    config: RetryConfig | None = None,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable:
    """
    Decorator for retrying functions with exponential backoff.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            retry_config = config or RetryConfig()
            last_exception = None

            for attempt in range(retry_config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == retry_config.max_attempts - 1:
                        # Last attempt failed, raise the exception
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(
                        retry_config.initial_delay * (retry_config.exponential_base ** attempt),
                        retry_config.max_delay,
                    )
                    
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception

        return wrapper

    return decorator
