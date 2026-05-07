# Agent Project Lab

[English](README.md) | 简体中文

**一个本地优先、平台无关的 AI coding agent 工作流 CLI，用来把模糊项目想法整理成可复用、可检查、可沉淀的工程协作资产。**

Agent Project Lab 不是 AI coding agent，也不替代任何 AI coding agent。它更像一个“项目工作流整理器”：帮助开发者把项目背景、协作规则、任务拆解、Agent Skill 草稿和运行日志落到本地 Markdown / JSON 文件里，让后续的人机协作更清晰、更可复用、更容易验证。

## 项目解决的问题

AI coding agent 很适合写代码、改 bug、补测试，但很多项目在真正开始协作前，缺少稳定的上下文：

- 项目想法只存在聊天记录里，下一次很难复用。
- setup、test、lint、run 命令没有集中记录。
- 仓库规则、不要做什么、完成标准分散在不同地方。
- 好用的提示词和工作流没有沉淀成 Skill。
- 每次 agent 协作做了什么、验证了什么、学到了什么，没有日志。

Agent Project Lab 的目标不是“自动写代码”，而是把这些前置和复盘信息结构化，帮助 AI 协作开发流程变得更稳定。

## 这个工具能做什么

- 通过 `lab init` 把项目想法整理成 `PROJECT_BRIEF.md`、`AGENTS.md` 和 `TASKS.md`。
- 通过 `lab agents check` 检查 `AGENTS.md` 是否包含对 AI coding agent 有用的项目规则。
- 通过 `lab skill new` 生成 Agent Skill 草稿。
- 通过 `lab skill review` 检查 `SKILL.md` 的触发条件、边界、输入、流程、输出格式和失败处理。
- 通过 `lab log add` 记录一次 agent-assisted development 的运行日志。
- 通过 `--from-file JSON` 支持脚本化、可复现的本地工作流。
- 通过 `--json` 输出支持机器可读的检查报告。

## 这个工具不做什么

- 不替代任何 AI coding agent。
- 不执行自动编码任务。
- 不调用外部 API。
- 不连接任何 AI coding agent 产品。
- 不提供 Web UI 或 TUI。
- 不使用数据库。
- 不声称自己是生产级 agent 平台。

## 核心功能表

| 模块 | v0.2.0 功能 |
| --- | --- |
| 项目初始化 | `lab init`、`lab init --from-file JSON` |
| Agent 规则检查 | `lab agents check`、`lab agents check --json` |
| Skill 草稿生成 | `lab skill new`、`lab skill new --from-file JSON` |
| Skill 质量检查 | `lab skill review`、`lab skill review --json` |
| 运行日志 | `lab log add`、`lab log add --from-file JSON`、`lab log add --dry-run` |
| 结构化校验 | Pydantic 校验本地 JSON 输入 |
| 模板生成 | Jinja2 渲染 Markdown 输出 |
| 工程验证 | pytest 测试和 Ruff lint |

## Demo Flow / 快速体验

```bash
lab init --from-file examples/init_input.json
lab agents check AGENTS.md --json
lab skill new --from-file examples/skill_input.json
lab skill review .agents/skills/repo-onboarding --json
lab log add --from-file examples/log_entry.json
```

这条流程会演示 v0.2.0 的核心能力：从 JSON 输入生成项目工作流文件，检查 agent 规则，生成和 review Skill，并记录一次 agent run log。

## 安装与本地运行

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

查看 CLI：

```bash
lab --help
```

交互式使用：

```bash
lab init
lab agents check
lab skill new
lab skill review .agents/skills/repo-onboarding
lab log add
```

## 命令说明

| 命令 | 作用 | 说明 |
| --- | --- | --- |
| `lab init` | 生成项目工作流文件 | 交互式提问并生成 `PROJECT_BRIEF.md`、`AGENTS.md`、`TASKS.md`。 |
| `lab init --from-file PATH` | 非交互初始化 | 从本地 JSON 文件读取项目字段。 |
| `lab agents check [PATH]` | 检查 `AGENTS.md` | 默认检查当前目录下的 `AGENTS.md`，输出 Rich 报告。 |
| `lab agents check [PATH] --json` | 输出 JSON 检查结果 | 适合脚本、CI 或其他自动化读取。 |
| `lab skill new` | 生成 Agent Skill 草稿 | 生成 `.agents/skills/<skill-name>/SKILL.md`。 |
| `lab skill new --from-file PATH` | 非交互生成 Skill | 从本地 JSON 文件读取 Skill 字段。 |
| `lab skill review PATH` | 检查 Skill 质量 | 支持传入 `SKILL.md` 文件或包含 `SKILL.md` 的目录。 |
| `lab skill review PATH --json` | 输出 JSON review 报告 | 返回分数、状态、优点、缺失项和修改建议。 |
| `lab log add` | 追加运行日志 | 记录任务目标、提示摘要、改动文件、验证结果和经验沉淀。 |
| `lab log add --from-file PATH` | 非交互追加日志 | 从本地 JSON 文件读取日志字段。 |
| `lab log add --dry-run` | 预览日志 | 只打印生成内容，不写入文件。 |

