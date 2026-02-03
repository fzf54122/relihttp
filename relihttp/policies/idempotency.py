# -*- coding: utf-8 -*-
# @Time    : 2026/2/3 11:01
# @Author  : fzf
# @FileName: idempotency.py
# @Software: PyCharm
import uuid
from typing import Callable, Optional, Sequence, Set

from .base import Policy
from ..models import Context


SAFE_METHODS: Set[str] = {"GET", "HEAD", "OPTIONS", "PUT", "DELETE"}


class IdempotencyPolicy(Policy):
    """
    Inject Idempotency-Key for non-idempotent methods to make retries safe.
    """

    def __init__(
        self,
        *,
        header_name: str = "Idempotency-Key",
        methods: Optional[Sequence[str]] = None,
        only_if_retry: bool = True,
        key_fn: Optional[Callable[[Context], str]] = None,
    ):
        self.header_name = header_name
        self.methods = {m.upper() for m in methods} if methods is not None else None
        self.only_if_retry = bool(only_if_retry)
        self.key_fn = key_fn

    def before_request(self, ctx: Context) -> None:
        if self.only_if_retry and ctx.max_retries <= 1:
            return

        method = ctx.request.method.upper()
        if self.methods is not None:
            if method not in self.methods:
                return
        else:
            if method in SAFE_METHODS:
                return

        headers = ctx.request.headers
        if self.header_name in headers:
            return

        key = self.key_fn(ctx) if self.key_fn is not None else str(uuid.uuid4())
        headers[self.header_name] = key
        ctx.tags["idempotency_key"] = key
