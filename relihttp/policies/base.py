# -*- coding: utf-8 -*-
# @Time    : 2026/2/3 11:01
# @Author  : fzf
# @FileName: base.py
# @Software: PyCharm
from ..models import Context


class Policy:

    def before_request(self, ctx: Context) -> None:
        pass

    def after_response(self, ctx: Context) -> None:
        pass

    def should_retry(self, ctx: Context) -> bool:
        pass

    def get_retry_delay_seconds(self, ctx: Context) -> float:
        pass

    def ob_retry(self, ctx: Context) -> None:
        pass

    async def async_before_request(self, ctx: Context) -> None:
        self.before_request(ctx)

    async def async_after_response(self, ctx: Context) -> None:
        self.after_response(ctx)

    async def async_should_retry(self, ctx: Context) -> bool:
        return bool(self.should_retry(ctx))

    async def async_get_retry_delay_seconds(self, ctx: Context) -> float:
        delay = self.get_retry_delay_seconds(ctx)
        return float(delay) if delay is not None else 0.0
