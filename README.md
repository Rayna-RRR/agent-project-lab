# Codex Project Lab

Codex Project Lab is a local-first CLI tool that helps builders turn rough project ideas into reusable AI-coding workflows: project briefs, `AGENTS.md` files, task prompt packs, agent skills, and Codex run logs.

It does not replace Codex. It helps users use Codex better by structuring project context, rules, tasks, skills, and learning logs.

This repository is currently an early v0.1 implementation. `lab init`, `lab agents check`, `lab skill new`, `lab skill review`, and `lab log add` work.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

## Commands

```bash
lab init [--force]
lab agents check [path]
lab skill new [--force]
lab skill review <skill_path>
lab log add [--file logs/codex_runs.md] [--dry-run]
```

## v0.1 Scope

- `lab --help` CLI entry point.
- `lab init` interactive project workflow generation.
- `lab agents check` practical AGENTS.md quality validation.
- `lab skill new` reusable Agent Skill draft generation.
- `lab skill review` practical Agent Skill quality validation.
- `lab log add` append-only Codex run logging.
- Markdown templates for `PROJECT_BRIEF.md`, `AGENTS.md`, and `TASKS.md`.
- Project README and `AGENTS.md` rules for Codex.
- pytest coverage for the CLI scaffold and `lab init`.

## Out of Scope for v0.1

- Web UI or TUI.
- Database or search index.
- External AI/API calls.
- Automatic Codex execution.
- GitHub, Linear, or hosted service integrations.

## Development

```bash
pytest
ruff check .
```
