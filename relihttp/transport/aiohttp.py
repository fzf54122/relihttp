# -*- coding: utf-8 -*-
# @Time    : 2026/2/3 13:35
# @Author  : fzf
# @FileName: aiohttp.py
# @Software: PyCharm
from __future__ import annotations
import asyncio
from ..exceotions import TransportError
from typing import Optional
from aiohttp import ClientError

try:
    import aiohttp  # type: ignore
except Exception:  # pragma: no cover - handled at runtime
    aiohttp = None

from .async_base import AsyncTransport
from ..models import Context, Response
from ..utils import now_ms


class AiohttpTransport(AsyncTransport):
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        if aiohttp is None:
            raise ImportError("aiohttp is required. Install with `pip install relihttp[async]`.")
        self._external_session = session is not None
        self.session = session

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def send(self, ctx: Context) -> Response:
        req = ctx.request
        start = now_ms()
        session = await self._ensure_session()

        try:
            async with session.request(
                method=req.method,
                url=req.url,
                params=req.params,
                headers=req.headers,
                data=req.data,
                json=req.json,
                timeout=ctx.timeout,
            ) as r:
                # 如果你希望 4xx/5xx 也走异常分支，打开这行
                r.raise_for_status()

                text = await r.text()
                end = now_ms()
                return Response(
                    status_code=r.status,
                    headers=dict(r.headers),
                    text=text,
                    url=str(r.url),
                    elapsed_ms=end - start,
                )

        # --- 超时：aiohttp 和 asyncio 两个都可能出现 ---
        except (asyncio.TimeoutError, aiohttp.ClientTimeout) as e:
            raise TransportError(f"timeout | {req.method} {req.url}") from e

        # --- 连接失败 / DNS 解析失败 / 连接重置等 ---
        except aiohttp.ClientConnectorError as e:
            raise TransportError(f"connection error | {req.method} {req.url}") from e

        # --- HTTP 非 2xx，只有当你调用 r.raise_for_status() 才会进来 ---
        except aiohttp.ClientResponseError as e:
            # e.status / e.message / e.headers 都在
            raise TransportError(f"http error | {req.method} {req.url} | {e.status} | {e.message}") from e

        # --- 兜底：aiohttp 所有 client 异常（TooManyRedirects、InvalidURL、PayloadError 等）---
        except ClientError as e:
            raise TransportError(f"request error | {req.method} {req.url}") from e


    async def close(self) -> None:
        if self._external_session or self.session is None:
            return
        await self.session.close()
