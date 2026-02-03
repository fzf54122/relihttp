# -*- coding: utf-8 -*-
# @Time    : 2026/2/3 13:46
# @Author  : fzf
# @FileName: test_tracing.py
# @Software: PyCharm
from relihttp.models import Context, Request
from relihttp.policies.tracing import TracingPolicy


def test_tracing_injects_headers() -> None:
    policy = TracingPolicy(request_id_header="X-Request-ID", trace_id_header="X-Trace-ID")
    req = Request(method="GET", url="https://example.com")
    ctx = Context(request=req, max_retries=1, request_id="req-123")

    policy.before_request(ctx)

    assert ctx.request.headers["X-Request-ID"] == "req-123"
    assert "X-Trace-ID" in ctx.request.headers
