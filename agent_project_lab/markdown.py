"""Shared helpers for deterministic Markdown checks."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class HeadingSection:
    """One normalized ATX heading and its body content."""

    heading: str
    content: str


def normalize_text(value: str) -> str:
    """Normalize prose for practical keyword checks."""

    return " ".join(value.lower().replace("-", " ").replace("_", " ").split())


def strip_fenced_code_blocks(markdown: str) -> str:
    """Remove fenced code blocks while preserving surrounding prose."""

    visible_lines: list[str] = []
    fence_character: Optional[str] = None
    fence_length = 0

    for line in markdown.splitlines():
        fence_match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if fence_character is None:
            if fence_match:
                marker = fence_match.group(1)
                fence_character = marker[0]
                fence_length = len(marker)
                continue
            visible_lines.append(line)
            continue

        closing_pattern = rf"^\s{{0,3}}{re.escape(fence_character)}{{{fence_length},}}\s*$"
        if re.match(closing_pattern, line):
            fence_character = None
            fence_length = 0

    return "\n".join(visible_lines)


def extract_heading_sections(markdown: str) -> list[HeadingSection]:
    """Return normalized Markdown ATX headings with their section content."""

    sections: list[HeadingSection] = []
    current_heading: Optional[str] = None
    current_content: list[str] = []
    fence_character: Optional[str] = None
    fence_length = 0

    def append_current_section() -> None:
        if current_heading is not None:
            sections.append(HeadingSection(current_heading, "\n".join(current_content).strip()))

    heading_pattern = re.compile(
        r"^\s{0,3}#{1,6}(?:[ \t]+|$)(.*?)(?:[ \t]+#+[ \t]*)?$"
    )

    for line in markdown.splitlines():
        fence_match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if fence_character is None and fence_match:
            marker = fence_match.group(1)
            fence_character = marker[0]
            fence_length = len(marker)
            if current_heading is not None:
                current_content.append(line)
            continue

        if fence_character is not None:
            if current_heading is not None:
                current_content.append(line)
            closing_pattern = rf"^\s{{0,3}}{re.escape(fence_character)}{{{fence_length},}}\s*$"
            if re.match(closing_pattern, line):
                fence_character = None
                fence_length = 0
            continue

        heading_match = heading_pattern.match(line)
        if heading_match:
            append_current_section()
            heading = heading_match.group(1).strip()
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
