# Literature-backed Checks

`pybelief` includes regression tests whose expected values come from standard
DST/DSmT examples.

## Alive/dead DST example

The basic DST example assigns:

```python
m(Alive) = 0.2
m(Dead) = 0.5
m(Alive | Dead) = 0.3
```

The tests check:

```python
Bel(Alive) = 0.2
Pl(Alive) = 0.5
Bel(Dead) = 0.5
Pl(Dead) = 0.8
```

## DSmC and DSmH

The DSmT introduction example over `t1`, `t2`, `t3` checks the free DSm model
DSmC values:

```text
t1                 0.21
t2                 0.11
t3                 0.06
t1 | t2            0.03
t1 & t2            0.21
t1 & t3            0.13
t2 & t3            0.14
t3 & (t1 | t2)     0.11
```

It also checks the hybrid result when `t3` is found empty:

```text
t1       0.34
t2       0.25
t1 | t2  0.41
```

## PCR5

The PCR5 examples check the two-hypothesis examples from the DSmT introduction,
including:

```text
PCR5(A)     = 0.54
PCR5(B)     = 0.18
PCR5(A | B) = 0.28
```

## Zadeh's example

The high-conflict medical diagnosis example checks:

```text
Dempster(T) = 1.0
Yager(M | C | T) = 0.99
DSmH(M | C) = 0.81
DSmH(M | T) = 0.09
DSmH(C | T) = 0.09
DSmH(T) = 0.01
PCR5(M) = 0.486
PCR5(C) = 0.486
PCR5(T) = 0.028
```

Run the regression suite with:

```bash
python -m pytest -q
```

