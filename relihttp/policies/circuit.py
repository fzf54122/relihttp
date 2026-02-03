# -*- coding: utf-8 -*-
# @Time    : 2026/2/3 11:01
# @Author  : fzf
# @FileName: circuit.py
# @Software: PyCharm
from collections import deque
from dataclasses import dataclass
from typing import Callable, Deque, Iterable, Optional, Set

from .base import Policy
from ..models import Context
from ..utils import monotonic


class CircuitOpenError(RuntimeError):
    pass


@dataclass
class _CircuitState:
    state: str = "closed"  # closed | open | half_open
    failure_count: int = 0
    success_count: int = 0
    opened_at: float = 0.0
    half_open_in_flight: bool = False
    window: Deque[bool] = None


class CircuitBreakerPolicy(Policy):
    """
    Simple circuit breaker to prevent cascading failures.

    - closed: requests pass through, failures are counted
    - open: requests are rejected until recovery timeout
    - half_open: allow limited probe; success closes, failure re-opens
    """

    def __init__(
        self,
        *,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_successes: int = 1,
        failure_statuses: Optional[Iterable[int]] = None,
        window_size: Optional[int] = None,
        failure_ratio: Optional[float] = None,
        min_requests: int = 10,
        time_fn: Callable[[], float] = monotonic,
    ):
        if failure_threshold <= 0:
            raise ValueError("failure_threshold must be > 0")
        if recovery_timeout <= 0:
            raise ValueError("recovery_timeout must be > 0")
        if half_open_successes <= 0:
            raise ValueError("half_open_successes must be > 0")
        if window_size is not None and window_size <= 0:
            raise ValueError("window_size must be > 0")
        if failure_ratio is not None and not (0.0 < failure_ratio <= 1.0):
            raise ValueError("failure_ratio must be in (0.0, 1.0]")
        if min_requests <= 0:
            raise ValueError("min_requests must be > 0")

        self.failure_threshold = int(failure_threshold)
        self.recovery_timeout = float(recovery_timeout)
        self.half_open_successes = int(half_open_successes)
        self.failure_statuses: Set[int] = set(failure_statuses or {500, 502, 503, 504, 429})
        self.window_size = int(window_size) if window_size is not None else None
        self.failure_ratio = float(failure_ratio) if failure_ratio is not None else None
        self.min_requests = int(min_requests)
        self.time_fn = time_fn

        window = deque(maxlen=self.window_size) if self.window_size else None
        self._state = _CircuitState(window=window)

    def before_request(self, ctx: Context) -> None:
        if self._state.state == "open":
            now = float(self.time_fn())
            if now - self._state.opened_at < self.recovery_timeout:
                raise CircuitOpenError("circuit open")

            # move to half-open and allow a probe
            self._state.state = "half_open"
            self._state.success_count = 0
            self._state.half_open_in_flight = False

        if self._state.state == "half_open":
            if self._state.half_open_in_flight:
                raise CircuitOpenError("circuit half-open: probe in flight")
            self._state.half_open_in_flight = True

    def after_response(self, ctx: Context) -> None:
        success = self._is_success(ctx)

        if self._state.state == "half_open":
            self._state.half_open_in_flight = False
            if success:
                self._state.success_count += 1
                if self._state.success_count >= self.half_open_successes:
                    self._close()
            else:
                self._open()
            return

        if self._state.state == "closed":
            if success:
                self._state.failure_count = 0
            else:
                self._state.failure_count += 1
                if self._state.failure_count >= self.failure_threshold:
                    self._open()

            if self._state.window is not None:
                self._record_window(success)
                if self._should_open_by_ratio():
                    self._open()

    def _is_success(self, ctx: Context) -> bool:
        if ctx.error is not None:
            return False
        if ctx.response is None:
            return False
        return ctx.response.status_code not in self.failure_statuses

    def _record_window(self, success: bool) -> None:
        if self._state.window is None:
            return
        self._state.window.append(success)

    def _should_open_by_ratio(self) -> bool:
        if self._state.window is None or self.failure_ratio is None:
            return False
        total = len(self._state.window)
        if total < self.min_requests:
            return False
        failures = sum(1 for ok in self._state.window if not ok)
        return (failures / float(total)) >= self.failure_ratio

    def _open(self) -> None:
        self._state.state = "open"
        self._state.opened_at = float(self.time_fn())
        self._state.failure_count = 0
        self._state.success_count = 0
        self._state.half_open_in_flight = False
        if self._state.window is not None:
            self._state.window.clear()

    def _close(self) -> None:
        self._state.state = "closed"
        self._state.failure_count = 0
        self._state.success_count = 0
        self._state.opened_at = 0.0
        self._state.half_open_in_flight = False
        if self._state.window is not None:
            self._state.window.clear()
