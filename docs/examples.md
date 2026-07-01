# Examples

The repository includes complete scripts you can run from a project clone with
`evidencelib` installed in your environment.

## Basic workflow

```bash
python examples/basic_dst.py
python examples/rules_dst.py
```

Start here if you want to see frames, masses, belief measures, and fusion rules
without extra theory.

## DSmT and conflict

```bash
python examples/dsmt_fusion.py
python examples/hybrid_dsmt.py
python examples/zadeh.py
```

These examples show overlapping hypotheses, hybrid constraints, and high
conflict behavior.

> **Good reading order:** `basic_dst.py`, `rules_dst.py`, `zadeh.py`,
> `dsmt_fusion.py`, then `hybrid_dsmt.py`.

## Plotting

Plotting examples require the optional plotting extra:

```bash
pip install "evidencelib[plot]"
python examples/plotting.py
```

Draw only selected figures:

```bash
python examples/plotting.py --figure models --model dst
python examples/plotting.py --figure belief
python examples/plotting.py --figure pignistic
python examples/plotting.py --figure all --save-dir /tmp/evidencelib-plots
```
