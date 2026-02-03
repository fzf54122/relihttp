# -*- coding: utf-8 -*-
# @Time    : 2026/2/3 11:01
# @Author  : fzf
# @FileName: tracing.py
# @Software: PyCharm
import uuid
from typing import Callable, Dict, Optional

from .base import Policy
from ..models import Context


class TracingPolicy(Policy):
    """
    Inject request/trace identifiers into headers for end-to-end tracing.
    """

    def __init__(
        self,
        *,
        request_id_header: str = "X-Request-ID",
        trace_id_header: Optional[str] = None,
        trace_id_fn: Optional[Callable[[Context], str]] = None,
        extra_headers: Optional[Dict[str, str]] = None,
    ):
        self.request_id_header = request_id_header
        self.trace_id_header = trace_id_header
        self.trace_id_fn = trace_id_fn
        self.extra_headers = dict(extra_headers or {})

    def before_request(self, ctx: Context) -> None:
        headers = ctx.request.headers

        if self.request_id_header and ctx.request_id:
            headers.setdefault(self.request_id_header, ctx.request_id)

        if self.trace_id_header:
            if self.trace_id_header not in headers:
                trace_id = (
                    self.trace_id_fn(ctx)
                    if self.trace_id_fn is not None
                    else (ctx.request_id or str(uuid.uuid4()))
                )
                headers[self.trace_id_header] = trace_id
                ctx.tags["trace_id"] = trace_id

        for key, value in self.extra_headers.items():
            headers.setdefault(key, value)
