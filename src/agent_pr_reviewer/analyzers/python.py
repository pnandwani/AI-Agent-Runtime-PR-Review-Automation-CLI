from __future__ import annotations

import ast
from pathlib import Path

from agent_pr_reviewer.analyzers.base import Analyzer
from agent_pr_reviewer.models import ChangedFile, Finding


class PythonSyntaxAnalyzer(Analyzer):
    name = "python-syntax"

    def analyze(self, repo_path: str, changed_files: list[ChangedFile]) -> list[Finding]:
        findings: list[Finding] = []
        for changed_file in changed_files:
            if not changed_file.path.endswith(".py"):
                continue
            absolute_path = Path(repo_path, changed_file.path)
            if not absolute_path.exists():
                continue
            source = absolute_path.read_text(encoding="utf-8")
            try:
                ast.parse(source)
            except SyntaxError as error:
                findings.append(
                    Finding(
                        rule_id="PY-SYNTAX",
                        severity="high",
                        file_path=changed_file.path,
                        line=error.lineno or 1,
                        message=error.msg,
                    )
                )
        return findings


class RuleBasedDiffAnalyzer(Analyzer):
    name = "rule-based-diff"

    def analyze(self, repo_path: str, changed_files: list[ChangedFile]) -> list[Finding]:
        findings: list[Finding] = []
        for changed_file in changed_files:
            absolute_path = Path(repo_path, changed_file.path)
            if not absolute_path.exists():
                continue
            lines = absolute_path.read_text(encoding="utf-8").splitlines()
            changed_line_set = set(changed_file.added_lines)
            for line_number in sorted(changed_line_set):
                if line_number < 1 or line_number > len(lines):
                    continue
                line_text = lines[line_number - 1]
                stripped = line_text.strip()
                if len(line_text) > 100:
                    findings.append(
                        Finding(
                            rule_id="STYLE-LONG-LINE",
                            severity="low",
                            file_path=changed_file.path,
                            line=line_number,
                            message="Line exceeds 100 characters",
                            snippet=stripped,
                            changed_line=True,
                        )
                    )
                if "print(" in stripped and changed_file.path.endswith(".py"):
                    findings.append(
                        Finding(
                            rule_id="PY-DEBUG-PRINT",
                            severity="medium",
                            file_path=changed_file.path,
                            line=line_number,
                            message="Debug print statement found in changed code",
                            snippet=stripped,
                            changed_line=True,
                        )
                    )
                if "TODO" in stripped or "FIXME" in stripped:
                    findings.append(
                        Finding(
                            rule_id="MAINT-TODO",
                            severity="low",
                            file_path=changed_file.path,
                            line=line_number,
                            message="TODO or FIXME left in changed code",
                            snippet=stripped,
                            changed_line=True,
                        )
                    )
        return findings
