# AGENTS.md

## Project Purpose

A local-first CLI that helps solo developers turn rough README notes into clearer project documentation.

## Target Users

Solo developers and small open-source maintainers.

## Main Problem Solved

Project docs often lack setup commands, usage examples, and clear scope, which slows down contributors and future AI coding sessions.

## MVP Scope

- Ask structured README improvement questions.
- Generate a README improvement checklist.
- Produce a concise rewrite plan.

## Tech Stack

- Python
- Typer
- Rich
- pytest

## Repo Layout

- `readme_coach/`: CLI package and command handlers.
- `readme_coach/templates/`: Markdown templates.
- `tests/`: pytest coverage for CLI behavior.

## Setup Command

```bash
pip install -e ".[dev]"
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
readme-coach --help
```

## Do-Not-Build Items

- No web UI in v0.1.
- No external AI API calls.
- No database.

## Done Criteria

- CLI help works.
- Generated Markdown is readable.
- Tests pass.

## Update Rules

- Update this file when setup, test, lint, run, or project rules change.
