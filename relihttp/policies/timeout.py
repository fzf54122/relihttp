# -*- coding: utf-8 -*-
# @Time    : 2026/2/3 11:01
# @Author  : fzf
# @FileName: timeout.py
# @Software: PyCharm
from relihttp.models import Context
from relihttp.policies.base import Policy


class TimeoutPolicy(Policy):
    """"""

    def __init__(self, timeout: float = 3.0):
        self.timeout = timeout

    def before_request(self, ctx: Context) -> None:
        if ctx.timeout is None:
            ctx.timeout = self.timeout
