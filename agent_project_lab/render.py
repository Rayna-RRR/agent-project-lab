"""Markdown template rendering helpers."""

from functools import lru_cache

from jinja2 import Environment, PackageLoader, select_autoescape


@lru_cache(maxsize=1)
def template_environment() -> Environment:
    """Return the shared packaged-template environment."""

    return Environment(
        loader=PackageLoader("agent_project_lab", "templates"),
        autoescape=select_autoescape(enabled_extensions=()),
        keep_trailing_newline=True,
        lstrip_blocks=True,
        trim_blocks=True,
    )


def render_markdown_template(template_name: str, context: dict[str, object]) -> str:
    """Render a packaged Markdown template and keep a trailing newline."""

    rendered = template_environment().get_template(template_name).render(**context)
    return rendered if rendered.endswith("\n") else f"{rendered}\n"
