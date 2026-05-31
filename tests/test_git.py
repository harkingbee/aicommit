from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from aicommit import git


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init", "-q"], check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "config", "user.name", "Test"], check=True)
    subprocess.run(["git", "config", "commit.gpgsign", "false"], check=True)
    return tmp_path


def test_staged_diff_empty_when_nothing_staged(repo: Path) -> None:
    assert git.staged_diff() == ""
    assert git.staged_files() == []


def test_staged_diff_returns_diff_after_add(repo: Path) -> None:
    (repo / "hello.txt").write_text("hello\n")
    subprocess.run(["git", "add", "hello.txt"], check=True)

    diff = git.staged_diff()
    assert "hello.txt" in diff
    assert "+hello" in diff
    assert git.staged_files() == ["hello.txt"]


def test_commit_creates_commit(repo: Path) -> None:
    (repo / "a.txt").write_text("a\n")
    subprocess.run(["git", "add", "a.txt"], check=True)

    git.commit("feat: add a.txt")

    log = subprocess.run(
        ["git", "log", "-1", "--pretty=%s"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert log == "feat: add a.txt"
