# Examples

Run examples from the repository root:

```bash
source .venv/bin/activate
python examples/basic_dst.py
python examples/rules_dst.py
python examples/dsmt_fusion.py
python examples/hybrid_dsmt.py
python examples/zadeh.py
```

Plotting examples require the optional plotting extra:

```bash
pip install "evidencelib[plot]"
python examples/plotting.py
```

The plotting script can also draw selected figures. For example:

```bash
python examples/plotting.py --figure models --model dst
python examples/plotting.py --figure belief
python examples/plotting.py --figure pignistic
python examples/plotting.py --figure all --save-dir /tmp/evidencelib-plots
```
