from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any
from urllib import request

from agent_pr_reviewer.runtime.memory import MemoryStore
from agent_pr_reviewer.runtime.retry import RetryableToolError
from agent_pr_reviewer.runtime.tools import Tool


@dataclass(frozen=True)
class OAuthToken:
    access_token: str
    token_type: str = "Bearer"
    refresh_token: str | None = None


@dataclass(frozen=True)
class WebhookEvent:
    event_type: str
    payload: dict[str, Any]
    signature: str | None = None


@dataclass
class RestApiTool(Tool):
    name: str
    url: str
    method: str = "GET"
    headers: dict[str, str] = field(default_factory=dict)
    timeout_seconds: int = 10

    def run(self, memory: MemoryStore, **kwargs: Any) -> dict[str, Any]:
        body = kwargs.get("body")
        token: OAuthToken | None = kwargs.get("token")
        payload = None if body is None else json.dumps(body).encode("utf-8")
        headers = dict(self.headers)
        headers.setdefault("Content-Type", "application/json")
        if token is not None:
            headers["Authorization"] = f"{token.token_type} {token.access_token}"
        req = request.Request(self.url, data=payload, method=self.method, headers=headers)
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                data = response.read().decode("utf-8")
                return json.loads(data) if data else {}
        except Exception as error:
            raise RetryableToolError(f"API request failed for {self.url}: {error}") from error
