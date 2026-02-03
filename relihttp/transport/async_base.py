# -*- coding: utf-8 -*-
# @Time    : 2026/2/3 13:35
# @Author  : fzf
# @FileName: async_base.py
# @Software: PyCharm
from abc import ABC, abstractmethod
from typing import Optional

from ..models import Context, Response


class AsyncTransport(ABC):
    @abstractmethod
    async def send(self, ctx: Context) -> Response:
        ...

    async def close(self) -> None:
        return None
