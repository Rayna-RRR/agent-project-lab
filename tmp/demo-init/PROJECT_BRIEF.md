# AI Resume Reviewer Project Brief

## Project Idea

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

## Commands

- Setup: `pip install -e ".[dev]"`
- Test: `python -m pytest`
- Lint: `ruff check .`
- Run: `lab resume review`

## Do-Not-Build Items

- web UI
- database
- external API

## Done Criteria

- generated report is clear and tests pass
