from __future__ import annotations

from abc import ABC, abstractmethod

from agent_pr_reviewer.models import ChangedFile, Finding


class Analyzer(ABC):
    name: str

    @abstractmethod
    def analyze(self, repo_path: str, changed_files: list[ChangedFile]) -> list[Finding]:
        raise NotImplementedError
