# Releasing Agent Project Lab

Agent Project Lab releases are built locally and published as GitHub Releases. PyPI publishing is
not part of the v0.2 release process.

## Prepare

1. Update the version in `pyproject.toml` and `agent_project_lab/__init__.py`.
2. Add the matching release heading and notes to `CHANGELOG.md`.
3. Install the development environment:

   ```bash
   python -m venv .venv
   . .venv/bin/activate
   python -m pip install --upgrade pip
   python -m pip install -e ".[dev]"
   ```

4. Run the local release checks:

   ```bash
   ruff check .
   pytest
   python -m build
   lab --help
   ```

5. Install both distributions in clean environments:

   ```bash
   python -m venv /tmp/agent-project-lab-wheel
   /tmp/agent-project-lab-wheel/bin/python -m pip install dist/*.whl
   /tmp/agent-project-lab-wheel/bin/lab --help

   python -m venv /tmp/agent-project-lab-sdist
   /tmp/agent-project-lab-sdist/bin/python -m pip install dist/*.tar.gz
   /tmp/agent-project-lab-sdist/bin/lab --help
   ```

6. Open a pull request and merge only after every CI job passes.

## Release

From an up-to-date `main` branch, create and push the version tag:

```bash
git tag v0.2.2
git push origin v0.2.2
```

The release workflow verifies that the tag matches both version declarations, builds wheel and
source archives, installs each archive in a clean environment, and creates a GitHub Release with
generated notes.

## Confirm

1. Confirm the tag workflow completed successfully.
2. Confirm the GitHub Release contains one `.whl` and one `.tar.gz` asset.
3. Download either asset and verify `lab --help` from a clean virtual environment.
