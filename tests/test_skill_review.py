import json
from pathlib import Path

from typer.testing import CliRunner

from agent_project_lab.cli import app

STRONG_SKILL = """---
name: review-skill-draft
description: Use when a user asks to review an Agent Skill draft for trigger clarity,
  workflow quality, and failure handling.
---

# Review Skill Draft

## Description

Review Agent Skill drafts for clear triggers, practical workflow steps, and quality standards.

## When To Use This Skill

Use this skill when a user asks for a SKILL.md review or wants to improve reusable agent guidance.

## When Not To Use This Skill

Do not use this skill for general code review, product planning, or non-skill documentation.

## Required Inputs

- Path to SKILL.md
- Intended workflow goal

## Workflow Steps

1. Read the frontmatter.
2. Check each required body section.
3. Report concrete improvements.

## Output Format

A concise Markdown report with status, score, strengths, missing items, and suggestions.

## Quality Bar

Feedback is specific, actionable, scoped to the skill file, and avoids external calls.

## Failure Handling

If inputs are missing or the file cannot be read, explain the blocker and ask for the
minimum missing context.
"""


WEAK_SKILL = """# Weak Skill

This is a helper.
"""


PLACEHOLDER_SECTION_SKILL = """---
name: review-skill-draft
description: Use when a user asks to review an Agent Skill draft for trigger clarity,
  workflow quality, and failure handling.
---

# Review Skill Draft

## When To Use This Skill

TBD

## When Not To Use This Skill

TBD

## Required Inputs

TBD

## Workflow Steps

TBD

## Output Format

TBD

## Quality Bar

TBD

## Failure Handling

TBD
"""


INVALID_NAME_SKILL = STRONG_SKILL.replace("name: review-skill-draft", "name: Review Skill Draft")

FENCED_FAKE_SECTIONS = """---
name: review-skill-draft
description: Use when a user asks for a detailed review of a reusable Agent Skill draft.
---

# Review Skill Draft

```markdown
## When To Use This Skill
Useful content.
## When Not To Use This Skill
Useful content.
## Required Inputs
Useful content.
## Workflow Steps
Useful content.
## Output Format
Useful content.
## Quality Bar
Useful content.
## Failure Handling
Useful content.
```
"""


