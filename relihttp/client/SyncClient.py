# -*- coding: utf-8 -*-
# @Time    : 2026/2/3 10:59
# @Author  : fzf
# @FileName: client.py
# @Software: PyCharm
import time
import uuid
from typing import Any, Dict, Optional

from relihttp.models import Context, Request, Response
from relihttp.utils import now_ms

from .BaseClient import BaseClient


class SyncClient(BaseClient):
    
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
