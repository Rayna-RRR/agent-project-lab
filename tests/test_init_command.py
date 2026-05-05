from pathlib import Path

from typer.testing import CliRunner

from codex_project_lab.cli import app


INIT_INPUT = "\n".join(
    [
        "Codex Project Lab",
        "A local-first CLI for shaping Codex-ready project workflows.",
        "Builders using Codex",
        "Rough ideas lack reusable project context",
        "Generate project brief, Generate AGENTS rules, Generate starter tasks",
        "Python, Typer, Rich, Jinja2",
        "pip install -e .",
        "pytest",
        "ruff check .",
        "lab --help",
        "Web UI, External APIs, Database",
        "Files generated, Commands documented, Tests pass",
        "",
    ]
)


def test_init_generates_project_files(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["init"], input=INIT_INPUT)

        assert result.exit_code == 0
        assert Path("PROJECT_BRIEF.md").exists()
        assert Path("AGENTS.md").exists()
        assert Path("TASKS.md").exists()
        assert "Generated project workflow files" in result.output
        assert "Codex Project Lab Project Brief" in Path("PROJECT_BRIEF.md").read_text(
            encoding="utf-8"
        )
        assert "## Setup Command" in Path("AGENTS.md").read_text(encoding="utf-8")
        assert "## Task 1: Generate project brief" in Path("TASKS.md").read_text(
            encoding="utf-8"
        )


def test_init_does_not_overwrite_without_force(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("PROJECT_BRIEF.md").write_text("existing brief", encoding="utf-8")

        result = runner.invoke(app, ["init"], input=INIT_INPUT)

        assert result.exit_code == 1
        assert "Refusing to overwrite" in result.output
        assert Path("PROJECT_BRIEF.md").read_text(encoding="utf-8") == "existing brief"
        assert not Path("AGENTS.md").exists()
        assert not Path("TASKS.md").exists()


def test_init_force_overwrites_generated_files(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("PROJECT_BRIEF.md").write_text("existing brief", encoding="utf-8")

        result = runner.invoke(app, ["init", "--force"], input=INIT_INPUT)

        assert result.exit_code == 0
        assert "existing brief" not in Path("PROJECT_BRIEF.md").read_text(encoding="utf-8")
        assert Path("AGENTS.md").exists()
        assert Path("TASKS.md").exists()
