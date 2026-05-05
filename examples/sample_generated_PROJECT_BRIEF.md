# README Coach Project Brief

## Project Idea

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

## Commands

- Setup: `pip install -e ".[dev]"`
- Test: `pytest`
- Lint: `ruff check .`
- Run: `readme-coach --help`

## Do-Not-Build Items

- No web UI in v0.1.
- No external AI API calls.
- No database.

## Done Criteria

- CLI help works.
- Generated Markdown is readable.
- Tests pass.
