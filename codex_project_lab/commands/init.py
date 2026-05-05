"""Project initialization command stub."""

from pathlib import Path

import typer
from rich.console import Console

console = Console()


def init_project(target_dir: Path = Path(".")) -> None:
    """Stub for generating PROJECT_BRIEF.md, AGENTS.md, and TASKS.md."""

    console.print(f"[yellow]Stub:[/yellow] init is not implemented yet. Target: {target_dir}")
