"""Agent skill commands."""

import json as json_module
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agent_project_lab.models import (
    InputFileError,
    ReportCheck,
    SkillNewInput,
    SkillReviewReport,
    load_json_model,
)
from agent_project_lab.render import render_markdown_template

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


@dataclass(frozen=True)
class HeadingSection:
    heading: str
    content: str


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

    return render_markdown_template("skill.md.j2", {"skill": skill})


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


def extract_heading_sections(markdown: str) -> list[HeadingSection]:
    """Return normalized Markdown headings with their section content."""

    sections: list[HeadingSection] = []
    current_heading: Optional[str] = None
    current_content: list[str] = []

    def append_current_section() -> None:
        if current_heading is not None:
            sections.append(HeadingSection(current_heading, "\n".join(current_content).strip()))

    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            append_current_section()
            heading = stripped.lstrip("#").strip()
            current_heading = normalize_text(heading) if heading else None
            current_content = []
        elif current_heading is not None:
            current_content.append(line)

    append_current_section()
    return sections


def section_has_useful_content(content: str) -> bool:
    """Return whether a Markdown section contains more than placeholder text."""

    normalized = normalize_text(content)
    placeholders = {
        "tbd",
        "todo",
        "to do",
        "to be decided",
        "none",
        "n/a",
        "na",
        "coming soon",
    }
    return bool(normalized) and normalized not in placeholders


def has_section_or_keyword(
    sections: list[HeadingSection],
    body: str,
    keywords: tuple[str, ...],
) -> bool:
    """Check whether a useful section appears by heading or body keyword."""

    normalized_keywords = tuple(normalize_text(keyword) for keyword in keywords)
    section_match = next(
        (
            section
            for section in sections
            if any(keyword in section.heading for keyword in normalized_keywords)
        ),
        None,
    )
    if section_match:
        return section_has_useful_content(section_match.content)

    return any(keyword in body for keyword in normalized_keywords)


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


def print_json_payload(payload: object) -> None:
    """Print machine-readable JSON without Rich formatting."""

    typer.echo(json_module.dumps(payload, indent=2))


def print_json_model(model: SkillReviewReport) -> None:
    """Print a Pydantic model as machine-readable JSON."""

    typer.echo(model.model_dump_json(indent=2))


def path_error(path: Path, message: str, json_output: bool) -> None:
    """Emit a path error in Rich or JSON format and exit."""

    if json_output:
        print_json_payload(
            {
                "path": str(path),
                "status": "ERROR",
                "score": 0,
                "passed": False,
                "error": message,
            }
        )
    else:
        console.print(f"[red]{message}:[/red] {path}")
    raise typer.Exit(1)


def resolve_skill_path(path: Path, json_output: bool = False) -> Path:
    """Resolve a direct SKILL.md path or a skill directory containing SKILL.md."""

    if path.is_dir():
        skill_file = path / "SKILL.md"
        if not skill_file.exists():
            path_error(path, "Directory does not contain SKILL.md", json_output)
        return skill_file

    if not path.exists():
        path_error(path, "File not found", json_output)
    if path.name != "SKILL.md":
        path_error(path, "Expected a SKILL.md file or skill directory", json_output)

    return path


def review_skill_markdown(markdown: str) -> tuple[list[ReviewResult], int, str]:
    """Review a SKILL.md file using practical local checks."""

    frontmatter, body_markdown, has_frontmatter = parse_frontmatter(markdown)
    body = normalize_text(body_markdown)
    sections = extract_heading_sections(body_markdown)
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
            has_section_or_keyword(sections, body, ("when to use", "use this skill when")),
            "Found usage guidance",
        ),
        "When not to use": (
            has_section_or_keyword(sections, body, ("when not to use", "do not use")),
            "Found non-usage guidance",
        ),
        "Required inputs": (
            has_section_or_keyword(sections, body, ("required inputs", "inputs")),
            "Found required inputs guidance",
        ),
        "Workflow steps": (
            has_section_or_keyword(sections, body, ("workflow steps", "workflow")),
            "Found workflow guidance",
        ),
        "Output format": (
            has_section_or_keyword(sections, body, ("output format", "final output")),
            "Found output guidance",
        ),
        "Quality bar": (
            has_section_or_keyword(sections, body, ("quality bar", "quality standard")),
            "Found quality guidance",
        ),
        "Failure handling": (
            has_section_or_keyword(
                sections,
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


def build_review_report(
    path: Path,
    results: list[ReviewResult],
    score: int,
    status: str,
) -> SkillReviewReport:
    """Build a machine-readable skill review report."""

    strengths = [result.requirement.name for result in results if result.passed]
    missing = [result.requirement.name for result in results if not result.passed]
    suggestions = [
        f"{result.requirement.name}: {result.requirement.suggestion}"
        for result in results
        if not result.passed
    ]
    checks = [
        ReportCheck(
            name=result.requirement.name,
            status=PASS if result.passed else FAIL,
            evidence=result.evidence,
            suggestion="" if result.passed else result.requirement.suggestion,
        )
        for result in results
    ]

    return SkillReviewReport(
        path=str(path),
        status=status,
        score=score,
        passed=score >= 80,
        strengths=strengths,
        missing_items=missing,
        suggestions=suggestions,
        checks=checks,
    )


def new(
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Overwrite an existing SKILL.md file."),
    ] = False,
    from_file: Annotated[
        Optional[Path],
        typer.Option(
            "--from-file",
            help="Read skill fields from a local JSON file instead of prompting.",
        ),
    ] = None,
) -> None:
    """Create a reusable Agent Skill draft."""

    console.print("[bold]Agent Project Lab skill new[/bold]")

    if from_file:
        try:
            skill_input = load_json_model(from_file, SkillNewInput)
        except InputFileError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc
        raw_name = skill_input.skill_name
    else:
        skill_input = None
        raw_name = prompt_required("Skill name")

    try:
        slug = normalize_skill_name(raw_name)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    skill_path = Path(".agents") / "skills" / slug / "SKILL.md"
    if skill_path.exists() and not force:
        console.print(f"[red]Refusing to overwrite existing skill:[/red] {skill_path}")
        console.print("Re-run with --force to overwrite this skill draft.")
        raise typer.Exit(1)

    if skill_input is not None:
        skill = skill_input.to_template_skill(slug)
    else:
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
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Print a machine-readable JSON report."),
    ] = False,
) -> None:
    """Review a SKILL.md file and report Agent Skill design quality."""

    resolved_path = resolve_skill_path(skill_path, json_output=json_output)
    markdown = resolved_path.read_text(encoding="utf-8")
    results, score, status = review_skill_markdown(markdown)
    if json_output:
        print_json_model(build_review_report(resolved_path, results, score, status))
    else:
        render_review_report(resolved_path, results, score, status)

    if score < 80:
        raise typer.Exit(1)
