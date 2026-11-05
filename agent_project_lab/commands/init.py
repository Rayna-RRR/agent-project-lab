"""Project initialization command."""

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from agent_project_lab.models import InputFileError, ProjectInitInput, load_json_model
from agent_project_lab.render import render_markdown_template

console = Console()

GENERATED_FILES = {
    "PROJECT_BRIEF.md": "project_brief.md.j2",
    "AGENTS.md": "agents.md.j2",
    "TASKS.md": "tasks.md.j2",
}


def split_items(value: str) -> list[str]:
    """Split comma-separated prompt input into cleaned Markdown list items."""

    return [item.strip() for item in value.split(",") if item.strip()]


def prompt_text(label: str) -> str:
    """Prompt for a required single-line value."""

    value = typer.prompt(label).strip()
    if not value:
        console.print(f"[red]{label} is required.[/red]")
        raise typer.Exit(1)
    return value


def prompt_items(label: str) -> list[str]:
    """Prompt for a required comma-separated list."""

    items = split_items(typer.prompt(f"{label} (comma-separated)"))
    if not items:
        console.print(f"[red]{label} requires at least one item.[/red]")
        raise typer.Exit(1)
    return items


def collect_project() -> dict[str, object]:
    """Collect project fields using the existing interactive prompts."""

    return {
        "name": prompt_text("Project name"),
        "idea": prompt_text("One-sentence project idea"),
        "target_users": prompt_text("Target users"),
        "main_problem": prompt_text("Main problem solved"),
        "mvp_scope": prompt_items("MVP scope"),
        "tech_stack": prompt_items("Tech stack"),
        "setup_command": prompt_text("Setup command"),
        "test_command": prompt_text("Test command"),
        "lint_command": prompt_text("Lint command"),
        "run_command": prompt_text("Run command"),
        "do_not_build": prompt_items("Do-not-build items"),
        "done_criteria": prompt_items("Done criteria"),
    }


def load_project_from_file(path: Path) -> dict[str, object]:
    """Load non-interactive project input from a local JSON file."""

    try:
        return load_json_model(path, ProjectInitInput).to_template_project()
    except InputFileError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc


def init_project(
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Overwrite generated files if they already exist."),
    ] = False,
    from_file: Annotated[
        Optional[Path],
        typer.Option(
            "--from-file",
            help="Read project fields from a local JSON file instead of prompting.",
        ),
    ] = None,
) -> None:
    """Generate PROJECT_BRIEF.md, AGENTS.md, and TASKS.md for an agent-ready project."""

    console.print("[bold]Agent Project Lab init[/bold]")

    target_dir = Path.cwd()
    output_paths = {filename: target_dir / filename for filename in GENERATED_FILES}
    directory_paths = [path for path in output_paths.values() if path.is_dir()]
    if directory_paths:
        console.print("[red]Expected generated output paths to be files, got directories:[/red]")
        for path in directory_paths:
            console.print(f"- {path.name}")
        raise typer.Exit(1)

    existing_files = [path for path in output_paths.values() if path.exists()]

    if existing_files and not force:
        console.print("[red]Refusing to overwrite existing generated files:[/red]")
        for path in existing_files:
            console.print(f"- {path.name}")
        console.print("Re-run with --force to overwrite these files.")
        raise typer.Exit(1)

    project = load_project_from_file(from_file) if from_file else collect_project()

    generated: list[Path] = []
    for filename, template_name in GENERATED_FILES.items():
        path = output_paths[filename]
        rendered = render_markdown_template(template_name, {"project": project})
        path.write_text(rendered, encoding="utf-8")
        generated.append(path)

    console.print("[green]Generated project workflow files:[/green]")
    for path in generated:
        console.print(f"- {path.name}")
