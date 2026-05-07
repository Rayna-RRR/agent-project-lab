# Agent Project Lab

English | [简体中文](README.zh-CN.md)

**Local-first CLI for turning rough project ideas into agent-ready AI coding agent workflows.**

Agent Project Lab helps builders create and maintain the workflow assets that make AI-assisted development more repeatable: `PROJECT_BRIEF.md`, `AGENTS.md`, `TASKS.md`, Agent Skills, and agent run logs.

It is platform-agnostic by design. The tool writes local Markdown and reads local JSON; it does not directly integrate with, call, authenticate with, or replace any AI coding agent.

## Demo Flow

```bash
lab init --from-file examples/init_input.json
lab agents check AGENTS.md --json
lab skill new --from-file examples/skill_input.json
lab skill review .agents/skills/repo-onboarding --json
lab log add --from-file examples/log_entry.json
```

## The Problem

AI coding agents are powerful, but the surrounding workflow is often messy:

- project intent lives in chat history,
- setup and verification commands are missing or stale,
- repository rules are scattered across docs,
- reusable skills are not captured,
- run logs and lessons are lost between sessions.

Agent Project Lab structures those assets locally so a human or AI coding agent can start with clearer context, safer boundaries, and reusable prompts.

## What This Tool Does

- Guides a rough project idea into an agent-ready project brief.
- Generates `AGENTS.md` with purpose, layout, commands, done criteria, do-not-build rules, and update rules.
- Generates `TASKS.md` with reusable task prompts.
- Creates Agent Skill drafts under `.agents/skills/<skill-name>/SKILL.md`.
- Reviews `AGENTS.md` and `SKILL.md` with deterministic local checks.
- Appends structured run logs to `logs/agent_runs.md`.
- Supports scripted workflows with JSON input files.
- Supports machine-readable JSON reports for checker commands.

## What This Tool Does Not Do

- It does not replace any AI coding agent.
- It does not execute coding-agent tasks.
- It does not provide a Web UI or TUI.
- It does not use a database.
- It does not make external API calls.
- It does not directly integrate with any AI coding product.
- It is not a production agent platform.

## Feature Overview

| Area | v0.2.0 capability |
| --- | --- |
| Project setup | `lab init` and `lab init --from-file JSON` |
| Agent guidance | `lab agents check` and `lab agents check --json` |
| Skill drafting | `lab skill new` and `lab skill new --from-file JSON` |
| Skill review | `lab skill review` and `lab skill review --json` |
| Run logs | `lab log add`, `lab log add --from-file JSON`, `lab log add --dry-run` |
| Validation | Pydantic models for structured JSON input |
| Quality checks | pytest test suite and Ruff linting |
| Examples | Sample JSON inputs, generated Markdown, and JSON reports |

