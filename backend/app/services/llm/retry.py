import asyncio
import random
from typing import Callable, TypeVar, Any
from app.core.config import settings
from app.services.llm.exceptions import LLMProviderError

T = TypeVar("T")


async def execute_with_retry(
    func: Callable[[], Any],
    max_retries: int = settings.LLM_MAX_RETRIES,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
) -> T:
    """
    Executes an async function with bounded exponential backoff and jitter.
    Only retries on transient errors (where error.is_retryable is True).
    """
    attempt = 0
    while True:
        try:
            return await func()
        except LLMProviderError as err:
            attempt += 1
            if not err.is_retryable or attempt >= max_retries:
                raise err
            
            # Calculate exponential backoff with full jitter
            delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
            jitter = random.uniform(0, delay * 0.5)
            total_delay = delay + jitter
            
            await asyncio.sleep(total_delay)
