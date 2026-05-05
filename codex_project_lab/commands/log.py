"""Codex run log command stubs."""

from pathlib import Path

import typer
from rich.console import Console

console = Console()


def add(log_file: Path = Path("logs/codex_runs.md")) -> None:
    """Stub for appending a Codex run log entry."""

    console.print(f"[yellow]Stub:[/yellow] log add is not implemented yet. Log: {log_file}")
