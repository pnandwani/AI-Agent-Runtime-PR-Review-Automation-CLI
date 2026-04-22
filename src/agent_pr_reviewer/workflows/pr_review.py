from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from agent_pr_reviewer.analyzers.base import Analyzer
from agent_pr_reviewer.analyzers.python import PythonSyntaxAnalyzer, RuleBasedDiffAnalyzer
from agent_pr_reviewer.gitops import RepositoryInspector
from agent_pr_reviewer.models import ReviewReport
from agent_pr_reviewer.runtime.tools import AgentRuntime, FunctionTool, ToolRegistry


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class PRReviewWorkflow:
    inspector: RepositoryInspector
    analyzers: list[Analyzer] = field(
        default_factory=lambda: [PythonSyntaxAnalyzer(), RuleBasedDiffAnalyzer()]
    )

    def __post_init__(self) -> None:
        registry = ToolRegistry()
        registry.register(FunctionTool(name="clone_repository", handler=self._clone_repository))
        registry.register(FunctionTool(name="collect_diff", handler=self._collect_diff))
        registry.register(FunctionTool(name="run_analyzers", handler=self._run_analyzers))
        self.runtime = AgentRuntime(registry=registry)

    def run(
        self,
        repo_url: str | None,
        repo_path: str | None,
        base_branch: str,
    ) -> ReviewReport:
        if not repo_url and not repo_path:
            raise ValueError("either repo_url or repo_path must be provided")

        if repo_path is None:
            repo_path = self.runtime.execute("clone_repository", repo_url=repo_url)

        changed_files = self.runtime.execute("collect_diff", repo_path=repo_path, base_branch=base_branch)
        findings = self.runtime.execute("run_analyzers", repo_path=repo_path, changed_files=changed_files)
        self.runtime.memory.put("repo_path", repo_path)
        self.runtime.memory.put("changed_files", changed_files)
        self.runtime.memory.put("findings", findings)

        return ReviewReport(
            repository=repo_url or repo_path,
            base_branch=base_branch,
            generated_at=utc_now(),
            changed_files=changed_files,
            findings=findings,
            runtime_trace=self.runtime.trace,
        )

    def _clone_repository(self, memory, repo_url: str) -> str:
        repo_path = self.inspector.clone(repo_url)
        memory.put("repo_path", repo_path)
        return repo_path

    def _collect_diff(self, memory, repo_path: str, base_branch: str):
        changed_files = self.inspector.extract_changed_files(repo_path=repo_path, base_branch=base_branch)
        memory.put("changed_files", changed_files)
        return changed_files

    def _run_analyzers(self, memory, repo_path: str, changed_files):
        findings = []
        for analyzer in self.analyzers:
            findings.extend(analyzer.analyze(repo_path=repo_path, changed_files=changed_files))
        changed_lines = {
            (changed_file.path, line)
            for changed_file in changed_files
            for line in changed_file.added_lines
        }
        for finding in findings:
            finding.changed_line = (finding.file_path, finding.line) in changed_lines
        memory.put("findings", findings)
        return findings
