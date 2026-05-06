"""CLI entry point for Agent Project Lab."""

import typer

from codex_project_lab.commands import agents, init, log, skill

app = typer.Typer(
    help="Local-first tools for shaping AI coding agent context, tasks, skills, and logs.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

agents_app = typer.Typer(help="AGENTS.md helpers.", no_args_is_help=True)
skill_app = typer.Typer(help="Agent skill helpers.", no_args_is_help=True)
log_app = typer.Typer(help="Agent run log helpers.", no_args_is_help=True)

app.command("init")(init.init_project)
agents_app.command("check")(agents.check)
skill_app.command("new")(skill.new)
skill_app.command("review")(skill.review)
log_app.command("add")(log.add)

app.add_typer(agents_app, name="agents")
app.add_typer(skill_app, name="skill")
app.add_typer(log_app, name="log")
