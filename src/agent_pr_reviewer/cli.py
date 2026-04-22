from __future__ import annotations

import argparse
from pathlib import Path
import sys

from agent_pr_reviewer.gitops import RepositoryInspector
from agent_pr_reviewer.reporting import write_json_report, write_markdown_report
from agent_pr_reviewer.workflows.pr_review import PRReviewWorkflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-pr-review")
    subparsers = parser.add_subparsers(dest="command", required=True)

    review = subparsers.add_parser("review", help="Run end-to-end PR review workflow")
    review.add_argument("--repo-url", help="Git repository URL to clone and review")
    review.add_argument("--repo-path", help="Existing local repository path to review")
    review.add_argument("--base-branch", default="main", help="Base branch to diff against")
    review.add_argument("--output", default="reports/review.json", help="JSON report output path")
    review.add_argument("--markdown", default="reports/review.md", help="Markdown report output path")
    review.add_argument(
        "--workspace-root",
        default=str(Path.cwd() / "tmp"),
        help="Directory used for cloned repositories",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "review":
        if not args.repo_url and not args.repo_path:
            parser.error("one of --repo-url or --repo-path is required")
        workflow = PRReviewWorkflow(inspector=RepositoryInspector(workspace_root=args.workspace_root))
        report = workflow.run(
            repo_url=args.repo_url,
            repo_path=args.repo_path,
            base_branch=args.base_branch,
        )
        write_json_report(report, args.output)
        write_markdown_report(report, args.markdown)
        print(f"Wrote JSON report to {args.output}")
        print(f"Wrote Markdown report to {args.markdown}")
        return 0

    print("Unsupported command", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
