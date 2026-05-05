# Codex Run Logs

Append-only notes from Codex-assisted project runs. Use this file to capture prompts, changes, verification, lessons, and next steps.

## 2026-05-05 14:30:00 HKT - Add README checklist output

### Task Goal

Generate a Markdown checklist that helps users improve README structure.

### Codex Prompt Summary

Asked Codex to add a checklist template, wire it into the CLI output, and cover it with pytest.

### Changed Files

`readme_coach/templates/checklist.md.j2`, `readme_coach/commands/init.py`, `tests/test_init.py`

### Verification

- Command: `pytest`
- Result: passed

### What Worked

Keeping the template small made the generated Markdown easy to test.

### What Remains

Add a second example for library-style projects.

### Lesson Learned

Explicit acceptance criteria made the Codex task easier to verify.

### Next Step

Run the README review skill against the generated sample.
