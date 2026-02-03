# -*- coding: utf-8 -*-
# @Time    : 2026/2/3 11:44
# @Author  : fzf
# @FileName: test_ratelimit.py
# @Software: PyCharm
from relihttp.utils import TokenBucket
from relihttp.policies.rate_limit import RateLimitPolicy, RateLimitedError
from relihttp.models import Context, Request


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def now(self) -> float:
        return self.t

    def sleep(self, seconds: float) -> None:
        self.t += float(seconds)


def make_ctx():
    req = Request(method="GET", url="https://example.com")
    return Context(request=req, max_retries=0)


def test_token_bucket_basic():
    clock = FakeClock()
    bucket = TokenBucket(rate=10.0, capacity=10.0, time_fn=clock.now)

    # consume 10 immediately
    for _ in range(10):
        assert bucket.acquire(1.0) == 0.0

    # 11th must wait 0.1s (rate=10/s)
    w = bucket.acquire(1.0)
    assert w > 0

    clock.sleep(w)
    assert bucket.acquire(1.0) == 0.0


def test_ratelimit_policy_sleep_mode_blocks():
    clock = FakeClock()
    bucket = TokenBucket(rate=1.0, capacity=1.0, time_fn=clock.now)  # 1 req/sec, burst 1
    policy = RateLimitPolicy(rate_limit=1.0, bucket=bucket, sleep_fn=clock.sleep, mode="sleep")

    ctx = make_ctx()
    policy.before_request(ctx)  # ok, consumes burst token
    # second call: should sleep ~1s in fake clock
    policy.before_request(ctx)
    assert clock.t >= 1.0


def test_ratelimit_policy_raise_mode_raises():
    clock = FakeClock()
    bucket = TokenBucket(rate=1.0, capacity=1.0, time_fn=clock.now)
    policy = RateLimitPolicy(rate_limit=1.0, bucket=bucket, sleep_fn=clock.sleep, mode="raise")

    ctx = make_ctx()
    policy.before_request(ctx)  # ok
    try:
        policy.before_request(ctx)
        assert False, "expected RateLimitedError"
    except RateLimitedError:
        pass
