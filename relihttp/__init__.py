# -*- coding: utf-8 -*-
# @Time    : 2026/2/3 10:59
# @Author  : fzf
# @FileName: __init__.py
# @Software: PyCharm
from .client import Client
from .exceotions import TransportError

try:
    from .async_client import AsyncClient
except Exception:
    AsyncClient = None  # type: ignore[assignment]

__all__ = ["Client",
           "TransportError"]
if AsyncClient is not None:
    __all__.append("AsyncClient")
