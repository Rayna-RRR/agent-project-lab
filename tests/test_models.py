import json
from pathlib import Path

import pytest

from agent_project_lab.models import InputFileError, ProjectInitInput, load_json_model

PROJECT_INPUT = {
    "project_name": "Agent Notes",
    "project_idea": "A local tool for turning meeting notes into agent-ready tasks.",
    "target_users": "Solo builders",
    "main_problem": "Project context is scattered.",
    "mvp_scope": ["Create project brief"],
    "tech_stack": ["Python"],
    "setup_command": "pip install -e .",
    "test_command": "pytest",
    "lint_command": "ruff check .",
    "run_command": "lab --help",
    "do_not_build": ["Web UI"],
    "done_criteria": ["Tests pass"],
}


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def test_load_json_model_validates_project_input(tmp_path: Path):
    input_path = tmp_path / "project.json"
    write_json(input_path, PROJECT_INPUT)

    project = load_json_model(input_path, ProjectInitInput)

    assert project.project_name == "Agent Notes"
    assert project.mvp_scope == ["Create project brief"]


def test_load_json_model_rejects_non_object_json(tmp_path: Path):
    input_path = tmp_path / "project.json"
    write_json(input_path, ["not", "an", "object"])

    with pytest.raises(InputFileError, match="Input JSON must be an object"):
        load_json_model(input_path, ProjectInitInput)


def test_load_json_model_rejects_unknown_fields(tmp_path: Path):
    input_path = tmp_path / "project.json"
    data = dict(PROJECT_INPUT)
    data["unexpected"] = "ignored fields should fail"
    write_json(input_path, data)

    with pytest.raises(InputFileError, match="unexpected"):
        load_json_model(input_path, ProjectInitInput)


def test_load_json_model_reports_non_utf8_input(tmp_path: Path):
    input_path = tmp_path / "project.json"
    input_path.write_bytes(b"\xff\xfe\x00")

    with pytest.raises(InputFileError, match="UTF-8"):
        load_json_model(input_path, ProjectInitInput)
