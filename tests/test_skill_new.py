from pathlib import Path

from typer.testing import CliRunner

from codex_project_lab.cli import app

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
