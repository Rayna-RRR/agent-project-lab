# AGENTS.md

## Project Purpose

A local CLI that helps maintain clear README files for small software projects.

## Repo Layout

- [PROJECT_BRIEF.md](PROJECT_BRIEF.md): users, problem, scope, and technology choices.
- [TASKS.md](TASKS.md): task objectives, verification, and handoff instructions.

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
lab --help
```

## Do-Not-Build Items

- Web UI
- Database
- External API calls

## Done Criteria

- Generated Markdown is readable
- Commands are documented
- Tests pass locally

## Update Rules

- Keep commands and repository paths current here; keep product context in PROJECT_BRIEF.md.
