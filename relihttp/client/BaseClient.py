import time
import uuid
from typing import Any, Dict, List, Optional, Sequence

from ..models import Context, Request, Response
from ..transport.requests import RequestsTransport
from ..transport.base import Transport
from ..policies.base import Policy
from ..policies.timeout import TimeoutPolicy
from ..policies.retry import RetryPolicy
from ..utils import now_ms


class BaseClient:
    def __init__(
        self,
        base_url: str = "",
        timeout: float = 3.0,
        retry: str = "safe",
        max_retries: int = 3,
        rate_limit: float = None,
        transport: Optional[Transport] = None,
        policies: Optional[Sequence[Policy]] = None,
        circuit_breaker: bool = False,
        idempotency: bool = False,
        trace: bool = False,
        logger:bool = False,
    ):
        self.base_url = base_url.rstrip("/")
        self.transport = transport or RequestsTransport()

        default_policies: List[Policy] = [
            TimeoutPolicy(timeout=timeout),
            RetryPolicy(max_retries=max_retries, retry=retry),
        ]
        if logger:
            from ..policies.logger import LoggingPolicy
            default_policies.append(LoggingPolicy())

        if rate_limit:
            from ..policies.rate_limit import RateLimitPolicy
            default_policies.append(RateLimitPolicy(rate_limit=rate_limit))
        if circuit_breaker:
            from ..policies.circuit import CircuitBreakerPolicy

            default_policies.append(CircuitBreakerPolicy())
        if idempotency:
            from ..policies.idempotency import IdempotencyPolicy

            default_policies.append(IdempotencyPolicy())
        if trace:
            from ..policies.tracing import TracingPolicy

            default_policies.append(TracingPolicy())
        self.policies = list(policies) if policies is not None else default_policies

        self._default_max_retries = int(max_retries)

    def request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        data: Any = None,
        json: Any = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
    ) -> Optional[Response]:
        pass

    # sugar
    def get(self, url: str, **kwargs) -> Optional[Response]:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> Optional[Response]:
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs) -> Optional[Response]:
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs) -> Optional[Response]:
        return self.request("DELETE", url, **kwargs)

    def patch(self, url: str, **kwargs) -> Optional[Response]:
        return self.request("PATCH", url, **kwargs)
