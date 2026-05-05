# Codex Project Lab

Codex Project Lab is a local-first CLI that turns rough project ideas into agent-ready Codex workflows: project briefs, `AGENTS.md` rules, task packs, reusable skills, and run logs.

It does not replace Codex. It helps builders use Codex better by making project context, rules, prompts, skills, and lessons explicit enough to reuse.

## Why This Exists

AI coding sessions often start with scattered context: a vague idea, a few rules in chat, missing setup commands, and no durable record of what worked. That makes each new session slower and less consistent.

Codex Project Lab gives builders a lightweight way to capture that structure before and after coding work. The result is a small set of Markdown files that can travel with a repo and help future Codex sessions start with better context.

## Problem It Solves

- Turns rough ideas into a practical project brief.
- Creates an `AGENTS.md` file with setup, test, lint, run, done, and do-not-build guidance.
- Creates starter task prompts that can be reused across Codex sessions.
- Drafts reusable Agent Skills under `.agents/skills/`.
- Reviews `AGENTS.md` and `SKILL.md` files with deterministic local checks.
- Keeps a simple append-only log of Codex runs and lessons learned.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

Run the CLI:

```bash
lab --help
```

## Quickstart

```bash
lab init
lab agents check
lab skill new
lab skill review .agents/skills/repo-onboarding
lab log add
```

The generated files are local Markdown files. There is no database, hosted service, or external API call in v0.1.

## Command Overview

| Command | Purpose |
| --- | --- |
| `lab init [--force]` | Ask structured project questions and generate `PROJECT_BRIEF.md`, `AGENTS.md`, and `TASKS.md`. |
| `lab agents check [path]` | Score whether an `AGENTS.md` file contains useful AI coding guidance. |
| `lab skill new [--force]` | Create `.agents/skills/<skill-name>/SKILL.md` from interactive prompts. |
| `lab skill review PATH` | Review a `SKILL.md` file or skill directory for practical skill-design quality. |
| `lab log add [--file path] [--dry-run]` | Append a Codex run log entry to `logs/codex_runs.md` or print it without writing. |

## Demo Workflow

Start with a rough idea:

```text
I want to build a small local-first CLI that helps solo developers clean up README files.
```

Run:

```bash
lab init
```

Answer the prompts with the project idea, target users, MVP scope, tech stack, commands, do-not-build rules, and done criteria. The command generates:

```text
PROJECT_BRIEF.md
AGENTS.md
TASKS.md
```

Then check the agent guidance:

```bash
lab agents check AGENTS.md
```

Draft a reusable skill for future sessions:

```bash
lab skill new
lab skill review .agents/skills/readme-review
```

After a Codex coding session, capture what happened:

```bash
lab log add
```

See [examples/](examples/) for short sample outputs.

## Before And After

Before:

```text
Build a README cleanup CLI. It should be local and probably use Python.
```

After `lab init`:

```text
PROJECT_BRIEF.md
- Project idea, users, problem, MVP scope, commands, constraints, done criteria

AGENTS.md
- Project purpose, repo layout, setup/test/lint/run commands, do-not-build rules

TASKS.md
- Starter Codex task prompts with context and acceptance criteria
```

After `lab skill new`:

```text
.agents/skills/readme-review/SKILL.md
- Description, triggers, non-triggers, required inputs, workflow, output format, quality bar, failure handling
```

After `lab log add`:

```text
logs/codex_runs.md
- Timestamped notes on prompt, changed files, verification, results, lessons, and next step
```

## Current v0.1 Scope

- Python CLI using Typer and Rich.
- Jinja2 Markdown templates.
- Pydantic dependency reserved for structured validation as the project grows.
- Local generation of `PROJECT_BRIEF.md`, `AGENTS.md`, `TASKS.md`, `SKILL.md`, and Codex run logs.
- Practical keyword/heading checks for `AGENTS.md` and `SKILL.md`.
- pytest coverage for the implemented command behavior.

## Intentionally Not Included

- No Web UI or TUI.
- No database or search index.
- No external AI/API calls.
- No automatic Codex execution.
- No GitHub, Linear, or hosted service integration.
- No claim of production readiness; v0.1 is a portfolio-ready local workflow tool.

## v0.2 Roadmap

- JSON output for checks and reviews.
- Configurable templates.
- Safer non-interactive flags for CI or scripted setup.
- Stronger Markdown parsing.
- Optional project profile files for repeatable defaults.
- Better examples for multiple project types.
- Packaging polish for `pipx` or PyPI publishing.

## Development

```bash
pytest
ruff check .
```
