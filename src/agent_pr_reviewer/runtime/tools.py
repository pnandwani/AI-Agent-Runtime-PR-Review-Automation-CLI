from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from agent_pr_reviewer.models import RuntimeEvent
from agent_pr_reviewer.runtime.memory import MemoryStore
from agent_pr_reviewer.runtime.retry import RetryPolicy


class Tool(ABC):
    name: str

    @abstractmethod
    def run(self, memory: MemoryStore, **kwargs: Any) -> Any:
        raise NotImplementedError


@dataclass
class FunctionTool(Tool):
    name: str
    handler: Callable[..., Any]

    def run(self, memory: MemoryStore, **kwargs: Any) -> Any:
        return self.handler(memory=memory, **kwargs)


@dataclass
class ToolRegistry:
    tools: dict[str, Tool] = field(default_factory=dict)

    def register(self, tool: Tool) -> None:
        self.tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        try:
            return self.tools[name]
        except KeyError as error:
            raise KeyError(f"tool '{name}' is not registered") from error


@dataclass
class AgentRuntime:
    registry: ToolRegistry
    memory: MemoryStore = field(default_factory=MemoryStore)
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    trace: list[RuntimeEvent] = field(default_factory=list)

    def execute(self, tool_name: str, **kwargs: Any) -> Any:
        tool = self.registry.get(tool_name)
        self.trace.append(RuntimeEvent(step=tool_name, status="started", detail=f"running {tool_name}"))
        try:
            result = self.retry_policy.run(lambda: tool.run(self.memory, **kwargs))
        except Exception as error:
            self.trace.append(RuntimeEvent(step=tool_name, status="failed", detail=str(error)))
            raise
        self.trace.append(RuntimeEvent(step=tool_name, status="completed", detail=f"completed {tool_name}"))
        return result
