"""Structured input and report models for Agent Project Lab."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Type, TypeVar

from pydantic import BaseModel, Field, ValidationError, field_validator

T = TypeVar("T", bound=BaseModel)


class InputFileError(ValueError):
    """Raised when a local JSON input file cannot be read or validated."""


def _required_text(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("must be a string")

    cleaned = value.strip()
    if not cleaned:
        raise ValueError("is required")
    return cleaned


def _optional_text(value: object) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError("must be a string")
    return value.strip()


def _required_text_list(value: object) -> list[str]:
    if not isinstance(value, list):
        raise ValueError("must be a non-empty list of strings")

    cleaned: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError("must contain only strings")
        stripped = item.strip()
        if not stripped:
            raise ValueError("must not contain empty items")
        cleaned.append(stripped)

    if not cleaned:
        raise ValueError("must be a non-empty list of strings")
    return cleaned


def format_validation_error(error: ValidationError) -> str:
    """Format Pydantic validation errors for concise CLI output."""

    details = []
    for item in error.errors():
        location = ".".join(str(part) for part in item["loc"])
        message = item["msg"]
        details.append(f"{location}: {message}" if location else message)

    return "Invalid input file data: " + "; ".join(details)


def load_json_model(path: Path, model_type: Type[T]) -> T:
    """Load a local JSON object and validate it as a Pydantic model."""

    if not path.exists():
        raise InputFileError(f"Input file not found: {path}")
    if path.is_dir():
        raise InputFileError(f"Expected a JSON file, got directory: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InputFileError(f"Invalid JSON in {path}: {exc.msg}") from exc
    except OSError as exc:
        raise InputFileError(f"Could not read input file {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise InputFileError("Input JSON must be an object.")

    try:
        return model_type.model_validate(data)
    except ValidationError as exc:
        raise InputFileError(format_validation_error(exc)) from exc


class ProjectInitInput(BaseModel):
    """Structured input for non-interactive `lab init`."""

    project_name: str
    project_idea: str
    target_users: str
    main_problem: str
    mvp_scope: list[str]
    tech_stack: list[str]
    setup_command: str
    test_command: str
    lint_command: str
    run_command: str
    do_not_build: list[str]
    done_criteria: list[str]

    @field_validator(
        "project_name",
        "project_idea",
        "target_users",
        "main_problem",
        "setup_command",
        "test_command",
        "lint_command",
        "run_command",
        mode="before",
    )
    @classmethod
    def clean_required_text(cls, value: object) -> str:
        return _required_text(value)

    @field_validator("mvp_scope", "tech_stack", "do_not_build", "done_criteria", mode="before")
    @classmethod
    def clean_required_text_list(cls, value: object) -> list[str]:
        return _required_text_list(value)

    def to_template_project(self) -> dict[str, object]:
        """Return the template context shape used by existing Markdown templates."""

        return {
            "name": self.project_name,
            "idea": self.project_idea,
            "target_users": self.target_users,
            "main_problem": self.main_problem,
            "mvp_scope": self.mvp_scope,
            "tech_stack": self.tech_stack,
            "setup_command": self.setup_command,
            "test_command": self.test_command,
            "lint_command": self.lint_command,
            "run_command": self.run_command,
            "do_not_build": self.do_not_build,
            "done_criteria": self.done_criteria,
        }


class SkillNewInput(BaseModel):
    """Structured input for non-interactive `lab skill new`."""

    skill_name: str
    description: str
    when_to_use: str
    when_not_to_use: str
    required_inputs: list[str]
    workflow_steps: list[str]
    output_format: str
    quality_bar: str
    failure_handling: str

    @field_validator(
        "skill_name",
        "description",
        "when_to_use",
        "when_not_to_use",
        "output_format",
        "quality_bar",
        "failure_handling",
        mode="before",
    )
    @classmethod
    def clean_required_text(cls, value: object) -> str:
        return _required_text(value)

    @field_validator("required_inputs", "workflow_steps", mode="before")
    @classmethod
    def clean_required_text_list(cls, value: object) -> list[str]:
        return _required_text_list(value)

    def to_template_skill(self, slug: str) -> dict[str, object]:
        """Return the template context shape used by the skill template."""

        return {
            "name": self.skill_name,
            "slug": slug,
            "description": self.description,
            "when_to_use": self.when_to_use,
            "when_not_to_use": self.when_not_to_use,
            "required_inputs": self.required_inputs,
            "workflow_steps": self.workflow_steps,
            "output_format": self.output_format,
            "quality_bar": self.quality_bar,
            "failure_handling": self.failure_handling,
        }


class RunLogInput(BaseModel):
    """Structured input for non-interactive `lab log add`."""

    task_title: str
    task_goal: str
    agent_tool_used: str = ""
    prompt_summary: str
    changed_files: list[str]
    verification_command: str
    verification_result: str
    what_worked: str
    what_remains: str
    lesson_learned: str
    next_step: str

    @field_validator(
        "task_title",
        "task_goal",
        "prompt_summary",
        "verification_command",
        "verification_result",
        "what_worked",
        "what_remains",
        "lesson_learned",
        "next_step",
        mode="before",
    )
    @classmethod
    def clean_required_text(cls, value: object) -> str:
        return _required_text(value)

    @field_validator("agent_tool_used", mode="before")
    @classmethod
    def clean_optional_text(cls, value: object) -> str:
        return _optional_text(value)

    @field_validator("changed_files", mode="before")
    @classmethod
    def clean_changed_files(cls, value: object) -> list[str]:
        return _required_text_list(value)

    def to_entry(self, timestamp: str) -> dict[str, str]:
        """Return the template context shape used by the agent run log template."""

        return {
            "timestamp": timestamp,
            "task_title": self.task_title,
            "task_goal": self.task_goal,
            "agent_tool_used": self.agent_tool_used,
            "prompt_summary": self.prompt_summary,
            "changed_files": "\n".join(f"- {item}" for item in self.changed_files),
            "verification_command": self.verification_command,
            "verification_result": self.verification_result,
            "what_worked": self.what_worked,
            "what_remains": self.what_remains,
            "lesson_learned": self.lesson_learned,
            "next_step": self.next_step,
        }


class ReportCheck(BaseModel):
    """One deterministic checker result for JSON output."""

    name: str
    status: str
    evidence: str
    suggestion: str = ""


class AgentCheckReport(BaseModel):
    """Machine-readable report for `lab agents check --json`."""

    path: str
    status: str
    score: int
    passed: bool
    checks: list[ReportCheck]
    missing_items: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class SkillReviewReport(BaseModel):
    """Machine-readable report for `lab skill review --json`."""

    path: str
    status: str
    score: int
    passed: bool
    strengths: list[str] = Field(default_factory=list)
    missing_items: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    checks: list[ReportCheck]
