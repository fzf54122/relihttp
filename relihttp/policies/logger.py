# -*- coding: utf-8 -*-
# @Time    : 2026/2/3 11:01
# @Author  : fzf
# @FileName: logging.py
# @Software: PyCharm
import logging

from relihttp.models import Context
from relihttp.policies.base import Policy

logger = logging.getLogger('relihttp')

class LoggingPolicy(Policy):

    def before_request(self, ctx: Context) -> None:
        logger.info('http.request',
                    extra={
                        'request_id':ctx.request_id,
                        'method':ctx.request.method,
                        'url':ctx.request.url,
                        'attempt':ctx.attempt
                    })



    def after_response(self, ctx: Context) -> None:
        if ctx.response is not None:
            logger.info(
                "http.response",
                extra={
                    "request_id": ctx.request_id,
                    "method": ctx.request.method,
                    "url": ctx.request.url,
                    "status_code": ctx.response.status_code,
                    "elapsed_ms": ctx.response.elapsed_ms,
                    "attempt": ctx.attempt,
                },
            )
        elif ctx.error is not None:
            logger.warning(
                "http.error",
                extra={
                    "request_id": ctx.request_id,
                    "method": ctx.request.method,
                    "url": ctx.request.url,
                    "attempt": ctx.attempt,
                    "error_type": type(ctx.error).__name__,
                    "error": str(ctx.error),
                },
            )