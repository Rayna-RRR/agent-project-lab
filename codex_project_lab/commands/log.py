"""Agent run log commands."""

from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from jinja2 import Environment, PackageLoader, select_autoescape
from rich.console import Console

console = Console()

DEFAULT_LOG_FILE = Path("logs/codex_runs.md")


def prompt_required(label: str) -> str:
    """Prompt for a required log field."""

    value = typer.prompt(label, default="", show_default=False).strip()
    if not value:
        console.print(f"[red]{label} is required.[/red]")
        raise typer.Exit(1)
    return value


def render_log_template(include_header: bool, entry: dict[str, str]) -> str:
    """Render the packaged agent run log template."""

    environment = Environment(
        loader=PackageLoader("codex_project_lab", "templates"),
        autoescape=select_autoescape(enabled_extensions=()),
        keep_trailing_newline=True,
        lstrip_blocks=True,
        trim_blocks=True,
    )
    rendered = environment.get_template("codex_runs.md.j2").render(
        include_header=include_header,
        entry=entry,
    )
    return rendered if rendered.endswith("\n") else f"{rendered}\n"


def collect_entry() -> dict[str, str]:
    """Collect one agent run log entry interactively."""

    return {
        "timestamp": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"),
        "task_title": prompt_required("Task title"),
        "task_goal": prompt_required("Task goal"),
        "agent_tool_used": typer.prompt(
            "Agent/tool used (optional)",
            default="",
            show_default=False,
        ).strip(),
        "prompt_summary": prompt_required("Agent/tool prompt summary"),
        "changed_files": prompt_required("Changed files"),
        "verification_command": prompt_required("Verification command"),
        "verification_result": prompt_required("Verification result"),
        "what_worked": prompt_required("What worked"),
        "what_remains": prompt_required("What remains"),
        "lesson_learned": prompt_required("Lesson learned"),
        "next_step": prompt_required("Next step"),
    }


def add(
    log_file: Annotated[
        Path,
        typer.Option(
            "--file",
            "-f",
            help="Markdown file where the agent run log entry should be appended.",
        ),
    ] = DEFAULT_LOG_FILE,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Print the generated log entry without writing a file."),
    ] = False,
) -> None:
    """Append an agent run log entry to logs/codex_runs.md."""

    target = log_file
    if target.exists() and target.is_dir():
        console.print(f"[red]Expected a Markdown log file, got directory:[/red] {target}")
        raise typer.Exit(1)
    if target.parent.exists() and not target.parent.is_dir():
        console.print(
            f"[red]Expected log file parent to be a directory:[/red] {target.parent}"
        )
        raise typer.Exit(1)

    entry = collect_entry()
    include_header = not target.exists()
    rendered = render_log_template(include_header=include_header, entry=entry)

    if dry_run:
        console.print("[bold]Dry run: generated log entry[/bold]")
        console.print(rendered)
        return

    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        existing = target.read_text(encoding="utf-8")
        separator = "" if existing.endswith("\n") else "\n"
        target.write_text(f"{existing}{separator}{rendered}", encoding="utf-8")
    else:
        target.write_text(rendered, encoding="utf-8")

    console.print("[green]Appended agent run log entry:[/green]")
    console.print(f"- File: {target}")
    console.print(f"- Task: {entry['task_title']}")
    console.print(f"- Timestamp: {entry['timestamp']}")
