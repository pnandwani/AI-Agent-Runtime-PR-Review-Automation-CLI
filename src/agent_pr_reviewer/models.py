from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class ChangedFile:
    path: str
    added_lines: list[int] = field(default_factory=list)
    removed_lines: list[int] = field(default_factory=list)
    patch: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Finding:
    rule_id: str
    severity: str
    file_path: str
    line: int
    message: str
    snippet: str = ""
    changed_line: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RuntimeEvent:
    step: str
    status: str
    detail: str
    timestamp: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ReviewReport:
    repository: str
    base_branch: str
    generated_at: str
    changed_files: list[ChangedFile]
    findings: list[Finding]
    runtime_trace: list[RuntimeEvent]

    def to_dict(self) -> dict[str, Any]:
        return {
            "repository": self.repository,
            "base_branch": self.base_branch,
            "generated_at": self.generated_at,
            "changed_files": [item.to_dict() for item in self.changed_files],
            "findings": [item.to_dict() for item in self.findings],
            "runtime_trace": [item.to_dict() for item in self.runtime_trace],
            "summary": {
                "changed_file_count": len(self.changed_files),
                "finding_count": len(self.findings),
                "high_severity_count": sum(1 for item in self.findings if item.severity == "high"),
            },
        }
