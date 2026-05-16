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

## Release

Follow `docs/release-checklist.md`.
