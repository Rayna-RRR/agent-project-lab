"""Agent skill commands."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import typer
from jinja2 import Environment, PackageLoader, select_autoescape
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

PASS = "PASS"
WARN = "WARN"
FAIL = "FAIL"


@dataclass(frozen=True)
class ReviewRequirement:
    name: str
    weight: int
    suggestion: str


@dataclass(frozen=True)
class ReviewResult:
    requirement: ReviewRequirement
    passed: bool
    evidence: str


REVIEW_REQUIREMENTS = (
    ReviewRequirement("YAML frontmatter", 10, "Add YAML frontmatter between --- markers."),
    ReviewRequirement("Frontmatter name", 8, "Add a name field to the YAML frontmatter."),
    ReviewRequirement(
        "Frontmatter description",
        8,
        "Add a description field to the YAML frontmatter.",
    ),
    ReviewRequirement(
        "Name format",
        8,
        "Use lowercase kebab-case for the frontmatter name, such as review-skill-draft.",
    ),
    ReviewRequirement(
        "Specific description",
        8,
        "Make the description specific enough to distinguish this skill from generic guidance.",
    ),
    ReviewRequirement(
        "Description trigger",
        8,
        "Include a clear trigger condition in the description, such as 'Use when...'.",
    ),
    ReviewRequirement("When to use", 8, "Add a section describing when to use this skill."),
    ReviewRequirement(
        "When not to use",
        7,
        "Add a section describing when this skill should not be used.",
    ),
    ReviewRequirement("Required inputs", 7, "List required inputs or context before use."),
    ReviewRequirement("Workflow steps", 8, "Add concrete workflow steps."),
    ReviewRequirement("Output format", 6, "Define the expected output format."),
    ReviewRequirement("Quality bar", 6, "Define the quality bar for a good result."),
    ReviewRequirement("Failure handling", 8, "Explain how to handle missing inputs or blockers."),
)


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


def normalize_text(value: str) -> str:
    """Normalize prose for practical keyword checks."""

    return " ".join(value.lower().replace("-", " ").replace("_", " ").split())


def parse_frontmatter(markdown: str) -> tuple[dict[str, str], str, bool]:
    """Parse simple YAML frontmatter without adding a YAML dependency."""

    lines = markdown.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, markdown, False

    closing_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_index = index
            break

    if closing_index is None:
        return {}, markdown, False

    frontmatter: dict[str, str] = {}
    for line in lines[1:closing_index]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip().lower()] = value.strip().strip('"').strip("'")

    body = "\n".join(lines[closing_index + 1 :])
    return frontmatter, body, True


def extract_headings(markdown: str) -> list[str]:
    """Return normalized Markdown headings."""

    headings = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip()
            if heading:
                headings.append(normalize_text(heading))
    return headings


def has_heading_or_keyword(headings: list[str], body: str, keywords: tuple[str, ...]) -> bool:
    """Check whether a section appears by heading or body keyword."""

    normalized_keywords = tuple(normalize_text(keyword) for keyword in keywords)
    return any(
        any(keyword in heading for keyword in normalized_keywords) for heading in headings
    ) or any(keyword in body for keyword in normalized_keywords)


def description_is_specific(description: str) -> bool:
    """Decide whether a skill description has enough practical detail for v0.1."""

    words = re.findall(r"[a-zA-Z0-9]+", description)
    generic_descriptions = {
        "useful skill",
        "helper skill",
        "does things",
        "skill",
        "review stuff",
    }
    return (
        len(description.strip()) >= 50
        and len(words) >= 8
        and normalize_text(description) not in generic_descriptions
    )


def description_has_trigger(description: str) -> bool:
    """Check for a practical trigger phrase in the description."""

    normalized = normalize_text(description)
    trigger_patterns = (
        "use when",
        "when the user",
        "when a user",
        "whenever",
        "if the user",
        "if a user",
        "asks to",
        "needs to",
        "for users who",
    )
    return any(pattern in normalized for pattern in trigger_patterns)


def name_is_kebab_case(name: str) -> bool:
    """Return whether a name is lowercase kebab-case."""

    return bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name))


def resolve_skill_path(path: Path) -> Path:
    """Resolve a direct SKILL.md path or a skill directory containing SKILL.md."""

    if path.is_dir():
        skill_file = path / "SKILL.md"
        if not skill_file.exists():
            console.print(f"[red]Directory does not contain SKILL.md:[/red] {path}")
            raise typer.Exit(1)
        return skill_file

    if not path.exists():
        console.print(f"[red]File not found:[/red] {path}")
        raise typer.Exit(1)

    return path


def review_skill_markdown(markdown: str) -> tuple[list[ReviewResult], int, str]:
    """Review a SKILL.md file using practical local checks."""

    frontmatter, body_markdown, has_frontmatter = parse_frontmatter(markdown)
    body = normalize_text(body_markdown)
    headings = extract_headings(body_markdown)
    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")

    checks = {
        "YAML frontmatter": (has_frontmatter, "Found --- frontmatter block"),
        "Frontmatter name": (bool(name), f"name: {name}" if name else "Missing name"),
        "Frontmatter description": (
            bool(description),
            "Found description" if description else "Missing description",
        ),
        "Name format": (
            bool(name) and name_is_kebab_case(name),
            f"name: {name}" if name else "Missing name",
        ),
        "Specific description": (
            bool(description) and description_is_specific(description),
            description or "Missing description",
        ),
        "Description trigger": (
            bool(description) and description_has_trigger(description),
            description or "Missing description",
        ),
        "When to use": (
            has_heading_or_keyword(headings, body, ("when to use", "use this skill when")),
            "Found usage guidance",
        ),
        "When not to use": (
            has_heading_or_keyword(headings, body, ("when not to use", "do not use")),
            "Found non-usage guidance",
        ),
        "Required inputs": (
            has_heading_or_keyword(headings, body, ("required inputs", "inputs")),
            "Found required inputs guidance",
        ),
        "Workflow steps": (
            has_heading_or_keyword(headings, body, ("workflow steps", "workflow")),
            "Found workflow guidance",
        ),
        "Output format": (
            has_heading_or_keyword(headings, body, ("output format", "final output")),
            "Found output guidance",
        ),
        "Quality bar": (
            has_heading_or_keyword(headings, body, ("quality bar", "quality standard")),
            "Found quality guidance",
        ),
        "Failure handling": (
            has_heading_or_keyword(
                headings,
                body,
                ("failure handling", "blocker", "missing inputs"),
            ),
            "Found failure guidance",
        ),
    }

    results = [
        ReviewResult(requirement, checks[requirement.name][0], checks[requirement.name][1])
        for requirement in REVIEW_REQUIREMENTS
    ]
    score = sum(result.requirement.weight for result in results if result.passed)

    if score >= 80:
        status = PASS
    elif score >= 60:
        status = WARN
    else:
        status = FAIL

    return results, score, status


def render_review_report(path: Path, results: list[ReviewResult], score: int, status: str) -> None:
    """Print a Rich quality report for a skill review."""

    color = {PASS: "green", WARN: "yellow", FAIL: "red"}[status]
    console.print(
        Panel(
            f"[bold {color}]{status}[/bold {color}]\nScore: [bold]{score}/100[/bold]\nFile: {path}",
            title="Skill Quality Report",
        )
    )

    table = Table(title="Agent Skill Design Checks")
    table.add_column("Item", style="bold")
    table.add_column("Status")
    table.add_column("Evidence")
    table.add_column("Suggestion")

    for result in results:
        item_status = PASS if result.passed else FAIL
        item_color = "green" if result.passed else "red"
        suggestion = "" if result.passed else result.requirement.suggestion
        table.add_row(
            result.requirement.name,
            f"[{item_color}]{item_status}[/{item_color}]",
            result.evidence,
            suggestion,
        )

    console.print(table)

    strengths = [result.requirement.name for result in results if result.passed]
    missing = [result.requirement.name for result in results if not result.passed]

    console.print("[green]Detected strengths:[/green]")
    if strengths:
        for item in strengths:
            console.print(f"- {item}")
    else:
        console.print("- none")

    console.print("[red]Missing items:[/red]")
    if missing:
        for item in missing:
            console.print(f"- {item}")
    else:
        console.print("- none")

    suggestions = [result for result in results if not result.passed]
    console.print("[yellow]Improvement suggestions:[/yellow]")
    if suggestions:
        for result in suggestions:
            console.print(f"- {result.requirement.name}: {result.requirement.suggestion}")
    else:
        console.print("- none")


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


def review(
    skill_path: Annotated[
        Path,
        typer.Argument(help="Path to a SKILL.md file or a skill directory containing SKILL.md."),
    ],
) -> None:
    """Review a SKILL.md file and report Agent Skill design quality."""

    resolved_path = resolve_skill_path(skill_path)
    markdown = resolved_path.read_text(encoding="utf-8")
    results, score, status = review_skill_markdown(markdown)
    render_review_report(resolved_path, results, score, status)

    if score < 80:
        raise typer.Exit(1)
