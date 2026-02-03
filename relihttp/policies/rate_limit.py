# -*- coding: utf-8 -*-
# @Time    : 2026/2/3 11:01
# @Author  : fzf
# @FileName: rate_limit.py
# @Software: PyCharm
from typing import Awaitable, Callable, Optional

from .base import Policy
from ..models import Context
from ..utils import TokenBucket
from ..utils import sleep as _sleep


class RateLimitedError(RuntimeError):
    pass


class RateLimitPolicy(Policy):
    """
    Token-bucket rate limiter policy.

    rate_limit: tokens per second
    burst: capacity (max burst). Default = rate_limit (allow 1s burst).
    mode:
      - "sleep": block and wait until allowed
      - "raise": raise RateLimitedError when would block
    """

    def __init__(
        self,
        rate_limit: float,
        *,
        burst: Optional[float] = None,
        mode: str = "sleep",
        bucket: Optional[TokenBucket] = None,
        sleep_fn: Callable[[float], None] = _sleep,
    ):
        self.rate_limit = float(rate_limit)
        self.burst = float(burst) if burst is not None else float(rate_limit)
        self.mode = mode
        self.sleep_fn = sleep_fn

        self.bucket = bucket or TokenBucket(rate=self.rate_limit, capacity=self.burst)

        if self.mode not in ("sleep", "raise"):
            raise ValueError("mode must be 'sleep' or 'raise'")

    def before_request(self, ctx: Context) -> None:
        # Acquire one token per request (simple + predictable).
        wait = self.bucket.acquire(1.0)
        if wait <= 0:
            return

        if self.mode == "raise":
            raise RateLimitedError(f"rate limited: wait {wait:.3f}s")

        # sleep mode: block until available (loop to handle jitter/time drift)
        # Important: use small loop rather than single sleep to be robust.
        remaining = wait
        while remaining > 0:
            self.sleep_fn(remaining)
            remaining = self.bucket.acquire(1.0)


class AsyncRateLimitPolicy(RateLimitPolicy):
    """
    Async rate limiter policy using awaitable sleep.
    """

    def __init__(
        self,
        rate_limit: float,
        *,
        burst: Optional[float] = None,
        mode: str = "sleep",
        bucket: Optional[TokenBucket] = None,
        sleep_fn: Optional[Callable[[float], Awaitable[None]]] = None,
    ):
        super().__init__(
            rate_limit=rate_limit,
            burst=burst,
            mode=mode,
            bucket=bucket,
            sleep_fn=_sleep,
        )
        self.async_sleep_fn = sleep_fn

    async def async_before_request(self, ctx: Context) -> None:
        wait = self.bucket.acquire(1.0)
        if wait <= 0:
            return

        if self.mode == "raise":
            raise RateLimitedError(f"rate limited: wait {wait:.3f}s")

        remaining = wait
        while remaining > 0:
            if self.async_sleep_fn is None:
                raise RuntimeError("async sleep_fn is required for AsyncRateLimitPolicy")
            await self.async_sleep_fn(remaining)
            remaining = self.bucket.acquire(1.0)
