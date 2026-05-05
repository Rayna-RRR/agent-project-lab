import re
from pathlib import Path

from typer.testing import CliRunner

from codex_project_lab.cli import app

LOG_INPUT = "\n".join(
    [
        "Implement lab log add",
        "Capture Codex run details in Markdown.",
        "Asked Codex to implement the log add feature.",
        "codex_project_lab/commands/log.py, tests/test_log_add.py",
        "pytest",
        "19 passed",
        "CliRunner made the append behavior easy to verify.",
        "Manual docs polish remains.",
        "Prompting for structured fields keeps logs reusable.",
        "Run the full test suite after docs updates.",
        "",
    ]
)


def test_log_add_creates_new_log_file(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["log", "add"], input=LOG_INPUT)
        log_file = Path("logs/codex_runs.md")

        assert result.exit_code == 0
        assert log_file.exists()
        content = log_file.read_text(encoding="utf-8")
        assert "# Codex Run Logs" in content
        assert "Implement lab log add" in content
        assert "Appended Codex run log entry" in result.output


def test_log_add_appends_second_entry(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        first = runner.invoke(app, ["log", "add"], input=LOG_INPUT)
        second = runner.invoke(app, ["log", "add"], input=LOG_INPUT)
        content = Path("logs/codex_runs.md").read_text(encoding="utf-8")

        assert first.exit_code == 0
        assert second.exit_code == 0
        assert content.count("# Codex Run Logs") == 1
        assert len(re.findall(r"^## \d{4}-\d{2}-\d{2}", content, flags=re.MULTILINE)) == 2


def test_log_add_custom_file_path_works(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["log", "add", "--file", "notes/runs.md"], input=LOG_INPUT)

        assert result.exit_code == 0
        assert Path("notes/runs.md").exists()
        assert not Path("logs/codex_runs.md").exists()


def test_log_add_dry_run_does_not_write_file(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["log", "add", "--dry-run"], input=LOG_INPUT)

        assert result.exit_code == 0
        assert "Dry run: generated log entry" in result.output
        assert "Implement lab log add" in result.output
        assert not Path("logs/codex_runs.md").exists()


def test_log_add_entry_includes_timestamp_and_required_sections(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["log", "add"], input=LOG_INPUT)
        content = Path("logs/codex_runs.md").read_text(encoding="utf-8")

        assert result.exit_code == 0
        assert re.search(r"## \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", content)
        assert "### Task Goal" in content
        assert "### Codex Prompt Summary" in content
        assert "### Changed Files" in content
        assert "### Verification" in content
        assert "### What Worked" in content
        assert "### What Remains" in content
        assert "### Lesson Learned" in content
        assert "### Next Step" in content
