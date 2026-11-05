# Agent Project Lab

[![CI](https://github.com/Rayna-RRR/agent-project-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/Rayna-RRR/agent-project-lab/actions/workflows/ci.yml)

[English](README.md) | 简体中文

**一个本地 CLI，让编码智能体在下一次协作时仍能用上准确的项目上下文。**

把项目输入整理成项目简报、仓库规则、任务提示、Skill 和运行日志。
所有文件都是本地 Markdown 或 JSON；CI 覆盖 Python 3.9–3.12。

## 快速开始

在仓库根目录安装：

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
lab --help
```

在临时目录体验完整流程：

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

省略 `--from-file`，即可交互式运行 `lab init`、`lab skill new`、`lab log add`。
初始化自己的项目时，在目标项目根目录运行 `lab init`。

## 每个文件负责什么

| 文件 | 用途 |
| --- | --- |
| `PROJECT_BRIEF.md` | 用户、问题、范围和技术选择 |
| `AGENTS.md` | 项目目标、命令、目录、约束和完成标准 |
| `TASKS.md` | 任务目标、公共验证步骤和交接要求 |
| `.agents/skills/<name>/SKILL.md` | 可复用流程，包含发现元数据和执行步骤 |
| `logs/agent_runs.md` | 改动、验证证据、经验和下一步 |

产品背景集中在简报里，规则与任务引用它，减少重复上下文。
初始化后，把示例验收标准改成实际项目可验证的结果，并补上真实源码和测试路径。

这沿用 [AGENTS.md](https://agents.md/) 的仓库规则定位，以及
[Agent Skills](https://agentskills.io/specification) 先加载元数据、按需加载正文的方式。
Skill 的自动发现目录取决于所使用的智能体。

## 命令

| 命令 | 行为 |
| --- | --- |
| `lab init [--from-file PATH]` | 生成 `PROJECT_BRIEF.md`、`AGENTS.md`、`TASKS.md`。 |
| `lab agents check [PATH] [--json]` | 检查规则覆盖情况，默认读取 `AGENTS.md`。 |
| `lab skill new [--from-file PATH]` | 生成 `.agents/skills/<name>/SKILL.md`，名称转为小写短横线格式。 |
| `lab skill review PATH [--json]` | 检查 `SKILL.md` 文件或其所在目录。 |
| `lab log add [--from-file PATH]` | 追加运行日志；可用 `--file PATH` 指定位置。 |
| `lab log add --dry-run` | 预览日志，不写文件。 |

生成命令保留已有文件；需要覆盖时传入 `--force`。
`--from-file` 读取本地 JSON，字段与交互式流程一致。

## 如何理解检查结果

检查基于标题、关键词和占位符规则，用来发现缺失的协作信息。
**分数表示本工具检查清单的覆盖程度，不代表智能体表现或完整的格式合规性。**
AGENTS.md 和 Skill 正文可以自由组织，建议的章节是本工具的约定。

- 默认输出 Rich 终端报告。
- `--json` 返回 `status`、`score`、`passed`、`checks`、`missing_items`、`suggestions`。
- 分数至少 80 时退出码为 `0`；低于 80 或输入出错时为 `1`。
- Skill 报告另含 `strengths`。

用分数找缺口，再用真实任务检验内容是否有效。保留能改变智能体具体行动的信息，删掉重复和常识。
参考 [Skill 编写实践](https://agentskills.io/skill-creation/best-practices)。

## 示例

完整 JSON 输入：

- [项目初始化](examples/init_input.json)
- [Skill 草稿](examples/skill_input.json)
- [运行日志](examples/log_entry.json)

[examples 目录](examples/) 还包含生成的 Markdown 和完整 JSON 检查报告。
追加日志前可以先预览：

```bash
lab log add --from-file /path/to/log_entry.json --dry-run
```

## 开发

```bash
python -m pytest
ruff check .
python -m build
```

实现采用 Typer CLI、Pydantic 输入校验和打包的 Jinja2 模板。
CI 包含 Python 版本矩阵、macOS 完整演示，以及 wheel/sdist 独立安装检查。
构建和 GitHub Release 流程见 [RELEASING.md](RELEASING.md)。

v0.2.x 聚焦本地协作文件和确定性检查，无数据库、托管服务、模型调用或智能体执行。
新增能力应先解决实际工作流问题，再考虑增加配置与依赖。

## 许可证

MIT，见 [LICENSE](LICENSE)。
