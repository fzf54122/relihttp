# -*- coding: utf-8 -*-
# @Time    : 2026/2/3 13:47
# @Author  : fzf
# @FileName: test_async_client.py
# @Software: PyCharm
import asyncio

from relihttp.async_client import AsyncClient
from relihttp.models import Context, Response
from relihttp.transport.async_base import AsyncTransport


class DummyAsyncTransport(AsyncTransport):
    async def send(self, ctx: Context) -> Response:
        return Response(
            status_code=200,
            headers={},
            text="ok",
            url=ctx.request.url,
            elapsed_ms=1,
        )


def test_async_client_basic() -> None:
    async def run() -> None:
        client = AsyncClient(transport=DummyAsyncTransport())
        resp = await client.get("https://example.com")
        assert resp.status_code == 200

    asyncio.run(run())