## Installation

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
```

Dry-run a log entry without writing:

```bash
lab log add --from-file examples/log_entry.json --dry-run
```

## Full Command Overview

| Command | Output | Notes |
| --- | --- | --- |
| `lab init` | `PROJECT_BRIEF.md`, `AGENTS.md`, `TASKS.md` | Interactive prompts. Refuses to overwrite generated files unless `--force` is used. |
| `lab init --from-file PATH` | `PROJECT_BRIEF.md`, `AGENTS.md`, `TASKS.md` | Reads local JSON instead of prompting. |
| `lab agents check [PATH]` | Rich terminal report | Defaults to `AGENTS.md`. Exits `0` when score is at least `80`, otherwise `1`. |
| `lab agents check [PATH] --json` | JSON report | Machine-readable checker result for scripts. |
| `lab skill new` | `.agents/skills/<skill-name>/SKILL.md` | Interactive prompts. Skill name is normalized to lowercase kebab-case. |
| `lab skill new --from-file PATH` | `.agents/skills/<skill-name>/SKILL.md` | Reads local JSON instead of prompting. |
| `lab skill review PATH` | Rich terminal report | Accepts a direct `SKILL.md` path or a skill directory containing `SKILL.md`. |
| `lab skill review PATH --json` | JSON report | Machine-readable skill quality report for scripts. |
| `lab log add` | `logs/agent_runs.md` | Interactive append-only run log entry. |
| `lab log add --from-file PATH` | `logs/agent_runs.md` | Reads local JSON instead of prompting. |
| `lab log add --file PATH` | Custom Markdown log | Appends to a custom log file. |
| `lab log add --dry-run` | Terminal output only | Prints the generated entry without writing a file. |

## Scripted Workflows With JSON

v0.2.0 supports JSON only for `--from-file`. This keeps automation dependency-light and easy to validate with Pydantic.

Example project input:

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

See the complete sample files:

- [examples/init_input.json](examples/init_input.json)
- [examples/skill_input.json](examples/skill_input.json)
- [examples/log_entry.json](examples/log_entry.json)

## JSON Output Examples

Checker commands use Rich output by default. Add `--json` when a script needs a stable machine-readable report.

`lab agents check AGENTS.md --json`:

```json
{
  "path": "AGENTS.md",
  "status": "PASS",
  "score": 100,
  "passed": true,
  "missing_items": [],
  "suggestions": []
}
```

`lab skill review .agents/skills/repo-onboarding --json`:

```json
{
  "path": ".agents/skills/repo-onboarding/SKILL.md",
  "status": "PASS",
  "score": 100,
  "passed": true,
  "strengths": ["YAML frontmatter", "Frontmatter name", "Workflow steps"],
  "missing_items": [],
  "suggestions": []
}
```

Full sample reports:

- [examples/agents_check_report.json](examples/agents_check_report.json)
- [examples/skill_review_report.json](examples/skill_review_report.json)

## Examples Folder

The [examples/](examples/) folder shows short, realistic inputs and outputs:

- `sample_project_idea.md`: rough starting idea,
- `sample_generated_PROJECT_BRIEF.md`: generated project brief,
- `sample_generated_AGENTS.md`: generated agent guidance,
- `sample_generated_TASKS.md`: generated task prompt pack,
- `sample_skill.md`: sample Agent Skill,
- `sample_agent_runs.md`: sample run log,
- `*_input.json`: scripted workflow inputs,
- `*_report.json`: machine-readable checker outputs.

## Project Structure

```text
agent-project-lab/
  agent_project_lab/
    cli.py
    models.py
    commands/
    templates/
  examples/
  tests/
  AGENTS.md
  CHANGELOG.md
  README.md
  pyproject.toml
```

## v0.2.0 Scope

- Local-first Python CLI using Typer and Rich.
- Jinja2 Markdown templates.
- Pydantic validation for structured JSON inputs.
- Deterministic local checks for `AGENTS.md` and `SKILL.md`.
- Machine-readable JSON output for checker commands.
- pytest coverage for CLI behavior.
- Ruff linting.
- No Web UI, database, external API calls, hidden network calls, or direct product integrations.

## v0.3 Roadmap

Potential next steps:

- YAML input support if there is a clear need.
- JSON Schema export for input files and reports.
- Schema versioning and migrations.
- Field-by-field non-interactive CLI flags.
- Configurable template packs.
- Stronger Markdown parsing.
- Optional project profile files for repeatable defaults.
- SARIF or richer report formats.
- Automatic repair suggestions for `AGENTS.md` or `SKILL.md`.

## Portfolio And Learning Value

Agent Project Lab is intentionally small, local, and inspectable. It demonstrates:

- CLI product design with a clear v0.1 to v0.2 evolution,
- practical use of Typer, Rich, Pydantic, Jinja2, pytest, and Ruff,
- deterministic quality checks without external AI calls,
- platform-agnostic workflow design for AI-assisted development,
- testable automation features that preserve interactive UX.

The project is portfolio-ready, but it avoids claiming to be a production agent platform.

## Development

```bash
pytest
ruff check .
```

## License

MIT. See [LICENSE](LICENSE).
