# -*- coding: utf-8 -*-
# @Time    : 2026/2/3 11:01
# @Author  : fzf
# @FileName: retry.py
# @Software: PyCharm
from typing import Iterable, Optional, Set
import requests

from .base import Policy
from ..models import Context
from ..utils import exponential_backoff, add_jitter


SAFE_METHODS: Set[str] = {"GET", "HEAD", "OPTIONS", "PUT", "DELETE"}


class RetryPolicy(Policy):
    def __init__(
        self,
        max_retries: int = 3,
        retry: str = "safe",  # "safe" or "all" or "off"
        retry_on_status: Optional[Iterable[int]] = None,
        base_delay: float = 0.2,
        max_delay: float = 5.0,
        jitter: float = 0.2,
    ):
        self.max_retries = int(max_retries)
        self.retry_mode = retry
        self.retry_on_status = set(retry_on_status or {500, 502, 503, 504, 429})
        self.base_delay = float(base_delay)
        self.max_delay = float(max_delay)
        self.jitter = float(jitter)

    def should_retry(self, ctx: Context) -> bool:
        if ctx.attempt >= ctx.max_retries:
            return False

        method = ctx.request.method.upper()

        if self.retry_mode == "off":
            return False
        if self.retry_mode == "safe" and method not in SAFE_METHODS:
            return False

        # network errors
        if ctx.error is not None:
            return isinstance(
                ctx.error,
                (requests.Timeout, requests.ConnectionError, requests.RequestException),
            )

        # status retry
        if ctx.response is not None and ctx.response.status_code in self.retry_on_status:
            return True

        return False

    def get_retry_delay_seconds(self, ctx: Context) -> float:
        delay = exponential_backoff(ctx.attempt, base=self.base_delay, cap=self.max_delay)
        return add_jitter(delay, jitter=self.jitter)
