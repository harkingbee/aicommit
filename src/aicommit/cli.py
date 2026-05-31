from __future__ import annotations

import os
import sys

import typer

from . import __version__
from .git import GitError, commit, staged_diff, staged_files
from .llm import LLMError, generate_commit_message

app = typer.Typer(
    name="aicommit",
    help="Generate Conventional Commits messages from staged git changes using the Claude API.",
    no_args_is_help=False,
    add_completion=False,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"aicommit {__version__}")
        raise typer.Exit()


@app.command()
def main(
    apply: bool = typer.Option(
        False,
        "--apply",
        "-a",
        help="Commit immediately with the generated message instead of just printing it.",
    ),
    model: str = typer.Option(
        "claude-haiku-4-5",
        "--model",
        "-m",
        help="Claude model ID to use.",
        envvar="AICOMMIT_MODEL",
    ),
    scope: str | None = typer.Option(
        None,
        "--scope",
        "-s",
        help="Optional Conventional Commits scope (e.g. 'api', 'cli').",
    ),
    max_diff_bytes: int = typer.Option(
        60_000,
        "--max-diff-bytes",
        help="Truncate the diff to this many bytes before sending it to the model.",
    ),
    version: bool = typer.Option(  # noqa: ARG001
        False,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """Read the staged diff, ask Claude for a commit message, print or commit it."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        typer.secho(
            "error: ANTHROPIC_API_KEY is not set. Export it before running aicommit.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=2)

    try:
        diff = staged_diff()
    except GitError as e:
        typer.secho(f"error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from e

    if not diff.strip():
        typer.secho(
            "no staged changes — run `git add` first.",
            fg=typer.colors.YELLOW,
            err=True,
        )
        raise typer.Exit(code=1)

    files = staged_files()
    truncated = len(diff.encode("utf-8")) > max_diff_bytes
    if truncated:
        diff = diff.encode("utf-8")[:max_diff_bytes].decode("utf-8", errors="ignore")

    try:
        message = generate_commit_message(
            diff=diff,
            files=files,
            scope=scope,
            model=model,
            truncated=truncated,
        )
    except LLMError as e:
        typer.secho(f"error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from e

    if apply:
        try:
            commit(message)
        except GitError as e:
            typer.secho(f"error: {e}", fg=typer.colors.RED, err=True)
            typer.echo(message)
            raise typer.Exit(code=1) from e
        typer.secho("committed:", fg=typer.colors.GREEN, err=True)
        typer.echo(message)
    else:
        typer.echo(message)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(app())
