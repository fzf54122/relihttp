# -*- coding: utf-8 -*-
# @Time    : 2026/2/3 13:36
# @Author  : fzf
# @FileName: async_client.py
# @Software: PyCharm
import asyncio
import uuid
from typing import Any, Dict, List, Optional, Sequence

from .models import Context, Request, Response
from .transport.async_base import AsyncTransport
from .policies.base import Policy
from .policies.timeout import TimeoutPolicy
from .policies.retry import RetryPolicy
from .policies.logger import LoggingPolicy
from .policies.rate_limit import AsyncRateLimitPolicy, RateLimitPolicy
from .utils import now_ms


class AsyncClient:
    def __init__(
        self,
        base_url: str = "",
        timeout: float = 3.0,
        retry: str = "safe",
        max_retries: int = 3,
        rate_limit: float = None,
        transport: Optional[AsyncTransport] = None,
        policies: Optional[Sequence[Policy]] = None,
        circuit_breaker: bool = False,
        idempotency: bool = False,
        trace: bool = False,
    ):
        self.base_url = base_url.rstrip("/")
        if transport is None:
            try:
                from .transport.aiohttp import AiohttpTransport
            except ImportError as exc:
                raise ImportError(
                    "AsyncClient requires aiohttp. Install with `pip install relihttp[async]`."
                ) from exc
            transport = AiohttpTransport()
        self.transport = transport

        default_policies: List[Policy] = [
            TimeoutPolicy(timeout=timeout),
            RetryPolicy(max_retries=max_retries, retry=retry),
            LoggingPolicy(),
        ]
        if rate_limit:
            default_policies.append(AsyncRateLimitPolicy(rate_limit=rate_limit, sleep_fn=asyncio.sleep))
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

    async def request(
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

        while True:
            ctx.attempt += 1
            ctx.response = None
            ctx.error = None

            for p in self.policies:
                await p.async_before_request(ctx)

            try:
                ctx.response = await self.transport.send(ctx)
            except BaseException as e:
                ctx.error = e

            for p in reversed(self.policies):
                await p.async_after_response(ctx)

            should_retry = False
            delay = 0.0
            for p in self.policies:
                if await p.async_should_retry(ctx):
                    should_retry = True
                    delay = max(delay, float(await p.async_get_retry_delay_seconds(ctx)))
            if should_retry:
                await asyncio.sleep(delay)
                continue

            if ctx.response is not None:
                return ctx.response
            assert ctx.error is not None
            raise ctx.error

    async def close(self) -> None:
        await self.transport.close()

    async def __aenter__(self) -> "AsyncClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    # sugar
    async def get(self, url: str, **kwargs) -> Optional[Response]:
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> Optional[Response]:
        return await self.request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs) -> Optional[Response]:
        return await self.request("PUT", url, **kwargs)

    async def delete(self, url: str, **kwargs) -> Optional[Response]:
        return await self.request("DELETE", url, **kwargs)

    async def patch(self, url: str, **kwargs) -> Optional[Response]:
        return await self.request("PATCH", url, **kwargs)
