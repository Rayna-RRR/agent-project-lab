# Agent Project Lab

Agent Project Lab is a local-first CLI for turning rough project ideas into reusable AI coding agent workflows: project briefs, `AGENTS.md` rules, task packs, Agent Skills, and agent run logs.

This repository still ships the Python package as `codex-project-lab`, but the workflow assets are platform-agnostic. They can support Codex, Qwen Code, Claude Code, Cursor, Gemini CLI, Copilot agent, or a manual prompt-based workflow without directly integrating with those products.

It does not replace any AI coding tool. It helps builders use AI coding agents better by making project context, rules, prompts, skills, and lessons explicit enough to reuse.

## Why This Exists

AI coding sessions often start with scattered context: a vague idea, a few rules in chat, missing setup commands, and no durable record of what worked. That makes each new session slower and less consistent, regardless of which coding agent or LLM workflow is used.

Agent Project Lab gives builders a lightweight way to capture that structure before and after coding work. The result is a small set of Markdown and JSON files that can travel with a repo and help future agent-assisted sessions start with better context.

## Problem It Solves

- Turns rough ideas into a practical project brief.
- Creates an `AGENTS.md` file with setup, test, lint, run, done, and do-not-build guidance.
- Creates starter task prompts that can be reused across agent sessions.
- Drafts reusable Agent Skills under `.agents/skills/`.
- Reviews `AGENTS.md` and `SKILL.md` files with deterministic local checks.
- Keeps a simple append-only log of agent-assisted runs and lessons learned.
- Supports scripted workflows with local JSON input files and JSON checker output.

## Why This Is Platform-Agnostic

Agent Project Lab writes plain Markdown and reads local JSON. It does not call, authenticate with, or directly integrate with any AI coding product.

The outputs are useful anywhere a human or coding agent needs project context:

- `PROJECT_BRIEF.md` explains what the project is and what matters.
- `AGENTS.md` captures repo rules, commands, constraints, and done criteria.
- `TASKS.md` stores reusable task prompts.
- `.agents/skills/<name>/SKILL.md` stores reusable workflow instructions.
- `logs/agent_runs.md` stores append-only agent run logs.

Compatible workflows can include Codex, Qwen Code, Claude Code, Cursor, Gemini CLI, Copilot agent, or manual LLM-assisted development. This is compatibility by file format and workflow structure, not direct product integration.

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

Interactive workflow:

```bash
lab init
lab agents check
lab skill new
lab skill review .agents/skills/repo-onboarding
lab log add
```

Scripted workflow:

```bash
lab init --from-file examples/init_input.json --force
lab agents check AGENTS.md --json
lab skill new --from-file examples/skill_input.json --force
lab skill review .agents/skills/repo-onboarding --json
lab log add --from-file examples/log_entry.json
lab log add --from-file examples/log_entry.json --dry-run
```

The generated files are local Markdown files. There is no database, hosted service, external API call, or direct product integration in v0.2.0.

## Command Overview

| Command | Purpose |
| --- | --- |
| `lab init [--force] [--from-file path.json]` | Ask structured project questions or read JSON input, then generate `PROJECT_BRIEF.md`, `AGENTS.md`, and `TASKS.md`. |
| `lab agents check [path] [--json]` | Score whether an `AGENTS.md` file contains useful AI coding agent guidance. Rich output is default; `--json` prints a machine-readable report. |
| `lab skill new [--force] [--from-file path.json]` | Create `.agents/skills/<skill-name>/SKILL.md` from prompts or JSON input. |
| `lab skill review PATH [--json]` | Review a `SKILL.md` file or skill directory for practical skill-design quality. Rich output is default; `--json` prints a machine-readable report. |
| `lab log add [--file path] [--dry-run] [--from-file path.json]` | Append an agent run log entry to `logs/agent_runs.md`, append to a custom file, or print the entry without writing. |

## JSON Input Files

v0.2.0 supports JSON only for `--from-file`. YAML, JSON Schema export, and schema migrations are intentionally postponed.

Project init input:

```json
{
  "project_name": "Readme Steward",
  "project_idea": "A local CLI that helps maintain clear README files for small software projects.",
  "target_users": "Solo developers and small teams using AI coding agents",
  "main_problem": "README updates are often skipped because project context and verification steps are scattered.",
  "mvp_scope": ["Generate a README improvement brief", "Create agent-ready repository rules"],
  "tech_stack": ["Python", "Typer", "Rich"],
  "setup_command": "pip install -e \".[dev]\"",
  "test_command": "pytest",
  "lint_command": "ruff check .",
  "run_command": "lab --help",
  "do_not_build": ["Web UI", "Database", "External API calls"],
  "done_criteria": ["Generated Markdown is readable", "Tests pass locally"]
}
```

Skill input and log input examples are available in [examples/skill_input.json](examples/skill_input.json) and [examples/log_entry.json](examples/log_entry.json).

## JSON Reports

Checker commands keep Rich terminal reports by default. Add `--json` when a script needs machine-readable output:

```bash
lab agents check AGENTS.md --json
lab skill review .agents/skills/repo-onboarding --json
```

Reports include `status`, `score`, `passed`, individual `checks`, missing items, and suggestions. Exit codes remain the same as the Rich output: `0` when the score is at least `80`, otherwise `1`.

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

After an AI coding agent session, capture what happened:

```bash
lab log add
```

See [examples/](examples/) for short sample inputs and outputs.

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
- Starter agent task prompts with context and acceptance criteria
```

After `lab skill new`:

```text
.agents/skills/readme-review/SKILL.md
- Description, triggers, non-triggers, required inputs, workflow, output format, quality bar, failure handling
```

After `lab log add`:

```text
logs/agent_runs.md
- Timestamped notes on agent/tool used, prompt, changed files, verification, results, lessons, and next step
```

## Current v0.2.0 Scope

- Python CLI using Typer and Rich.
- Jinja2 Markdown templates.
- Pydantic validation for local JSON input files.
- Local generation of `PROJECT_BRIEF.md`, `AGENTS.md`, `TASKS.md`, `SKILL.md`, and agent run logs.
- Practical keyword/heading checks for `AGENTS.md` and `SKILL.md`.
- Machine-readable JSON output for checker commands.
- pytest coverage for implemented command behavior.

## Intentionally Not Included

- No Web UI or TUI.
- No database or search index.
- No external AI/API calls.
- No direct integration with Codex, Qwen Code, Claude Code, Cursor, Gemini CLI, Copilot agent, or other coding tools.
- No automatic coding-agent execution.
- No YAML input support in v0.2.0.
- No claim of production readiness; v0.2.0 is a portfolio-ready local workflow tool.

## v0.3 Roadmap

- YAML input support if users need it.
- JSON Schema export for input files and reports.
- Schema versioning and migrations.
- Field-by-field non-interactive CLI flags.
- Configurable template packages and template versioning.
- Stronger Markdown parsing.
- Optional project profile files for repeatable defaults.
- SARIF or richer report formats.
- Automatic repair suggestions for `AGENTS.md` or `SKILL.md`.

## Development

```bash
pytest
ruff check .
```
