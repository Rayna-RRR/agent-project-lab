from pathlib import Path

from typer.testing import CliRunner

from codex_project_lab.cli import app

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


INVALID_NAME_SKILL = STRONG_SKILL.replace("name: review-skill-draft", "name: Review Skill Draft")


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
