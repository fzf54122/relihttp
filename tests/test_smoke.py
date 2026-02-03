# -*- coding: utf-8 -*-
# @Time    : 2026/2/3 11:35
# @Author  : fzf
# @FileName: test_smoke.py
# @Software: PyCharm
from relihttp import Client


def test_client_init():
    c = Client()
    assert c is not None
