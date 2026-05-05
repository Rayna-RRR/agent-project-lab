from typer.testing import CliRunner

from codex_project_lab.cli import app


def test_lab_help_lists_v01_commands():
    runner = CliRunner()

    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "init" in result.output
    assert "agents" in result.output
    assert "skill" in result.output
    assert "log" in result.output
    assert "AI coding agent" in result.output
    assert "Agent run log helpers" in result.output
