# Changelog

## v0.2.0

- Added local JSON `--from-file` input for `lab init`, `lab skill new`, and `lab log add`.
- Added machine-readable `--json` reports for `lab agents check` and `lab skill review`.
- Added scripted workflow examples for repeatable local agent workflow setup.
- Updated README language around platform-agnostic AI coding agent workflows.

This release remains local-first and intentionally does not include a web UI, database, external API calls, direct coding-tool integrations, YAML input, or automatic agent execution.

## v0.1.0

- Added `lab init` to generate `PROJECT_BRIEF.md`, `AGENTS.md`, and `TASKS.md`.
- Added `lab agents check` for practical local `AGENTS.md` quality checks.
- Added `lab skill new` to draft reusable Agent Skills under `.agents/skills/`.
- Added `lab skill review` for deterministic `SKILL.md` quality reports.
- Added `lab log add` for append-only agent run logs.
- Added README, AGENTS.md, examples, and pytest coverage for the v0.1 workflow.

This release is local-first and intentionally does not include a web UI, database, external API calls, direct coding-tool integrations, or automatic agent execution.
