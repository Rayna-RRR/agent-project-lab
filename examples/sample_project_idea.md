# Sample Project Idea

Project name: README Coach

One-sentence idea: A local-first CLI that helps solo developers turn rough README notes into clearer project documentation.

Target users: Solo developers and small open-source maintainers.

Main problem solved: Project docs often lack setup commands, usage examples, and clear scope, which slows down contributors and future AI coding sessions.

MVP scope:

- Ask structured README improvement questions.
- Generate a README improvement checklist.
- Produce a concise rewrite plan.

Tech stack:

- Python
- Typer
- Rich
- pytest

Commands:

- Setup: `pip install -e ".[dev]"`
- Test: `pytest`
- Lint: `ruff check .`
- Run: `readme-coach --help`

Do-not-build items:

- No web UI in v0.1.
- No external AI API calls.
- No database.

Done criteria:

- CLI help works.
- Generated Markdown is readable.
- Tests pass.
