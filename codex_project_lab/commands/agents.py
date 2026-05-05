"""AGENTS.md command stubs."""

from pathlib import Path

import typer
from rich.console import Console

console = Console()


def check(path: Path = Path("AGENTS.md")) -> None:
    """Stub for checking whether AGENTS.md contains required project guidance."""

    console.print(f"[yellow]Stub:[/yellow] agents check is not implemented yet. Path: {path}")
