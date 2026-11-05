# Agent Project Lab

[![CI](https://github.com/Rayna-RRR/agent-project-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/Rayna-RRR/agent-project-lab/actions/workflows/ci.yml)

English | [简体中文](README.zh-CN.md)

**A local CLI for keeping coding-agent context useful between sessions.**

Turn project inputs into a brief, repository instructions, task prompts, Skills, and run logs.
Everything is local Markdown or JSON; Python 3.9–3.12 is covered by CI.

## Quickstart

From a checkout:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
lab --help
```

Try the full workflow in a temporary directory:

```bash
repo_dir="$PWD"
demo_dir="$(mktemp -d)"
cd "$demo_dir"
lab init --from-file "$repo_dir/examples/init_input.json"
lab agents check AGENTS.md --json
lab skill new --from-file "$repo_dir/examples/skill_input.json"
lab skill review .agents/skills/repo-onboarding --json
lab log add --from-file "$repo_dir/examples/log_entry.json"
```

Use `lab init`, `lab skill new`, or `lab log add` without `--from-file` for interactive prompts.
To initialize your own project, run `lab init` from its root.

## What Goes Where

| File | Purpose |
| --- | --- |
| `PROJECT_BRIEF.md` | Users, problem, scope, and technology choices |
| `AGENTS.md` | Project purpose, commands, repository paths, constraints, and completion criteria |
| `TASKS.md` | Task objectives with shared verification and handoff instructions |
| `.agents/skills/<name>/SKILL.md` | A reusable procedure with discovery metadata and workflow steps |
| `logs/agent_runs.md` | Changes, verification evidence, lessons, and the next step |

The brief holds product context; repository rules and task prompts refer to it instead of copying
it into every file. After initialization, replace starter criteria with checks for your actual
project and add source/test paths as they become known.

This follows the role of [AGENTS.md](https://agents.md/) as repository guidance and the
[Agent Skills](https://agentskills.io/specification) model of loading metadata first and detailed
instructions when needed. Skill discovery locations depend on the agent you use.

## Commands

| Command | Behavior |
| --- | --- |
| `lab init [--from-file PATH]` | Generate `PROJECT_BRIEF.md`, `AGENTS.md`, and `TASKS.md`. |
| `lab agents check [PATH] [--json]` | Review guidance coverage; defaults to `AGENTS.md`. |
| `lab skill new [--from-file PATH]` | Generate `.agents/skills/<name>/SKILL.md`. Names become lowercase kebab-case. |
| `lab skill review PATH [--json]` | Review a `SKILL.md` file or its directory. |
| `lab log add [--from-file PATH]` | Append a run log. Use `--file PATH` for a custom destination. |
| `lab log add --dry-run` | Preview an entry without writing it. |

Generation commands preserve existing files unless `--force` is passed. `--from-file` accepts
local JSON using the same fields as the interactive workflow.

## Reading Check Results

Checks use local heading, keyword, and placeholder heuristics. They help find missing guidance;
a score is **coverage of this tool's checklist**, not proof of agent performance or full format
compliance. AGENTS.md and Skill body headings are flexible; the suggested structure is this
tool's convention.

- Default output is a Rich terminal report.
- `--json` returns `status`, `score`, `passed`, `checks`, `missing_items`, and `suggestions`.
- Exit `0` means a score of at least 80; exit `1` means a lower score or an input error.
- Skill reports also include `strengths`.

Use the score to find gaps, then check the content against a real task. Keep instructions that
change an agent's actions; remove repetitions and generic advice. See the
[Skill authoring guidance](https://agentskills.io/skill-creation/best-practices).

## Examples

Start with these complete JSON inputs:

- [Project setup](examples/init_input.json)
- [Skill drafting](examples/skill_input.json)
- [Run log](examples/log_entry.json)

The [examples directory](examples/) also includes generated Markdown and full JSON review reports.
To inspect a log before appending:

```bash
lab log add --from-file /path/to/log_entry.json --dry-run
```

## Development

```bash
python -m pytest
ruff check .
python -m build
```

The implementation is a small Typer CLI with Pydantic input validation and packaged Jinja2
templates. CI runs the Python matrix, a macOS demo, and clean wheel/sdist installation checks.
See [RELEASING.md](RELEASING.md) for packaging and GitHub Releases.

v0.2.x stays focused on local workflow files and deterministic reviews. It has no database,
hosted service, model calls, or agent execution. New capabilities should solve a demonstrated
workflow problem before adding configuration or dependencies.

## License

MIT. See [LICENSE](LICENSE).
