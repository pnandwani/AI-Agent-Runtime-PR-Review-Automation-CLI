# AI Agent Runtime & Tool Orchestration System

A Python project that combines an agent-style runtime with a deterministic pull request review CLI.

This system is designed to feel closer to how real AI products operate in production: tools are orchestrated through a runtime, steps are stateful, failures are retried in a controlled way, outputs are traceable, and the final review report maps findings directly to the code that changed.

## Why this project exists

Most demo agents stop at "call an LLM and print the answer." This project focuses on the harder engineering work around agentic systems:

- orchestrating tools as explicit runtime steps
- handling failures and retries predictably
- keeping execution state in memory
- producing deterministic reports developers can trust
- integrating cleanly with repository and review workflows

## Core capabilities

- Agent runtime with:
  - tool registry
  - workflow execution
  - run state tracking
  - in-memory execution context
  - retry and failure policies
- PR review workflow with:
  - repository cloning or local repository analysis
  - diff extraction against a target branch
  - static analysis and rule-based checks
  - mapping findings to changed lines only
  - structured JSON and Markdown review reports
- External integration primitives with:
  - REST API tool abstraction
  - OAuth token model
  - webhook event envelope

## Architecture

```text
CLI
  -> PRReviewWorkflow
      -> AgentRuntime
          -> ToolRegistry
          -> MemoryStore
          -> RetryPolicy
      -> RepositoryInspector
      -> Analyzers
          -> PythonSyntaxAnalyzer
          -> RuleBasedDiffAnalyzer
      -> ReportRenderer
```

## Project structure

```text
src/agent_pr_reviewer/
  analyzers/        Deterministic code analyzers
  integrations/     REST, OAuth, webhook primitives
  runtime/          Agent runtime, tools, retry, memory
  workflows/        PR review workflow
  cli.py            Command-line entrypoint
tests/
```

## Quick start

### 1. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install the project

```bash
pip install -e .
```

### 3. Run against a local repository

```bash
agent-pr-review review \
  --repo-path /path/to/repo \
  --base-branch main \
  --output reports/review.json \
  --markdown reports/review.md
```

### 4. Run by cloning a repository first

```bash
agent-pr-review review \
  --repo-url https://github.com/org/repo.git \
  --base-branch main \
  --output reports/review.json \
  --markdown reports/review.md
```

## Example output

The JSON report includes:

- repository metadata
- changed files and touched line numbers
- findings with severity, rule id, message, and exact changed-line mapping
- runtime execution trace
- summary statistics

The Markdown report is company-friendly and easy to attach to an email or GitHub discussion.

## Design choices

- Standard library first: the project avoids unnecessary dependencies.
- Deterministic analysis: review rules are explicit and reproducible.
- Explainable orchestration: runtime trace shows which tool ran and what happened.
- Production-oriented resilience: retries are limited, typed, and observable.

## Roadmap

- Add GitHub API integration for PR metadata and comments
- Post inline review comments through a webhook or API sink
- Add configurable rule packs and language-specific analyzers
- Plug in an LLM summarizer as an optional final step, not the source of truth

## Suggested GitHub repo name

`agent-pr-reviewer`

## How to present this to a company

Lead with the engineering framing:

> Built a Python-based agent runtime and PR review system that orchestrates repository analysis, deterministic static checks, failure handling, and structured reporting. Designed to reflect real AI system behavior beyond simple LLM calls by coordinating tools, memory, retries, and review workflows end to end.

## License

MIT
