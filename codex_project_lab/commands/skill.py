"""Agent skill commands."""

from pathlib import Path
import re
from typing import Annotated

from jinja2 import Environment, PackageLoader, select_autoescape
import typer
from rich.console import Console

console = Console()


def prompt_required(label: str) -> str:
    """Prompt for a required value and fail with a clear error if empty."""

    value = typer.prompt(label, default="", show_default=False).strip()
    if not value:
        console.print(f"[red]{label} is required.[/red]")
        raise typer.Exit(1)
    return value


def split_items(value: str) -> list[str]:
    """Split comma-separated prompt input into cleaned Markdown items."""

    return [item.strip() for item in value.split(",") if item.strip()]


def prompt_items(label: str) -> list[str]:
    """Prompt for a required comma-separated list."""

    items = split_items(typer.prompt(f"{label} (comma-separated)", default="", show_default=False))
    if not items:
        console.print(f"[red]{label} requires at least one item.[/red]")
        raise typer.Exit(1)
    return items


def normalize_skill_name(name: str) -> str:
    """Normalize a skill name to lowercase kebab-case."""

    lowered = name.strip().lower()
    slug = re.sub(r"\s+", "-", lowered)
    slug = re.sub(r"[^a-z0-9-]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")

    if not slug:
        raise ValueError("Skill name must contain at least one letter or number.")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ValueError("Skill name may only use letters, numbers, spaces, and hyphens.")

    return slug


def render_skill_template(skill: dict[str, object]) -> str:
    """Render the packaged skill template."""

    environment = Environment(
        loader=PackageLoader("codex_project_lab", "templates"),
        autoescape=select_autoescape(enabled_extensions=()),
        keep_trailing_newline=True,
        lstrip_blocks=True,
        trim_blocks=True,
    )
    rendered = environment.get_template("skill.md.j2").render(skill=skill)
    return rendered if rendered.endswith("\n") else f"{rendered}\n"


def new(
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Overwrite an existing SKILL.md file."),
    ] = False,
) -> None:
    """Create a reusable Agent Skill draft."""

    console.print("[bold]Codex Project Lab skill new[/bold]")

    raw_name = prompt_required("Skill name")
    try:
        slug = normalize_skill_name(raw_name)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    skill = {
        "name": raw_name.strip(),
        "slug": slug,
        "description": prompt_required("One-sentence description"),
        "when_to_use": prompt_required("When to use this skill"),
        "when_not_to_use": prompt_required("When not to use this skill"),
        "required_inputs": prompt_items("Required inputs"),
        "workflow_steps": prompt_items("Workflow steps"),
        "output_format": prompt_required("Output format"),
        "quality_bar": prompt_required("Quality bar"),
        "failure_handling": prompt_required("Failure handling"),
    }

    skill_path = Path(".agents") / "skills" / slug / "SKILL.md"
    if skill_path.exists() and not force:
        console.print(f"[red]Refusing to overwrite existing skill:[/red] {skill_path}")
        console.print("Re-run with --force to overwrite this skill draft.")
        raise typer.Exit(1)

    skill_path.parent.mkdir(parents=True, exist_ok=True)
    skill_path.write_text(render_skill_template(skill), encoding="utf-8")

    console.print("[green]Generated Agent Skill draft:[/green]")
    console.print(f"- Path: {skill_path}")
    console.print(f"- Skill name: {slug}")
    console.print("- Reminder: the description controls when an agent may use this skill.")


def review(skill_path: Path) -> None:
    """Stub for reviewing a SKILL.md file."""

    console.print(f"[yellow]Stub:[/yellow] skill review is not implemented yet. Path: {skill_path}")
