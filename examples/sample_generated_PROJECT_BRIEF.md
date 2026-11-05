# Readme Steward Project Brief

## Project Idea

A local CLI that helps maintain clear README files for small software projects.

## Target Users

Solo developers and small teams using AI coding agents

## Main Problem Solved

README updates are often skipped because project context and verification steps are scattered.

## MVP Scope

- Generate a README improvement brief
- Create agent-ready repository rules
- Draft reusable README cleanup tasks

## Tech Stack

- Python
- Typer
- Rich
- Jinja2

## Commands

- Setup: `pip install -e ".[dev]"`
- Test: `pytest`
- Lint: `ruff check .`
- Run: `lab --help`

## Do-Not-Build Items

- Web UI
- Database
- External API calls

## Done Criteria

- Generated Markdown is readable
- Commands are documented
- Tests pass locally
