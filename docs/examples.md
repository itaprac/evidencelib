# Examples

Run examples from the repository root after installing the package in editable
mode:

```bash
source .venv/bin/activate
python examples/basic_dst.py
python examples/rules_dst.py
python examples/dsmt_fusion.py
python examples/hybrid_dsmt.py
python examples/zadeh.py
```

## Literature Tests

The strongest regression checks are in `tests/`.

- `tests/test_dst.py` checks the alive/dead DST example, PCR5 examples, Zadeh's
  example, parser behavior, and total conflict.
- `tests/test_dsmt.py` checks DSmC, DSmH, hyper-power set cardinalities, and
  generalized pignistic behavior.

Run:

```bash
python -m pytest -q
```

