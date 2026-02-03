# -*- coding: utf-8 -*-
# @Time    : 2026/2/3 13:46
# @Author  : fzf
# @FileName: test_idempotency.py
# @Software: PyCharm
from relihttp.models import Context, Request
from relihttp.policies.idempotency import IdempotencyPolicy


def test_idempotency_key_injected_for_post() -> None:
    policy = IdempotencyPolicy()
    req = Request(method="POST", url="https://example.com")
    ctx = Context(request=req, max_retries=3)

    policy.before_request(ctx)
    assert "Idempotency-Key" in ctx.request.headers
    key_first = ctx.request.headers["Idempotency-Key"]

    # calling again should keep same key
    policy.before_request(ctx)
    assert ctx.request.headers["Idempotency-Key"] == key_first


def test_idempotency_key_not_injected_for_get() -> None:
    policy = IdempotencyPolicy()
    req = Request(method="GET", url="https://example.com")
    ctx = Context(request=req, max_retries=3)

    policy.before_request(ctx)
    assert "Idempotency-Key" not in ctx.request.headers
