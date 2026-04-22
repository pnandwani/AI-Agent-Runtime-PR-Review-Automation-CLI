from __future__ import annotations

import json
from pathlib import Path

from agent_pr_reviewer.models import ReviewReport


def write_json_report(report: ReviewReport, output_path: str) -> None:
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")


def write_markdown_report(report: ReviewReport, output_path: str) -> None:
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Pull Request Review Report",
        "",
        f"- Repository: `{report.repository}`",
        f"- Base branch: `{report.base_branch}`",
        f"- Generated at: `{report.generated_at}`",
        f"- Changed files: `{len(report.changed_files)}`",
        f"- Findings: `{len(report.findings)}`",
        "",
        "## Findings",
        "",
    ]
    if not report.findings:
        lines.append("No findings detected in changed lines.")
        lines.append("")
    else:
        for finding in report.findings:
            lines.extend(
                [
                    f"### {finding.rule_id} [{finding.severity}]",
                    f"- File: `{finding.file_path}`",
                    f"- Line: `{finding.line}`",
                    f"- Message: {finding.message}",
                    f"- Changed line: `{finding.changed_line}`",
                    "",
                ]
            )
            if finding.snippet:
                lines.extend(["```text", finding.snippet, "```", ""])

    lines.extend(["## Runtime Trace", ""])
    for event in report.runtime_trace:
        lines.append(f"- `{event.timestamp}` `{event.step}` `{event.status}` {event.detail}")
    lines.append("")

    target.write_text("\n".join(lines), encoding="utf-8")
