from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
import tempfile

from agent_pr_reviewer.models import ChangedFile
from agent_pr_reviewer.runtime.retry import RetryableToolError


def run_git(args: list[str], cwd: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RetryableToolError(completed.stderr.strip() or "git command failed")
    return completed.stdout


@dataclass
class RepositoryInspector:
    workspace_root: str | None = None

    def clone(self, repo_url: str) -> str:
        base_dir = self.workspace_root or tempfile.mkdtemp(prefix="agent-pr-")
        Path(base_dir).mkdir(parents=True, exist_ok=True)
        clone_name = Path(repo_url.rstrip("/")).stem.replace(".git", "")
        target = Path(base_dir, clone_name)
        if target.exists():
            shutil.rmtree(target)
        run_git(["clone", repo_url, str(target)], cwd=base_dir)
        return str(target)

    def extract_changed_files(self, repo_path: str, base_branch: str) -> list[ChangedFile]:
        try:
            run_git(["fetch", "--all"], cwd=repo_path)
        except RetryableToolError:
            # Local-only repositories may not have a remote configured yet.
            pass
        diff_output = run_git(["diff", "--unified=0", f"{base_branch}...HEAD"], cwd=repo_path)
        return parse_unified_diff(diff_output)


def parse_unified_diff(diff_text: str) -> list[ChangedFile]:
    files: list[ChangedFile] = []
    current: ChangedFile | None = None
    new_line = 0
    old_line = 0

    for raw_line in diff_text.splitlines():
        if raw_line.startswith("diff --git "):
            if current is not None:
                files.append(current)
            current = None
            continue
        if raw_line.startswith("+++ b/"):
            path = raw_line[6:]
            current = ChangedFile(path=path)
            new_line = 0
            old_line = 0
            continue
        if current is None:
            continue
        current.patch += raw_line + "\n"
        if raw_line.startswith("@@"):
            header = raw_line.split("@@")[1].strip()
            old_part, new_part = header.split(" ")
            old_line = int(old_part.split(",")[0][1:])
            new_line = int(new_part.split(",")[0][1:])
            continue
        if raw_line.startswith("+") and not raw_line.startswith("+++"):
            current.added_lines.append(new_line)
            new_line += 1
            continue
        if raw_line.startswith("-") and not raw_line.startswith("---"):
            current.removed_lines.append(old_line)
            old_line += 1
            continue
        if not raw_line.startswith("\\"):
            old_line += 1
            new_line += 1

    if current is not None:
        files.append(current)
    return files
