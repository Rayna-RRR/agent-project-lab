import json
import re
from pathlib import Path
from typing import Optional

from typer.testing import CliRunner

from agent_project_lab.cli import app

LOG_INPUT = "\n".join(
    [
        "Implement lab log add",
        "Capture AI coding agent run details in Markdown.",
        "Qwen Code",
        "Asked an AI coding agent to implement the log add feature.",
        "agent_project_lab/commands/log.py, tests/test_log_add.py",
        "pytest",
        "19 passed",
        "CliRunner made the append behavior easy to verify.",
        "Manual docs polish remains.",
        "Prompting for structured fields keeps logs reusable.",
        "Run the full test suite after docs updates.",
        "",
    ]
)

LOG_JSON = {
    "task_title": "Add JSON input support",
    "task_goal": "Make log add usable from scripts.",
    "agent_tool_used": "Agent Project Lab",
    "prompt_summary": "Implement --from-file for lab log add.",
    "changed_files": ["agent_project_lab/commands/log.py", "tests/test_log_add.py"],
    "verification_command": "pytest",
    "verification_result": "Passed",
    "what_worked": "The same template worked for interactive and file-based input.",
    "what_remains": "Add README examples.",
    "lesson_learned": "Structured inputs make workflows easier to reproduce.",
    "next_step": "Add JSON output to checkers.",
}


def write_log_json(path: Path, data: Optional[dict[str, object]] = None) -> None:
    path.write_text(json.dumps(LOG_JSON if data is None else data), encoding="utf-8")


def test_log_add_creates_new_log_file(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["log", "add"], input=LOG_INPUT)
        log_file = Path("logs/agent_runs.md")

        assert result.exit_code == 0
        assert log_file.exists()
        content = log_file.read_text(encoding="utf-8")
        assert "# Agent Run Logs" in content
        assert "Implement lab log add" in content
        assert "Appended agent run log entry" in result.output


def test_log_add_appends_second_entry(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        first = runner.invoke(app, ["log", "add"], input=LOG_INPUT)
        second = runner.invoke(app, ["log", "add"], input=LOG_INPUT)
        content = Path("logs/agent_runs.md").read_text(encoding="utf-8")

        assert first.exit_code == 0
        assert second.exit_code == 0
        assert content.count("# Agent Run Logs") == 1
        assert len(re.findall(r"^## \d{4}-\d{2}-\d{2}", content, flags=re.MULTILINE)) == 2


def test_log_add_appends_after_existing_file_without_trailing_newline(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        log_file = Path("logs/agent_runs.md")
        log_file.parent.mkdir()
        log_file.write_text("existing entry", encoding="utf-8")

        result = runner.invoke(app, ["log", "add"], input=LOG_INPUT)
        content = log_file.read_text(encoding="utf-8")

        assert result.exit_code == 0
        assert content.startswith("existing entry\n## ")


def test_log_add_custom_file_path_works(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["log", "add", "--file", "notes/runs.md"], input=LOG_INPUT)

        assert result.exit_code == 0
        assert Path("notes/runs.md").exists()
        assert not Path("logs/agent_runs.md").exists()


def test_log_add_dry_run_does_not_write_file(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["log", "add", "--dry-run"], input=LOG_INPUT)

        assert result.exit_code == 0
        assert "Dry run: generated log entry" in result.output
        assert "Implement lab log add" in result.output
        assert not Path("logs/agent_runs.md").exists()


def test_log_add_file_option_rejects_directory(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("logs").mkdir()

        result = runner.invoke(app, ["log", "add", "--file", "logs"], input=LOG_INPUT)

        assert result.exit_code == 1
        assert "Expected a Markdown log file, got directory" in result.output
        assert "logs" in result.output
        assert not Path("logs/agent_runs.md").exists()


def test_log_add_file_option_rejects_file_parent(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("notes").write_text("not a directory", encoding="utf-8")

        result = runner.invoke(app, ["log", "add", "--file", "notes/runs.md"], input=LOG_INPUT)

        assert result.exit_code == 1
        assert "Expected log file parent to be a directory" in result.output
        assert "notes" in result.output


def test_log_add_entry_includes_timestamp_and_required_sections(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["log", "add"], input=LOG_INPUT)
        content = Path("logs/agent_runs.md").read_text(encoding="utf-8")

        assert result.exit_code == 0
        assert re.search(r"## \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", content)
        assert "### Agent/Tool Used" in content
        assert "Qwen Code" in content
        assert "### Task Goal" in content
        assert "### Agent/Tool Prompt Summary" in content
        assert "### Changed Files" in content
        assert "### Verification" in content
        assert "### What Worked" in content
        assert "### What Remains" in content
        assert "### Lesson Learned" in content
        assert "### Next Step" in content


def test_log_add_from_file_creates_new_log_file(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        write_log_json(Path("log.json"))

        result = runner.invoke(app, ["log", "add", "--from-file", "log.json"])
        log_file = Path("logs/agent_runs.md")

        assert result.exit_code == 0
        assert log_file.exists()
        content = log_file.read_text(encoding="utf-8")
        assert "# Agent Run Logs" in content
        assert "Add JSON input support" in content
        assert "- agent_project_lab/commands/log.py" in content


def test_log_add_from_file_appends_second_entry(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        write_log_json(Path("log.json"))

        first = runner.invoke(app, ["log", "add", "--from-file", "log.json"])
        second = runner.invoke(app, ["log", "add", "--from-file", "log.json"])
        content = Path("logs/agent_runs.md").read_text(encoding="utf-8")

        assert first.exit_code == 0
        assert second.exit_code == 0
        assert content.count("# Agent Run Logs") == 1
        assert len(re.findall(r"^## \d{4}-\d{2}-\d{2}", content, flags=re.MULTILINE)) == 2


def test_log_add_from_file_custom_file_path_works(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        write_log_json(Path("log.json"))

        result = runner.invoke(
            app,
            ["log", "add", "--from-file", "log.json", "--file", "notes/runs.md"],
        )

        assert result.exit_code == 0
        assert Path("notes/runs.md").exists()
        assert not Path("logs/agent_runs.md").exists()


def test_log_add_from_file_dry_run_does_not_write_file(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        write_log_json(Path("log.json"))

        result = runner.invoke(app, ["log", "add", "--from-file", "log.json", "--dry-run"])

        assert result.exit_code == 0
        assert "Dry run: generated log entry" in result.output
        assert "Add JSON input support" in result.output
        assert not Path("logs/agent_runs.md").exists()


def test_log_add_from_file_missing_required_field_errors(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        log_json = dict(LOG_JSON)
        del log_json["task_title"]
        write_log_json(Path("log.json"), log_json)

        result = runner.invoke(app, ["log", "add", "--from-file", "log.json"])

        assert result.exit_code == 1
        assert "Invalid input file data" in result.output
        assert "task_title" in result.output
