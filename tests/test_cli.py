from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from aicommit.cli import app


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init", "-q"], check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "config", "user.name", "Test"], check=True)
    subprocess.run(["git", "config", "commit.gpgsign", "false"], check=True)
    return tmp_path


def test_version_flag(runner: CliRunner) -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "aicommit" in result.stdout


def test_missing_api_key_errors(
    runner: CliRunner, repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    result = runner.invoke(app, [])
    assert result.exit_code == 2
    assert "ANTHROPIC_API_KEY" in result.stderr


def test_no_staged_changes_errors(
    runner: CliRunner, repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    result = runner.invoke(app, [])
    assert result.exit_code == 1
    assert "no staged changes" in result.stderr


def test_prints_generated_message(
    runner: CliRunner, repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    (repo / "f.txt").write_text("hi\n")
    subprocess.run(["git", "add", "f.txt"], check=True)

    with patch("aicommit.cli.generate_commit_message", return_value="feat: add f.txt"):
        result = runner.invoke(app, [])

    assert result.exit_code == 0
    assert "feat: add f.txt" in result.stdout
