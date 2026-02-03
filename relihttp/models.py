# -*- coding: utf-8 -*-
# @Time    : 2026/2/3 11:00
# @Author  : fzf
# @FileName: models.py
# @Software: PyCharm

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional

@dataclass(frozen=True)
class Request:
    method: str
    url: str
    params: Optional[Mapping[str, Any]] = None
    headers: Dict[str, str] = field(default_factory=dict)
    data: Any = None
    json: Any = None

@dataclass
class Response:
    status_code: int
    headers: Mapping[str, str]
    text: str
    url: str
    elapsed_ms: int

    def json(self) -> Any:
        import json as re_json
        return re_json.loads(self.text)


@dataclass
class Context:
    request: Request
    timeout: Optional[float] = None
    attempt: int = 0
    max_retries: int = 0
    start_ms: int = 0

    response: Optional[Response] = None
    error: Optional[BaseException] = None

    request_id: Optional[str] = None
    tags: Dict[str, Any] = field(default_factory=dict)