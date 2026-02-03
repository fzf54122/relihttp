# -*- coding: utf-8 -*-
# @Time    : 2026/2/3 14:25
# @Author  : fzf
# @FileName: test_async_ratelimit.py
# @Software: PyCharm
import asyncio

from relihttp.models import Context, Request
from relihttp.policies.rate_limit import AsyncRateLimitPolicy
from relihttp.utils import TokenBucket


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def now(self) -> float:
        return self.t

    async def sleep(self, seconds: float) -> None:
        self.t += float(seconds)


def make_ctx() -> Context:
    req = Request(method="GET", url="https://example.com")
    return Context(request=req, max_retries=0)


def test_async_ratelimit_policy_sleep_mode_blocks() -> None:
    async def run() -> None:
        clock = FakeClock()
        bucket = TokenBucket(rate=1.0, capacity=1.0, time_fn=clock.now)
        policy = AsyncRateLimitPolicy(rate_limit=1.0, bucket=bucket, sleep_fn=clock.sleep)

        ctx = make_ctx()
        await policy.async_before_request(ctx)
        await policy.async_before_request(ctx)
        assert clock.t >= 1.0

    asyncio.run(run())
