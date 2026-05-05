"""AGENTS.md validation command."""

from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

PASS = "PASS"
WARN = "WARN"
FAIL = "FAIL"


@dataclass(frozen=True)
class Requirement:
    name: str
    heading_keywords: tuple[str, ...]
    body_keywords: tuple[str, ...]
    suggestion: str


@dataclass(frozen=True)
class CheckResult:
    requirement: Requirement
    status: str
    evidence: str


REQUIREMENTS = (
    Requirement(
        name="Project purpose",
        heading_keywords=("project purpose", "purpose", "goal"),
        body_keywords=("project purpose", "helps", "goal", "mission"),
        suggestion="Add a section explaining what this project is for and what Codex should optimize for.",
    ),
    Requirement(
        name="Repo layout",
        heading_keywords=("repo layout", "repository layout", "project layout"),
        body_keywords=("repo layout", "repository layout", "directory", "folder", "package"),
        suggestion="Document the important directories and what each area owns.",
    ),
    Requirement(
        name="Setup command",
        heading_keywords=("setup command", "install command", "setup"),
        body_keywords=("setup command", "pip install", "npm install", "uv sync", "poetry install"),
        suggestion="Add the command a coding agent should run to install or prepare the project.",
    ),
    Requirement(
        name="Test command",
        heading_keywords=("test command", "tests", "test"),
        body_keywords=("test command", "pytest", "npm test", "cargo test", "go test"),
        suggestion="Add the command a coding agent should run to verify tests.",
    ),
    Requirement(
        name="Lint command",
        heading_keywords=("lint command", "lint", "format check"),
        body_keywords=("lint command", "ruff check", "npm run lint", "eslint", "cargo clippy"),
        suggestion="Add the command a coding agent should run for lint or static checks.",
    ),
    Requirement(
        name="Run command",
        heading_keywords=("run command", "start command", "run"),
        body_keywords=("run command", "python -m", "npm run dev", "npm start", "lab --help"),
        suggestion="Add the command a coding agent should run to start or smoke-test the project.",
    ),
    Requirement(
        name="Done criteria",
        heading_keywords=("done criteria", "definition of done", "acceptance criteria"),
        body_keywords=("done criteria", "definition of done", "acceptance criteria", "tests pass"),
        suggestion="Add concrete criteria that define when a change is complete.",
    ),
    Requirement(
        name="Do-not-build or do-not-change rules",
        heading_keywords=(
            "do not build",
            "do not change",
            "do not rules",
            "do not build items",
            "do not rules",
        ),
        body_keywords=("do not", "do-not", "do not build", "do not change", "do-not-build"),
        suggestion="Add boundaries for what Codex should avoid building or changing.",
    ),
    Requirement(
        name="AGENTS.md update rules",
        heading_keywords=("update rules", "agents update rules", "maintenance rules"),
        body_keywords=("update rules", "agents.md", "update agents"),
        suggestion="Add rules for when future changes should update AGENTS.md.",
    ),
)


def normalize(text: str) -> str:
    """Normalize text for practical v0.1 keyword checks."""

    return " ".join(text.lower().replace("-", " ").replace("_", " ").split())


def extract_headings(markdown: str) -> list[str]:
    """Return normalized Markdown headings."""

    headings = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip()
            if heading:
                headings.append(normalize(heading))
    return headings


def check_requirement(requirement: Requirement, headings: list[str], body: str) -> CheckResult:
    """Check one requirement using headings first, then body keywords."""

    heading_match = next(
        (
            heading
            for heading in headings
            if any(keyword in heading for keyword in requirement.heading_keywords)
        ),
        None,
    )
    if heading_match:
        return CheckResult(requirement, PASS, f"Found heading: {heading_match}")

    body_match = next(
        (keyword for keyword in requirement.body_keywords if normalize(keyword) in body),
        None,
    )
    if body_match:
        return CheckResult(requirement, WARN, f"Found keyword without clear heading: {body_match}")

    return CheckResult(requirement, FAIL, "Missing")


def score_results(results: list[CheckResult]) -> int:
    """Convert requirement checks to a 100-point score."""

    points = 0.0
    for result in results:
        if result.status == PASS:
            points += 1
        elif result.status == WARN:
            points += 0.5

    return round((points / len(results)) * 100)


def render_report(path: Path, results: list[CheckResult], score: int) -> None:
    """Print a Rich report for AGENTS.md quality."""

    overall = PASS if score >= 80 else FAIL
    color = "green" if overall == PASS else "red"
    console.print(
        Panel(
            f"[bold {color}]{overall}[/bold {color}]\nScore: [bold]{score}/100[/bold]\nFile: {path}",
            title="AGENTS.md Check",
        )
    )

    table = Table(title="Required Agent Guidance")
    table.add_column("Item", style="bold")
    table.add_column("Status")
    table.add_column("Evidence")
    table.add_column("Suggestion")

    styles = {PASS: "green", WARN: "yellow", FAIL: "red"}
    for result in results:
        suggestion = "" if result.status == PASS else result.requirement.suggestion
        table.add_row(
            result.requirement.name,
            f"[{styles[result.status]}]{result.status}[/{styles[result.status]}]",
            result.evidence,
            suggestion,
        )

    console.print(table)

    missing = [result.requirement.name for result in results if result.status == FAIL]
    warnings = [result.requirement.name for result in results if result.status == WARN]

    if missing:
        console.print("[red]Missing items:[/red]")
        for item in missing:
            console.print(f"- {item}")
    else:
        console.print("[green]Missing items:[/green] none")

    if warnings:
        console.print("[yellow]Improvement suggestions:[/yellow]")
        for result in results:
            if result.status == WARN:
                console.print(f"- {result.requirement.name}: {result.requirement.suggestion}")


def check(
    path: Annotated[
        Path,
        typer.Argument(help="Path to the AGENTS.md file to validate."),
    ] = Path("AGENTS.md"),
) -> None:
    """Validate whether an AGENTS.md file is useful for an AI coding agent."""

    if not path.exists():
        console.print(f"[red]File not found:[/red] {path}")
        raise typer.Exit(1)

    markdown = path.read_text(encoding="utf-8")
    headings = extract_headings(markdown)
    body = normalize(markdown)
    results = [check_requirement(requirement, headings, body) for requirement in REQUIREMENTS]
    score = score_results(results)

    render_report(path, results, score)

    if score < 80:
        raise typer.Exit(1)
