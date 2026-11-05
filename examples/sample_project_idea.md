# Sample Project Idea

Project name: Readme Steward

One-sentence idea: A local CLI that helps maintain clear README files for small software projects.

Target users: Solo developers and small teams using AI coding agents.

Main problem solved: README updates are often skipped because project context and verification steps are scattered.

MVP scope:

- Generate a README improvement brief.
- Create agent-ready repository rules.
- Draft reusable README cleanup tasks.

Tech stack:

- Python
- Typer
- Rich
- Jinja2

Commands:

- Setup: `pip install -e ".[dev]"`
- Test: `pytest`
- Lint: `ruff check .`
- Run: `lab --help`

Do-not-build items:

- Web UI.
- Database.
- External API calls.

Done criteria:

- Generated Markdown is readable.
- Commands are documented.
- Tests pass locally.
