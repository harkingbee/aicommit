# aicommit

[![CI](https://github.com/harkingbee/aicommit/actions/workflows/ci.yml/badge.svg)](https://github.com/harkingbee/aicommit/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Generate **Conventional Commits** messages from your staged `git` changes using the **Claude API**.

`aicommit` reads `git diff --staged`, sends it to Claude, and prints a properly formatted commit message — or commits it directly with `--apply`.

```text
$ git add src/parser.py tests/test_parser.py
$ aicommit
fix(parser): handle empty diff hunks without crashing

The hunk iterator previously assumed at least one line per hunk,
which raised IndexError when git emitted a header-only hunk for
binary file boundary changes. Guard the iterator and skip empties.
```

## Why?

Most developers either spend 30 seconds writing a vague commit message or skip the message entirely with `git commit -m "wip"`. Both rot the project history. `aicommit` removes the friction by generating a thoughtful, Conventional Commits-compliant message from the staged diff in about a second.

## Install

```bash
pip install aicommit
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv tool install aicommit
```

Requires Python 3.10+ and an [Anthropic API key](https://console.anthropic.com/).

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

### Preview a message (default)

```bash
git add <files>
aicommit
```

Prints the generated commit message to stdout. Pipe it into `git commit` if you like it:

```bash
aicommit | git commit -F -
```

### Commit directly

```bash
aicommit --apply
```

Skips the preview and runs `git commit -m "<generated message>"`.

### Specify a scope

```bash
aicommit --scope api
# → feat(api): add streaming endpoint for /events
```

### Use a different Claude model

By default `aicommit` uses **Claude Haiku 4.5** (`claude-haiku-4-5`) — fast, cheap, and accurate enough for commit messages. Override with `--model` or `AICOMMIT_MODEL`:

```bash
aicommit --model claude-sonnet-4-6
# or
export AICOMMIT_MODEL=claude-opus-4-7
aicommit
```

### All options

```text
Usage: aicommit [OPTIONS]

  Read the staged diff, ask Claude for a commit message, print or commit it.

Options:
  -a, --apply              Commit immediately with the generated message.
  -m, --model TEXT         Claude model ID  [env: AICOMMIT_MODEL]
  -s, --scope TEXT         Conventional Commits scope (e.g. 'api', 'cli').
  --max-diff-bytes INT     Truncate the diff to this many bytes  [default: 60000]
  --version                Show version and exit.
  --help                   Show this message and exit.
```

## How it works

1. Runs `git diff --staged --no-color` to get the unified diff.
2. Sends the diff plus a system prompt explaining the Conventional Commits spec to the Claude API.
3. Returns the model's response as the commit message.

The system prompt is sent with `cache_control` set so repeated invocations within a 5-minute window benefit from [prompt caching](https://docs.claude.com/en/docs/build-with-claude/prompt-caching), reducing per-call latency and cost.

## Cost

A typical commit (≈500-line diff) on Claude Haiku 4.5 costs well under one cent per message. Run the command a hundred times a day and you're still in the noise compared to the engineering time you save.

## Development

```bash
git clone https://github.com/harkingbee/aicommit
cd aicommit
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check src tests
```

## License

[MIT](LICENSE)
