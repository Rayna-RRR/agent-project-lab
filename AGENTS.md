# AGENTS.md

## Project Purpose

Agent Project Lab helps builders organize project context, project rules, reusable task prompts, Agent Skills, and agent run logs for AI-assisted development. The Python package is still named `agent-project-lab`, but the generated Markdown and JSON assets are platform-agnostic and must not execute or impersonate any AI coding tool.

## Command Output

Protect context usage. **Any command with unknown or potentially large output must be byte-capped.**

Default pattern:

```bash
COMMAND 2>&1 | head -c 4000
```

## Repo Layout

- `agent_project_lab/`: Python package for the CLI, templates, and command handlers.
- `agent_project_lab/commands/`: Typer command modules grouped by CLI area.
- `agent_project_lab/templates/`: Jinja2 Markdown templates used for generated files.
- `examples/`: Short sample inputs and generated Markdown outputs for README/demo use.
- `tests/`: pytest coverage for CLI behavior and implemented command behavior.
- `.github/workflows/`: Cross-version CI and tag-driven GitHub Release automation.

## Setup Command

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
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

## Build Command

```bash
python -m build
```

## Done Criteria

- `lab --help` works and lists the planned command surface.
- `lab init` generates `PROJECT_BRIEF.md`, `AGENTS.md`, and `TASKS.md`.
- `lab agents check` reports AGENTS.md quality with a clear score and exit code.
- `lab skill new` generates `.agents/skills/<skill-name>/SKILL.md`.
- `lab skill review` reports SKILL.md quality with a clear score and exit code.
- `lab log add` appends an agent run log entry to Markdown.
- `lab init`, `lab skill new`, and `lab log add` support local JSON `--from-file` input without breaking interactive prompts.
- `lab agents check` and `lab skill review` support `--json` output without changing default Rich reports.
- Focused pytest tests pass for implemented behavior.
- Wheel and source distribution builds install cleanly and expose `lab --help`.
- GitHub Actions passes on supported Python versions before release.
- The implementation remains local-first with no database and no external API calls.

## Do-Not Rules

- Do not add a web UI, TUI, database, hosted service, or external AI/API integration in v0.2.
- Do not make this tool execute, impersonate, or replace any external AI coding tool.
- Do not add hidden network calls.
- Do not generate files outside the user-selected target directory for generation commands.
- Do not add YAML support unless it is explicitly scoped for a future release.

## Update Rules

- When adding a CLI command, update `README.md`, `AGENTS.md`, and tests in the same change.
- When changing a generated Markdown shape, update the corresponding Jinja2 template and tests.
- When changing command behavior, add focused tests in the same change.
- When changing release behavior, update `RELEASING.md`, workflow files, and relevant tests or
  smoke checks.
- Keep `pyproject.toml`, `agent_project_lab.__version__`, `CHANGELOG.md`, and release tags aligned.
