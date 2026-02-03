# -*- coding: utf-8 -*-
# @Time    : 2026/2/3 11:02
# @Author  : fzf
# @FileName: request.py
# @Software: PyCharm
from __future__ import annotations

import requests
from requests import exceptions
from typing import Optional

from .base import Transport
from ..exceotions import TransportError
from ..models import Context, Response
from ..utils import now_ms


class RequestsTransport(Transport):
    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()

    def send(self, ctx: Context) -> Response:
        req = ctx.request
        start = now_ms()
        try:
            r = self.session.request(
                method=req.method,
                url=req.url,
                params=req.params,
                headers=req.headers,
                data=req.data,
                json=req.json,
                timeout=ctx.timeout,
            )

            # 如果你希望 4xx/5xx 也走异常逻辑，就加这行
            r.raise_for_status()

        except exceptions.Timeout as e:
            raise TransportError(f"timeout | {req.method} {req.url}") from e

        except exceptions.ConnectionError as e:
            raise TransportError(f"connection error | {req.method} {req.url}") from e

        except exceptions.HTTPError as e:
            resp = getattr(e, "response", None)
            if resp is not None:
                raise TransportError(
                    f"http error | {req.method} {req.url} | {resp.status_code} | {resp.text[:300]}"
                ) from e
            raise TransportError(f"http error | {req.method} {req.url}") from e

        except exceptions.RequestException as e:
            raise TransportError(f"request error | {req.method} {req.url}") from e
        end = now_ms()
        return Response(
            status_code=r.status_code,
            headers=dict(r.headers),
            text=r.text,
            url=str(r.url),
            elapsed_ms=end - start,
        )
