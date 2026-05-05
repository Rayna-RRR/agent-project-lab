"""Project initialization command."""

from pathlib import Path
from typing import Annotated

import typer
from jinja2 import Environment, PackageLoader, select_autoescape
from rich.console import Console

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


def render_template(template_name: str, context: dict[str, object]) -> str:
    """Render one packaged Markdown template."""

    environment = Environment(
        loader=PackageLoader("codex_project_lab", "templates"),
        autoescape=select_autoescape(enabled_extensions=()),
        keep_trailing_newline=True,
        lstrip_blocks=True,
        trim_blocks=True,
    )
    rendered = environment.get_template(template_name).render(**context)
    return rendered if rendered.endswith("\n") else f"{rendered}\n"


def init_project(
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Overwrite generated files if they already exist."),
    ] = False,
) -> None:
    """Generate PROJECT_BRIEF.md, AGENTS.md, and TASKS.md for an agent-ready project."""

    console.print("[bold]Codex Project Lab init[/bold]")

    project = {
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

    target_dir = Path.cwd()
    output_paths = {filename: target_dir / filename for filename in GENERATED_FILES}
    existing_files = [path for path in output_paths.values() if path.exists()]

    if existing_files and not force:
        console.print("[red]Refusing to overwrite existing generated files:[/red]")
        for path in existing_files:
            console.print(f"- {path.name}")
        console.print("Re-run with --force to overwrite these files.")
        raise typer.Exit(1)

    generated: list[Path] = []
    for filename, template_name in GENERATED_FILES.items():
        path = output_paths[filename]
        path.write_text(render_template(template_name, {"project": project}), encoding="utf-8")
        generated.append(path)

    console.print("[green]Generated project workflow files:[/green]")
    for path in generated:
        console.print(f"- {path.name}")
