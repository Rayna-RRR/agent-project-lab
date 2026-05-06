import json
from pathlib import Path
from typing import Optional

from typer.testing import CliRunner

from codex_project_lab.cli import app

INIT_INPUT = "\n".join(
    [
        "Agent Project Lab",
        "A local-first CLI for shaping agent-ready project workflows.",
        "Builders using AI coding agents",
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

PROJECT_JSON = {
    "project_name": "Agent Notes",
    "project_idea": "A local tool for turning meeting notes into agent-ready tasks.",
    "target_users": "Solo builders and small teams",
    "main_problem": "Project context is scattered across notes and prompts.",
    "mvp_scope": ["Create project brief", "Generate AGENTS.md", "Create task plan"],
    "tech_stack": ["Python", "Typer", "Rich"],
    "setup_command": "pip install -e \".[dev]\"",
    "test_command": "pytest",
    "lint_command": "ruff check .",
    "run_command": "lab --help",
    "do_not_build": ["Web UI", "Database", "External API calls"],
    "done_criteria": ["Generated files are useful", "Tests pass"],
}


def write_project_json(path: Path, data: Optional[dict[str, object]] = None) -> None:
    path.write_text(json.dumps(data or PROJECT_JSON), encoding="utf-8")


def test_init_generates_project_files(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["init"], input=INIT_INPUT)

        assert result.exit_code == 0
        assert Path("PROJECT_BRIEF.md").exists()
        assert Path("AGENTS.md").exists()
        assert Path("TASKS.md").exists()
        assert "Generated project workflow files" in result.output
        assert "Agent Project Lab Project Brief" in Path("PROJECT_BRIEF.md").read_text(
            encoding="utf-8"
        )
        agents_content = Path("AGENTS.md").read_text(encoding="utf-8")
        assert "## Repo Layout" in agents_content
        assert "## Setup Command" in agents_content
        assert "## Update Rules" in agents_content
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


def test_init_from_file_generates_project_files(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        write_project_json(Path("project.json"))

        result = runner.invoke(app, ["init", "--from-file", "project.json"])

        assert result.exit_code == 0
        assert Path("PROJECT_BRIEF.md").exists()
        assert Path("AGENTS.md").exists()
        assert Path("TASKS.md").exists()
        assert "Generated project workflow files" in result.output
        assert "Agent Notes Project Brief" in Path("PROJECT_BRIEF.md").read_text(
            encoding="utf-8"
        )
        assert "A local tool for turning meeting notes" in Path("TASKS.md").read_text(
            encoding="utf-8"
        )


def test_init_from_file_does_not_overwrite_without_force(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        write_project_json(Path("project.json"))
        Path("PROJECT_BRIEF.md").write_text("existing brief", encoding="utf-8")

        result = runner.invoke(app, ["init", "--from-file", "project.json"])

        assert result.exit_code == 1
        assert "Refusing to overwrite" in result.output
        assert Path("PROJECT_BRIEF.md").read_text(encoding="utf-8") == "existing brief"
        assert not Path("AGENTS.md").exists()
        assert not Path("TASKS.md").exists()


def test_init_from_file_force_overwrites_generated_files(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        write_project_json(Path("project.json"))
        Path("PROJECT_BRIEF.md").write_text("existing brief", encoding="utf-8")

        result = runner.invoke(app, ["init", "--from-file", "project.json", "--force"])

        assert result.exit_code == 0
        assert "existing brief" not in Path("PROJECT_BRIEF.md").read_text(encoding="utf-8")
        assert Path("AGENTS.md").exists()
        assert Path("TASKS.md").exists()


def test_init_from_file_invalid_json_errors(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("project.json").write_text("{bad json", encoding="utf-8")

        result = runner.invoke(app, ["init", "--from-file", "project.json"])

        assert result.exit_code == 1
        assert "Invalid JSON" in result.output


def test_init_from_file_missing_required_field_errors(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        data = dict(PROJECT_JSON)
        del data["project_name"]
        write_project_json(Path("project.json"), data)

        result = runner.invoke(app, ["init", "--from-file", "project.json"])

        assert result.exit_code == 1
        assert "Invalid input file data" in result.output
        assert "project_name" in result.output
