# AGENTS.md

## Project Purpose

Codex Project Lab helps builders use Codex better by organizing project context, project rules, reusable task prompts, agent skills, and Codex run logs. It does not replace Codex and must not execute or impersonate Codex workflows.

## Repo Layout

- `codex_project_lab/`: Python package for the CLI, templates, and command handlers.
- `codex_project_lab/commands/`: Typer command modules grouped by CLI area.
- `codex_project_lab/templates/`: Jinja2 Markdown templates used for generated files.
- `tests/`: pytest coverage for CLI behavior and implemented command behavior.

## Setup Command

```bash
python -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"
```

## Test Command

```bash
pytest
```

## Lint Command

```bash
ruff check .
```

## Run Command

```bash
lab --help
```

## Done Criteria

- `lab --help` works and lists the planned command surface.
- `lab init` generates `PROJECT_BRIEF.md`, `AGENTS.md`, and `TASKS.md`.
- `lab agents check` reports AGENTS.md quality with a clear score and exit code.
- `lab skill new` generates `.agents/skills/<skill-name>/SKILL.md`.
- `lab skill review` reports SKILL.md quality with a clear score and exit code.
- Unimplemented commands remain explicit stubs.
- Focused pytest tests pass for implemented behavior.
- The scaffold remains local-first with no database and no external API calls.

## Do-Not Rules

- Do not add a web UI, TUI, database, hosted service, or external AI/API integration in v0.1.
- Do not make this tool execute Codex or replace Codex.
- Do not add hidden network calls.
- Do not generate files outside the user-selected target directory for generation commands.

## Update Rules

- When adding a CLI command, update `README.md`, `AGENTS.md`, and tests in the same change.
- When changing a generated Markdown shape, update the corresponding Jinja2 template and tests.
- When replacing stubs with real behavior, add focused tests in the same change.
