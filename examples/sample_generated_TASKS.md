# Readme Steward Tasks

Read [PROJECT_BRIEF.md](PROJECT_BRIEF.md) for product context and [AGENTS.md](AGENTS.md) for repository rules.

## Working Method

For each task, define one observable acceptance check, implement the outcome, and run the relevant verification below.

## Verification

- Test: `pytest`
- Lint: `ruff check .`
- Smoke test: `lab --help`

## Project Acceptance Criteria

- Generated Markdown is readable
- Commands are documented
- Tests pass locally

## Handoff

Report the changed behavior and files, verification commands with actual results, and the next unfinished task.

## Task 1: Generate a README improvement brief

Implement `Generate a README improvement brief`. Demonstrate the result with a task-specific check and use the shared verification and acceptance criteria above.

## Task 2: Create agent-ready repository rules

Implement `Create agent-ready repository rules`. Demonstrate the result with a task-specific check and use the shared verification and acceptance criteria above.

## Task 3: Draft reusable README cleanup tasks

Implement `Draft reusable README cleanup tasks`. Demonstrate the result with a task-specific check and use the shared verification and acceptance criteria above.
