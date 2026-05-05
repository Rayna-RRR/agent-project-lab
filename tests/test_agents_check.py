from pathlib import Path

from typer.testing import CliRunner

from codex_project_lab.cli import app


COMPLETE_AGENTS = """# AGENTS.md

## Project Purpose

Help builders structure Codex-ready project workflows.

## Repo Layout

- `codex_project_lab/`: CLI package.
- `tests/`: pytest tests.

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

## Done Criteria

- Tests pass.
- Generated Markdown is reviewed.

## Do-Not-Build Rules

- Do not add a web UI.
- Do not add external API calls.

## Update Rules

- Update AGENTS.md when commands, setup, tests, or project rules change.
"""


WEAK_AGENTS = """# Notes

This project has a CLI.

Run tests sometimes.
"""


def test_agents_check_complete_file_passes(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("AGENTS.md").write_text(COMPLETE_AGENTS, encoding="utf-8")

        result = runner.invoke(app, ["agents", "check"])

        assert result.exit_code == 0
        assert "PASS" in result.output
        assert "Score:" in result.output
        assert "100/100" in result.output


def test_agents_check_weak_file_fails(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("AGENTS.md").write_text(WEAK_AGENTS, encoding="utf-8")

        result = runner.invoke(app, ["agents", "check"])

        assert result.exit_code == 1
        assert "FAIL" in result.output
        assert "Missing items" in result.output
        assert "Setup command" in result.output


def test_agents_check_missing_file_errors(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["agents", "check", "missing/AGENTS.md"])

        assert result.exit_code == 1
        assert "File not found" in result.output
        assert "missing/AGENTS.md" in result.output


def test_agents_check_custom_file_path_works(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        custom_path = Path("docs/AGENTS.custom.md")
        custom_path.parent.mkdir()
        custom_path.write_text(COMPLETE_AGENTS, encoding="utf-8")

        result = runner.invoke(app, ["agents", "check", str(custom_path)])

        assert result.exit_code == 0
        assert str(custom_path) in result.output
