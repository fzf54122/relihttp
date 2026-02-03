# -*- coding: utf-8 -*-
# @Time    : 2026/2/3 13:36
# @Author  : fzf
# @FileName: async_client.py
# @Software: PyCharm
import asyncio
import uuid
from typing import Any, Dict, Optional

from relihttp.transport.aiohttp import AiohttpTransport

from .BaseClient import BaseClient
from ..models import Context, Request, Response
from ..utils import now_ms


class AsyncClient(BaseClient):


    def __init__(self, *, transport=None, **kwargs):
        super().__init__(**kwargs)
        self.transport = transport or AiohttpTransport(...)

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