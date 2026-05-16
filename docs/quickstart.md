# Quickstart

Install the package:

```bash
pip install evidencelib
```

For local development:

```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,docs]"
python -m pytest -q
```

Create a DST frame and a mass function:

```python
from evidencelib import Frame

frame = Frame.dst(["Alive", "Dead"])
Alive, Dead = frame.symbols()

m = frame.mass({
    Alive: 0.2,
    Dead: 0.5,
    Alive | Dead: 0.3,
})

print(m.belief(Alive))       # 0.2
print(m.plausibility(Alive)) # 0.5
print(m.pignistic())         # {"Alive": 0.35, "Dead": 0.65}
```

Combine two sources:

```python
frame = Frame.dst(["A", "B"])
A, B = frame.symbols()

m1 = frame.mass({A: 0.6, A | B: 0.4})
m2 = frame.mass({B: 0.3, A | B: 0.7})

print(m1.dempster(m2).to_dict())
print(m1.pcr5(m2).to_dict())
```