## JSON 输入与 JSON 输出

v0.2.0 的非交互输入只支持 JSON，不支持 YAML。这是为了保持依赖简单，也方便用 Pydantic 做确定性校验。

示例项目输入：

```json
{
  "project_name": "Readme Steward",
  "project_idea": "A local CLI that helps maintain clear README files for small software projects.",
  "target_users": "Solo developers and small teams using AI coding agents",
  "main_problem": "README updates are often skipped because project context and verification steps are scattered.",
  "mvp_scope": ["Generate a README improvement brief", "Create agent-ready repository rules"],
  "tech_stack": ["Python", "Typer", "Rich"],
  "setup_command": "pip install -e \".[dev]\"",
  "test_command": "pytest",
  "lint_command": "ruff check .",
  "run_command": "lab --help",
  "do_not_build": ["Web UI", "Database", "External API calls"],
  "done_criteria": ["Generated Markdown is readable", "Tests pass locally"]
}
```

checker 命令可以输出 JSON：

```bash
lab agents check AGENTS.md --json
lab skill review .agents/skills/repo-onboarding --json
```

报告会包含：

- `status`
- `score`
- `passed`
- `checks`
- `missing_items`
- `suggestions`

这让它可以被脚本、CI 或其他本地自动化流程读取。

## examples 目录说明

[examples/](examples/) 目录提供了短小但完整的示例：

- `sample_project_idea.md`：一个原始项目想法。
- `sample_generated_PROJECT_BRIEF.md`：生成后的项目 brief。
- `sample_generated_AGENTS.md`：生成后的 agent 协作规则。
- `sample_generated_TASKS.md`：生成后的任务提示包。
- `sample_skill.md`：示例 Agent Skill。
- `sample_agent_runs.md`：示例运行日志。
- `init_input.json`：`lab init --from-file` 示例输入。
- `skill_input.json`：`lab skill new --from-file` 示例输入。
- `log_entry.json`：`lab log add --from-file` 示例输入。
- `agents_check_report.json`：`lab agents check --json` 示例输出。
- `skill_review_report.json`：`lab skill review --json` 示例输出。

## 项目结构

```text
agent-project-lab/
  agent_project_lab/
    cli.py
    models.py
    render.py
    commands/
    templates/
  examples/
  tests/
  AGENTS.md
  CHANGELOG.md
  LICENSE
  README.md
  README.zh-CN.md
  pyproject.toml
```

## v0.2.0 当前范围

- Python CLI，基于 Typer 和 Rich。
- 使用 Jinja2 模板生成 Markdown。
- 使用 Pydantic 校验结构化 JSON 输入。
- 本地生成 `PROJECT_BRIEF.md`、`AGENTS.md`、`TASKS.md`、`SKILL.md` 和 agent run logs。
- 本地、确定性的 `AGENTS.md` / `SKILL.md` 检查。
- checker 支持 JSON 输出。
- pytest 测试覆盖主要 CLI 行为。
- Ruff 用于 lint。
- 无 Web UI、无数据库、无外部 API 调用、无隐藏网络请求、无直接产品集成。

## 后续路线

v0.3 可以考虑：

- YAML 输入支持。
- JSON Schema 导出。
- 输入 schema 版本管理和迁移。
- 更细粒度的非交互 CLI 参数。
- 可配置模板包。
- 更强的 Markdown 解析。
- 项目 profile 文件。
- SARIF 或更丰富的报告格式。
- 对 `AGENTS.md` / `SKILL.md` 的自动修复建议。

这些都属于后续增强，不是 v0.2.0 的范围。

## 作品集与求职价值

这个项目适合作为国内实习投递和作品集展示项目，重点不在“做了一个很大的 agent 平台”，而在于展示：

- 能把 AI 协作开发流程拆成清晰、可复用的工程资产。
- 能用 CLI 解决真实开发流程里的上下文管理问题。
- 能用 Pydantic / pytest / Ruff 把输入校验、行为测试和质量检查做扎实。
- 能从 v0.1 到 v0.2 逐步迭代功能，而不是一次性堆功能。
- 能明确产品边界：local-first、不调用外部 API、不替代 AI coding agent。

对 HR 来说，它展示的是完整度和表达能力；对业务面试官来说，它展示的是对开发协作流程的理解；对技术面试官来说，它展示的是 CLI 设计、结构化校验、模板渲染、测试和工程边界意识。

## 开发与验证命令

```bash
python -m pytest
ruff check .
```

也可以直接检查 CLI：

```bash
lab --help
lab agents check AGENTS.md
```

## License

MIT. See [LICENSE](LICENSE).