def test_skill_review_strong_skill_passes(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("SKILL.md").write_text(STRONG_SKILL, encoding="utf-8")

        result = runner.invoke(app, ["skill", "review", "SKILL.md"])

        assert result.exit_code == 0
        assert "PASS" in result.output
        assert "Score: 100/100" in result.output
        assert "Detected strengths" in result.output


def test_skill_review_weak_skill_fails(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("SKILL.md").write_text(WEAK_SKILL, encoding="utf-8")

        result = runner.invoke(app, ["skill", "review", "SKILL.md"])

        assert result.exit_code == 1
        assert "FAIL" in result.output
        assert "Missing items" in result.output
        assert "YAML frontmatter" in result.output


def test_skill_review_placeholder_sections_fail(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("SKILL.md").write_text(PLACEHOLDER_SECTION_SKILL, encoding="utf-8")

        result = runner.invoke(app, ["skill", "review", "SKILL.md", "--json"])
        payload = json.loads(result.output)

        assert result.exit_code == 1
        assert payload["status"] == "FAIL"
        assert "Workflow steps" in payload["missing_items"]
        assert "Failure handling" in payload["missing_items"]


def test_skill_review_ignores_sections_inside_fenced_code(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("SKILL.md").write_text(FENCED_FAKE_SECTIONS, encoding="utf-8")

        result = runner.invoke(app, ["skill", "review", "SKILL.md", "--json"])
        payload = json.loads(result.output)

        assert result.exit_code == 1
        assert payload["status"] == "FAIL"
        assert "Workflow steps" in payload["missing_items"]


def test_skill_review_directory_path_works(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        skill_dir = Path(".agents/skills/review-skill-draft")
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(STRONG_SKILL, encoding="utf-8")

        result = runner.invoke(app, ["skill", "review", str(skill_dir)])

        assert result.exit_code == 0
        assert ".agents/skills/review-skill-draft/SKILL.md" in result.output


def test_skill_review_missing_file_errors(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["skill", "review", "missing/SKILL.md"])

        assert result.exit_code == 1
        assert "File not found" in result.output
        assert "missing/SKILL.md" in result.output


def test_skill_review_non_skill_file_errors(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("sample_skill.md").write_text(STRONG_SKILL, encoding="utf-8")

        result = runner.invoke(app, ["skill", "review", "sample_skill.md"])

        assert result.exit_code == 1
        assert "Expected a SKILL.md file or skill directory" in result.output
        assert "sample_skill.md" in result.output


def test_skill_review_directory_without_skill_md_errors(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        skill_dir = Path(".agents/skills/empty-skill")
        skill_dir.mkdir(parents=True)

        result = runner.invoke(app, ["skill", "review", str(skill_dir)])

        assert result.exit_code == 1
        assert "Directory does not contain SKILL.md" in result.output
        assert ".agents/skills/empty-skill" in result.output


def test_skill_review_invalid_name_format_is_detected(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("SKILL.md").write_text(INVALID_NAME_SKILL, encoding="utf-8")

        result = runner.invoke(app, ["skill", "review", "SKILL.md"])

        assert result.exit_code == 0
        assert "Name format" in result.output
        assert "Use lowercase kebab-case" in result.output


def test_skill_review_json_strong_skill_passes(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("SKILL.md").write_text(STRONG_SKILL, encoding="utf-8")

        result = runner.invoke(app, ["skill", "review", "SKILL.md", "--json"])
        payload = json.loads(result.output)

        assert result.exit_code == 0
        assert payload["status"] == "PASS"
        assert payload["score"] == 100
        assert payload["passed"] is True
        assert "YAML frontmatter" in payload["strengths"]
        assert payload["missing_items"] == []


def test_skill_review_json_weak_skill_fails(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("SKILL.md").write_text(WEAK_SKILL, encoding="utf-8")

        result = runner.invoke(app, ["skill", "review", "SKILL.md", "--json"])
        payload = json.loads(result.output)

        assert result.exit_code == 1
        assert payload["status"] == "FAIL"
        assert payload["score"] < 60
        assert "YAML frontmatter" in payload["missing_items"]
        assert payload["suggestions"]


def test_skill_review_json_directory_path_works(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        skill_dir = Path(".agents/skills/review-skill-draft")
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(STRONG_SKILL, encoding="utf-8")

        result = runner.invoke(app, ["skill", "review", str(skill_dir), "--json"])
        payload = json.loads(result.output)

        assert result.exit_code == 0
        assert payload["path"] == ".agents/skills/review-skill-draft/SKILL.md"
        assert payload["status"] == "PASS"


def test_skill_review_json_missing_file_errors(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["skill", "review", "missing/SKILL.md", "--json"])
        payload = json.loads(result.output)

        assert result.exit_code == 1
        assert payload["status"] == "ERROR"
        assert payload["passed"] is False
        assert payload["error"] == "File not found"


def test_skill_review_json_non_utf8_file_errors(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("SKILL.md").write_bytes(b"\xff\xfe\x00")

        result = runner.invoke(app, ["skill", "review", "SKILL.md", "--json"])
        payload = json.loads(result.output)

        assert result.exit_code == 1
        assert payload["status"] == "ERROR"
        assert payload["error"] == "File must be UTF-8 text"


def test_skill_review_json_directory_without_skill_md_errors(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        skill_dir = Path(".agents/skills/empty-skill")
        skill_dir.mkdir(parents=True)

        result = runner.invoke(app, ["skill", "review", str(skill_dir), "--json"])
        payload = json.loads(result.output)

        assert result.exit_code == 1
        assert payload["status"] == "ERROR"
        assert payload["error"] == "Directory does not contain SKILL.md"


def test_skill_review_json_invalid_name_format_is_detected(tmp_path: Path):
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("SKILL.md").write_text(INVALID_NAME_SKILL, encoding="utf-8")

        result = runner.invoke(app, ["skill", "review", "SKILL.md", "--json"])
        payload = json.loads(result.output)

        assert result.exit_code == 0
        assert payload["status"] == "PASS"
        assert "Name format" in payload["missing_items"]
        assert any("Use lowercase kebab-case" in item for item in payload["suggestions"])
