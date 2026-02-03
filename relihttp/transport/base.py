# -*- coding: utf-8 -*-
# @Time    : 2026/2/3 11:02
# @Author  : fzf
# @FileName: base.py
# @Software: PyCharm
from abc import ABC, abstractmethod
from ..models import Context, Response


class Transport(ABC):
    @abstractmethod
    def send(self, ctx: Context) -> Response:
        ...