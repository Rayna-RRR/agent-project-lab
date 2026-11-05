---
name: repo-onboarding
description: "Use when an agent needs to understand a new repository before making code changes."
---

# repo onboarding

## When To Use This Skill

When starting work in an unfamiliar repo or after a long break from the project.

## When Not To Use This Skill

Do not use for tiny edits where the target file and acceptance criteria are already clear.

## Required Inputs

- Repository path
- User goal
- Known constraints

## Workflow Steps

1. Inspect the README, AGENTS.md, pyproject/package config, and tests.
2. Identify setup, test, lint, and run commands.
3. Summarize project purpose, layout, risks, and next steps.

## Output Format

A concise Markdown briefing with commands, architecture notes, risks, and recommended next action.

## Quality Bar

The briefing is grounded in files that were actually inspected and avoids unsupported claims.

## Failure Handling

If key files are missing or commands cannot be inferred, report the blocker and ask for the minimum missing context.
