# Contributing

## Development setup

```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,docs]"
```

## Checks

```bash
python -m pytest -q
python -m sphinx -W -b html docs docs/_build/html
python -m build
```

## Documentation

The documentation is built with Sphinx and MyST Markdown. Read the Docs uses
`.readthedocs.yaml` in the repository root.

Add user-facing conceptual documentation under `docs/*.md` and generated API
documentation under `docs/api-reference.rst`.

## Release

Follow `docs/release-checklist.md`.

