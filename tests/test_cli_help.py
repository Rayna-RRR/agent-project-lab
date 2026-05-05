from typer.testing import CliRunner

from codex_project_lab.cli import app


def test_lab_help_lists_scaffold_commands():
    runner = CliRunner()

    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "init" in result.output
    assert "agents" in result.output
    assert "skill" in result.output
    assert "log" in result.output
