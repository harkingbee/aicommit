from __future__ import annotations

import subprocess


class GitError(RuntimeError):
    pass


def _run(args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as e:
        raise GitError("git executable not found in PATH") from e
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").strip()
        raise GitError(f"git {' '.join(args)} failed: {stderr}") from e
    return result.stdout


def staged_diff() -> str:
    """Return the unified diff of currently staged changes."""
    return _run(["diff", "--staged", "--no-color"])


def staged_files() -> list[str]:
    """Return the list of staged file paths."""
    out = _run(["diff", "--staged", "--name-only"])
    return [line for line in out.splitlines() if line]


def commit(message: str) -> str:
    """Create a commit with the given message and return git's output."""
    return _run(["commit", "-m", message])
