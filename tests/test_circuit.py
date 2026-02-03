# -*- coding: utf-8 -*-
# @Time    : 2026/2/3 13:45
# @Author  : fzf
# @FileName: test_circuit.py
# @Software: PyCharm
from relihttp.models import Context, Request, Response
from relihttp.policies.circuit import CircuitBreakerPolicy, CircuitOpenError


class FakeClock:
    def __init__(self) -> None:
        self.t = 0.0

    def now(self) -> float:
        return self.t

    def advance(self, seconds: float) -> None:
        self.t += float(seconds)


def make_ctx() -> Context:
    req = Request(method="GET", url="https://example.com")
    return Context(request=req, max_retries=1)


def make_response(status: int) -> Response:
    return Response(
        status_code=status,
        headers={},
        text="",
        url="https://example.com",
        elapsed_ms=1,
    )


def test_circuit_breaker_opens_and_recovers() -> None:
    clock = FakeClock()
    policy = CircuitBreakerPolicy(
        failure_threshold=2,
        recovery_timeout=10.0,
        time_fn=clock.now,
    )

    # first failure
    ctx = make_ctx()
    policy.before_request(ctx)
    ctx.response = make_response(500)
    policy.after_response(ctx)

    # second failure -> opens
    ctx = make_ctx()
    policy.before_request(ctx)
    ctx.response = make_response(500)
    policy.after_response(ctx)

    # open: should reject
    ctx = make_ctx()
    try:
        policy.before_request(ctx)
        assert False, "expected CircuitOpenError"
    except CircuitOpenError:
        pass

    # advance time to half-open, success closes
    clock.advance(10.0)
    ctx = make_ctx()
    policy.before_request(ctx)
    ctx.response = make_response(200)
    policy.after_response(ctx)


def test_circuit_breaker_sliding_window_failure_ratio() -> None:
    clock = FakeClock()
    policy = CircuitBreakerPolicy(
        window_size=4,
        failure_ratio=0.5,
        min_requests=4,
        recovery_timeout=10.0,
        time_fn=clock.now,
    )

    for status in [200, 500, 200, 500]:
        ctx = make_ctx()
        policy.before_request(ctx)
        ctx.response = make_response(status)
        policy.after_response(ctx)

    ctx = make_ctx()
    try:
        policy.before_request(ctx)
        assert False, "expected CircuitOpenError"
    except CircuitOpenError:
        pass

    # closed: should allow
    ctx = make_ctx()
    policy.before_request(ctx)
    ctx.response = make_response(200)
    policy.after_response(ctx)
