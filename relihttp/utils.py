# -*- coding: utf-8 -*-
# @Time    : 2026/2/3 11:22
# @Author  : fzf
# @FileName: utils.py
# @Software: PyCharm
import random
import threading
import time
from dataclasses import dataclass
from typing import Callable


def now_ms() -> int:
    """测试用的当前时间戳"""
    return int(time.time() * 1000)


def exponential_backoff(attempt: int, base: float = 0.2, cap: float = 5.0) -> float:
    # attempt: 1,2,3...
    delay = base * (2 ** (attempt - 1))
    return min(delay, cap)


def add_jitter(delay: float, jitter: float = 0.2) -> float:
    # jitter=0.2 => +/-20%
    if delay <= 0:
        return 0.0
    r = 1 + random.uniform(-jitter, jitter)
    return max(0.0, delay * r)

def monotonic() -> float:
    """Monotonic seconds for rate limiting/backoff."""
    return time.monotonic()


def sleep(seconds: float) -> None:
    time.sleep(seconds)


@dataclass
class TokenBucket:
    """
    Token Bucket rate limiter.

    rate: tokens per second
    capacity: max burst tokens
    """
    rate: float
    capacity: float
    time_fn: Callable[[], float] = monotonic

    def __post_init__(self) -> None:
        if self.rate <= 0:
            raise ValueError("rate must be > 0")
        if self.capacity <= 0:
            raise ValueError("capacity must be > 0")

        self._lock = threading.Lock()
        self._tokens = float(self.capacity)
        self._last = float(self.time_fn())

    def _refill(self, now: float) -> None:
        elapsed = max(0.0, now - self._last)
        self._last = now
        self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)

    def acquire(self, tokens: float = 1.0) -> float:
        """
        Try to acquire tokens.

        Returns:
            wait_seconds (float):
              - 0.0 if tokens are available immediately
              - >0.0 if caller should wait this long then retry acquire
        """
        if tokens <= 0:
            return 0.0

        with self._lock:
            now = float(self.time_fn())
            self._refill(now)

            if self._tokens >= tokens:
                self._tokens -= tokens
                return 0.0

            deficit = tokens - self._tokens
            # Need deficit tokens, at rate tokens/sec => deficit/rate seconds.
            wait = deficit / self.rate
            # Do not change tokens here; caller will wait and call acquire again.
            return max(0.0, wait)