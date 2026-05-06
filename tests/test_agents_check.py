import json
from pathlib import Path

from typer.testing import CliRunner

from agent_project_lab.cli import app

COMPLETE_AGENTS = """# AGENTS.md

## Project Purpose

Help builders structure agent-ready project workflows.

## Repo Layout

- `agent_project_lab/`: CLI package.
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


PLACEHOLDER_AGENTS = """# AGENTS.md

## Project Purpose

TBD

## Repo Layout

TBD

## Setup Command

TBD

## Test Command

TBD

## Lint Command

TBD

## Run Command

TBD

## Done Criteria

TBD

## Do-Not-Build Rules

TBD

## Update Rules

TBD
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


def test_agents_check_placeholder_sections_fail(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("AGENTS.md").write_text(PLACEHOLDER_AGENTS, encoding="utf-8")

        result = runner.invoke(app, ["agents", "check", "--json"])
        payload = json.loads(result.output)

        assert result.exit_code == 1
        assert payload["status"] == "FAIL"
        assert payload["checks"][0]["evidence"].startswith(
            "Found heading with empty or placeholder content"
        )


def test_agents_check_missing_file_errors(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["agents", "check", "missing/AGENTS.md"])

        assert result.exit_code == 1
        assert "File not found" in result.output
        assert "missing/AGENTS.md" in result.output


def test_agents_check_directory_path_errors(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("docs").mkdir()

        result = runner.invoke(app, ["agents", "check", "docs"])

        assert result.exit_code == 1
        assert "Expected an AGENTS.md file, got directory" in result.output
        assert "docs" in result.output


def test_agents_check_custom_file_path_works(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        custom_path = Path("docs/AGENTS.custom.md")
        custom_path.parent.mkdir()
        custom_path.write_text(COMPLETE_AGENTS, encoding="utf-8")

        result = runner.invoke(app, ["agents", "check", str(custom_path)])

        assert result.exit_code == 0
        assert str(custom_path) in result.output


def test_agents_check_json_complete_file_passes(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("AGENTS.md").write_text(COMPLETE_AGENTS, encoding="utf-8")

        result = runner.invoke(app, ["agents", "check", "--json"])
        payload = json.loads(result.output)

        assert result.exit_code == 0
        assert payload["status"] == "PASS"
        assert payload["score"] == 100
        assert payload["passed"] is True
        assert payload["missing_items"] == []
        assert payload["checks"][0]["name"] == "Project purpose"


def test_agents_check_json_weak_file_fails(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("AGENTS.md").write_text(WEAK_AGENTS, encoding="utf-8")

        result = runner.invoke(app, ["agents", "check", "--json"])
        payload = json.loads(result.output)

        assert result.exit_code == 1
        assert payload["status"] == "FAIL"
        assert payload["score"] < 80
        assert "Setup command" in payload["missing_items"]
        assert payload["suggestions"]


def test_agents_check_json_missing_file_errors(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["agents", "check", "missing/AGENTS.md", "--json"])
        payload = json.loads(result.output)

        assert result.exit_code == 1
        assert payload["status"] == "ERROR"
        assert payload["passed"] is False
        assert payload["error"] == "File not found"


def test_agents_check_json_custom_file_path_works(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        custom_path = Path("docs/AGENTS.custom.md")
        custom_path.parent.mkdir()
        custom_path.write_text(COMPLETE_AGENTS, encoding="utf-8")

        result = runner.invoke(app, ["agents", "check", str(custom_path), "--json"])
        payload = json.loads(result.output)

        assert result.exit_code == 0
        assert payload["path"] == str(custom_path)
        assert payload["status"] == "PASS"
