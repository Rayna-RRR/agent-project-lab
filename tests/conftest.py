import pytest


@pytest.fixture(autouse=True)
def project_directory(tmp_path, monkeypatch):
    """Give every test a fresh project directory, independent of the CLI runner."""

    monkeypatch.chdir(tmp_path)
