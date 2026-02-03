
class TransportError(Exception):
    """统一的 HTTP 传输异常"""

    def __init__(
        self,
        message: str,
        *,
        method: str | None = None,
        url: str | None = None,
        status_code: int | None = None,
        elapsed_ms: int | None = None,
    ):
        self.method = method
        self.url = url
        self.status_code = status_code
        self.elapsed_ms = elapsed_ms

        parts = [message]
        if method:
            parts.append(f"method={method}")
        if url:
            parts.append(f"url={url}")
        if status_code:
            parts.append(f"status={status_code}")
        if elapsed_ms is not None:
            parts.append(f"elapsed={elapsed_ms}ms")

        super().__init__(" | ".join(parts))
