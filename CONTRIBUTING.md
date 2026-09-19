# Contributing

Real commands for this repository. `.github/workflows/ci.yml` is the source of
truth if this page and CI ever disagree.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/macOS
pip install -r requirements.txt
```

The base install only needs `PyYAML`. The provider packages in
`requirements.txt` (`anthropic`, `openai`, `pypdf`) are commented out —
install only the one you are actually touching, e.g. `pip install pypdf`.
Tests do not need any of them: `--selftest` and the `demo` provider run with
no API key and no network.

## Before you write code

Adding a fifth provider (alongside `anthropic`, `openai`, `ollama`, `demo`)
is welcome. Changing what the `demo` provider promises — rule-based,
no API key, no network — is not; open an issue first if you think that
should change.

## The one rule that is not negotiable

A new check starts as a failing test. Add a `check("label", condition)` call
inside `selftest()` in `extract.py` — it already covers prompt building, JSON
parsing, type coercion, and the `demo` provider, all offline. Confirm your
new check fails first, then implement.

## Running the tests

```bash
python -m compileall -q .
python extract.py --selftest
```

Same two steps CI runs, in that order.

## Commit messages

Match `git log --oneline` in this repository: a short, imperative summary, no
ticket prefixes, no emoji. Recent examples:

```
Add --selftest, and run it in CI
llm-doc-extractor: schema-driven document -> JSON via Anthropic/OpenAI/Ollama, with no-key demo mode
```

## License

Contributions are published under this repository's MIT license.
