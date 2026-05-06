import json
from pathlib import Path

from typer.testing import CliRunner

from agent_project_lab.cli import app

SKILL_INPUT = "\n".join(
    [
        "Review Skill Draft",
        "Review Agent Skill drafts for clear triggers, workflow, and quality standards.",
        "Use when a user asks to create or improve a SKILL.md file.",
        "Do not use for general code review or product planning.",
        "Path to SKILL.md, Intended workflow goal",
        "Read the draft, Check required sections, Report concrete improvements",
        "A concise Markdown report with section-level feedback.",
        "Feedback is specific, actionable, and scoped to the skill file.",
        "If inputs are missing, explain the blocker and ask for the minimum missing context.",
        "",
    ]
)

SKILL_JSON = {
    "skill_name": "Repo Onboarding",
    "description": "Use when an agent needs to understand a new repository before editing.",
    "when_to_use": "When starting work in an unfamiliar repo.",
    "when_not_to_use": "When the task is a tiny single-file edit with clear context.",
    "required_inputs": ["Repository path", "User goal", "Relevant constraints"],
    "workflow_steps": ["Inspect project files", "Identify commands", "Summarize architecture"],
    "output_format": "A short repo briefing with risks and next steps.",
    "quality_bar": "Specific, grounded in files, and avoids unsupported claims.",
    "failure_handling": "Ask for missing context or report blockers clearly.",
}


def write_skill_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def test_skill_new_generates_skill_file(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["skill", "new"], input=SKILL_INPUT)
        skill_path = Path(".agents/skills/review-skill-draft/SKILL.md")

        assert result.exit_code == 0
        assert skill_path.exists()
        content = skill_path.read_text(encoding="utf-8")
        assert "name: review-skill-draft" in content
        assert "Review Agent Skill drafts" in content
        assert "Generated Agent Skill draft" in result.output
        assert "description controls when an agent may use this skill" in result.output


def test_skill_new_normalizes_skill_name(tmp_path: Path):
    runner = CliRunner()
    skill_input = SKILL_INPUT.replace("Review Skill Draft", "  Review   Skill Draft!!  ", 1)

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["skill", "new"], input=skill_input)

        assert result.exit_code == 0
        assert Path(".agents/skills/review-skill-draft/SKILL.md").exists()


def test_skill_new_does_not_overwrite_without_force(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        skill_path = Path(".agents/skills/review-skill-draft/SKILL.md")
        skill_path.parent.mkdir(parents=True)
        skill_path.write_text("existing skill", encoding="utf-8")

        result = runner.invoke(app, ["skill", "new"], input=SKILL_INPUT)

        assert result.exit_code == 1
        assert "Refusing to overwrite" in result.output
        assert skill_path.read_text(encoding="utf-8") == "existing skill"


def test_skill_new_refuses_existing_skill_before_prompting_for_details(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        skill_path = Path(".agents/skills/review-skill-draft/SKILL.md")
        skill_path.parent.mkdir(parents=True)
        skill_path.write_text("existing skill", encoding="utf-8")

        result = runner.invoke(app, ["skill", "new"], input="Review Skill Draft\n")

        assert result.exit_code == 1
        assert "Refusing to overwrite" in result.output
        assert "One-sentence description" not in result.output


def test_skill_new_force_overwrites_existing_skill(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        skill_path = Path(".agents/skills/review-skill-draft/SKILL.md")
        skill_path.parent.mkdir(parents=True)
        skill_path.write_text("existing skill", encoding="utf-8")

        result = runner.invoke(app, ["skill", "new", "--force"], input=SKILL_INPUT)

        assert result.exit_code == 0
        assert "existing skill" not in skill_path.read_text(encoding="utf-8")


def test_skill_new_empty_skill_name_errors(tmp_path: Path):
    runner = CliRunner()
    skill_input = SKILL_INPUT.replace("Review Skill Draft", "", 1)

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["skill", "new"], input=skill_input)

        assert result.exit_code == 1
        assert "Skill name is required" in result.output


def test_skill_new_from_file_generates_skill_file(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        write_skill_json(Path("skill.json"), SKILL_JSON)

        result = runner.invoke(app, ["skill", "new", "--from-file", "skill.json"])
        skill_path = Path(".agents/skills/repo-onboarding/SKILL.md")

        assert result.exit_code == 0
        assert skill_path.exists()
        content = skill_path.read_text(encoding="utf-8")
        assert "name: repo-onboarding" in content
        assert "Use when an agent needs to understand" in content


def test_skill_new_from_file_normalizes_skill_name(tmp_path: Path):
    runner = CliRunner()
    skill_json = dict(SKILL_JSON)
    skill_json["skill_name"] = "  Repo   Onboarding!!  "

    with runner.isolated_filesystem(temp_dir=tmp_path):
        write_skill_json(Path("skill.json"), skill_json)

        result = runner.invoke(app, ["skill", "new", "--from-file", "skill.json"])

        assert result.exit_code == 0
        assert Path(".agents/skills/repo-onboarding/SKILL.md").exists()


def test_skill_new_from_file_does_not_overwrite_without_force(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        write_skill_json(Path("skill.json"), SKILL_JSON)
        skill_path = Path(".agents/skills/repo-onboarding/SKILL.md")
        skill_path.parent.mkdir(parents=True)
        skill_path.write_text("existing skill", encoding="utf-8")

        result = runner.invoke(app, ["skill", "new", "--from-file", "skill.json"])

        assert result.exit_code == 1
        assert "Refusing to overwrite" in result.output
        assert skill_path.read_text(encoding="utf-8") == "existing skill"


def test_skill_new_from_file_force_overwrites_existing_skill(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        write_skill_json(Path("skill.json"), SKILL_JSON)
        skill_path = Path(".agents/skills/repo-onboarding/SKILL.md")
        skill_path.parent.mkdir(parents=True)
        skill_path.write_text("existing skill", encoding="utf-8")

        result = runner.invoke(app, ["skill", "new", "--from-file", "skill.json", "--force"])

        assert result.exit_code == 0
        assert "existing skill" not in skill_path.read_text(encoding="utf-8")


def test_skill_new_from_file_empty_skill_name_errors(tmp_path: Path):
    runner = CliRunner()
    skill_json = dict(SKILL_JSON)
    skill_json["skill_name"] = ""

    with runner.isolated_filesystem(temp_dir=tmp_path):
        write_skill_json(Path("skill.json"), skill_json)

        result = runner.invoke(app, ["skill", "new", "--from-file", "skill.json"])

        assert result.exit_code == 1
        assert "Invalid input file data" in result.output
        assert "skill_name" in result.output
