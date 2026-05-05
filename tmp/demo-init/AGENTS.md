# AGENTS.md

## Project Purpose

A local tool that reviews resumes against job descriptions.

## Target Users

students and junior job seekers

## Main Problem Solved

users do not know how to tailor resumes for specific jobs

## MVP Scope

- CLI that generates review notes and rewrite suggestions

## Tech Stack

- Python
- Typer
- pytest

## Setup Command

```bash
pip install -e ".[dev]"
```

## Test Command

```bash
python -m pytest
```

## Lint Command

```bash
ruff check .
```

## Run Command

```bash
lab resume review
```

## Do-Not-Build Items

- web UI
- database
- external API

## Done Criteria

- generated report is clear and tests pass
