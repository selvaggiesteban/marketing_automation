import pytest
import asyncio
from datetime import datetime
from src.rate_limiter import RateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_3min_delay():
    """Rate limiter enforces 3 minute delay"""
    limiter = RateLimiter(min_delay_seconds=0.1)  # 100ms for testing

    start = datetime.now()
    await limiter.acquire()
    await limiter.acquire()  # Second call waits
    elapsed = (datetime.now() - start).total_seconds()

    assert elapsed >= 0.1, f"Expected delay, got {elapsed}s"


@pytest.mark.asyncio
async def test_rate_limiter_first_call_immediate():
    """First call is not delayed"""
    limiter = RateLimiter(min_delay_seconds=1.0)

    start = datetime.now()
    await limiter.acquire()
    elapsed = (datetime.now() - start).total_seconds()

    assert elapsed < 0.1, f"First call should be immediate"
