# -*- coding: utf-8 -*-
# @Time    : 2026/2/3 10:59
# @Author  : fzf
# @FileName: client.py
# @Software: PyCharm
import time
import uuid
from typing import Any, Dict, List, Optional, Sequence

from .models import Context, Request, Response
from .transport.requests import RequestsTransport
from .transport.base import Transport
from .policies.base import Policy
from .policies.timeout import TimeoutPolicy
from .policies.retry import RetryPolicy
from .policies.logger import LoggingPolicy
from .policies.rate_limit import RateLimitPolicy
from .utils import now_ms


class Client:
    def __init__(
        self,
        base_url: str = "",
        timeout: float = 3.0,
        retry: str = "safe",
        max_retries: int = 3,
        rate_limit: float = None,
        transport: Optional[Transport] = None,
        policies: Optional[Sequence[Policy]] = None,
        circuit_breaker: bool = False,
        idempotency: bool = False,
        trace: bool = False,
    ):
        self.base_url = base_url.rstrip("/")
        self.transport = transport or RequestsTransport()

        default_policies: List[Policy] = [
            TimeoutPolicy(timeout=timeout),
            RetryPolicy(max_retries=max_retries, retry=retry),
            LoggingPolicy(),
        ]
        if rate_limit:
            default_policies.append(RateLimitPolicy(rate_limit=rate_limit))
        if circuit_breaker:
            from .policies.circuit import CircuitBreakerPolicy

            default_policies.append(CircuitBreakerPolicy())
        if idempotency:
            from .policies.idempotency import IdempotencyPolicy

            default_policies.append(IdempotencyPolicy())
        if trace:
            from .policies.tracing import TracingPolicy

            default_policies.append(TracingPolicy())
        self.policies = list(policies) if policies is not None else default_policies

        self._default_max_retries = int(max_retries)

    def request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        data: Any = None,
        json: Any = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
    ) -> Optional[Response]:
        full_url = url
        if self.base_url and url.startswith("/"):
            full_url = self.base_url + url

        req = Request(
            method=method.upper(),
            url=full_url,
            params=params,
            headers=headers or {},
            data=data,
            json=json,
        )
        ctx = Context(
            request=req,
            timeout=timeout,
            max_retries=self._default_max_retries if max_retries is None else int(max_retries),
            start_ms=now_ms(),
            request_id=str(uuid.uuid4()),
        )

        # attempts: 1..max_retries+1
        while True:
            ctx.attempt += 1
            ctx.response = None
            ctx.error = None

            # before hooks
            for p in self.policies:
                p.before_request(ctx)

            # send
            try:
                ctx.response = self.transport.send(ctx)
            except BaseException as e:
                ctx.error = e

            # after hooks
            for p in reversed(self.policies):
                p.after_response(ctx)

            # retry decision (any policy can decide; we OR them)
            should_retry = False
            delay = 0.0
            for p in self.policies:
                if p.should_retry(ctx):
                    should_retry = True
                    delay = max(delay, float(p.get_retry_delay_seconds(ctx)))
            if should_retry:
                time.sleep(delay)
                continue

            # final
            if ctx.response is not None:
                return ctx.response
            assert ctx.error is not None
            raise ctx.error

    # sugar
    def get(self, url: str, **kwargs) -> Optional[Response]:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> Optional[Response]:
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs) -> Optional[Response]:
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs) -> Optional[Response]:
        return self.request("DELETE", url, **kwargs)

    def patch(self, url: str, **kwargs) -> Optional[Response]:
        return self.request("PATCH", url, **kwargs)
