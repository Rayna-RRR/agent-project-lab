"""Agent skill command stubs."""

from pathlib import Path

import typer
from rich.console import Console

console = Console()


def new(skill_name: str) -> None:
    """Stub for creating a new Agent Skill draft."""

    console.print(f"[yellow]Stub:[/yellow] skill new is not implemented yet. Skill: {skill_name}")


def review(skill_path: Path) -> None:
    """Stub for reviewing a SKILL.md file."""

    console.print(f"[yellow]Stub:[/yellow] skill review is not implemented yet. Path: {skill_path}")
