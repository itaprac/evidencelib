# Fusion Rules

Fusion combines mass functions from the same frame.

```python
combined = m1.dempster(m2)
```

All sources must belong to the same original `Frame` instance. Every rule
returns a new `MassFunction`; input sources are not modified. Fusion rules assume
that sources are independent in the sense required by the selected theory.

When constraints are learned after source elicitation, pass a separate target
frame with `model=...`. The result belongs to that target frame.

## Choose a rule

| Rule | Best when | Conflict behavior |
| --- | --- | --- |
| `conjunctive()` / `smets()` | You want to inspect raw conflict. | Keeps conflict on `empty`. |
| `dempster()` | Classical DST normalization is acceptable. | Removes `empty` conflict and renormalizes. |
| `yager()` | Conflict should become uncertainty. | Moves conflict to total ignorance. |
| `dsmc()` | Free DSmT intersections are meaningful. | Keeps mass on intersections. |
| `dsmh()` | Static or dynamic hybrid constraints matter. | Applies the complete `S1 + S2 + S3` transfer. |
| `dubois_prade()` | Two-source, static conflict transfer is appropriate. | Transfers static conflicts to unions. |
| `pcr5()` / `pcr6()` | High conflict should stay local. | Redistributes conflict to involved propositions. |

## Conjunctive / DSmC / Smets

```python
m1.conjunctive(m2)
m1.dsmc(m2)
m1.smets(m2)
```

The unnormalized conjunctive rule intersects propositions and multiplies their
masses. On a free DSmT frame this is the classic DSm rule, DSmC. On a DST frame,
conflicting intersections accumulate on `empty`.

`smets()` is an alias for the same unnormalized behavior.

> **Use when:** you want to inspect conflict explicitly before deciding how to
> handle it.

## Dempster

```python
m1.dempster(m2)
```

Dempster's rule removes empty-set conflict and normalizes the remaining masses.
If conflict is total, `TotalConflictError` is raised.

> **Use when:** the frame is exclusive and normalized conflict handling matches
> your application.

## Yager

```python
m1.yager(m2)
```

Yager's rule transfers total conflict to total ignorance. This keeps the result
normalized while representing conflict as uncertainty instead of assigning it to
specific hypotheses.

> **Use when:** disagreement between sources should make the result less
> specific.

## Hybrid DSm rule (DSmH)

```python
m1.dsmh(m2)                 # static model
m1.dsmh(m2, model=target)   # constraints learned later
```

`dsmh()` implements all three terms of the hybrid rule:

- `S1` keeps products whose intersection remains non-empty;
- `S2` handles focal elements that all became empty, using their original
  atom-unions `u(X)` and falling back to total ignorance only when required;
- `S3` transfers other relatively empty intersections to their canonical
  disjunction.

For a dynamic change, source assignments must be created on the original frame.
Do not recreate them on the constrained frame: doing so collapses distinct
relative-empty propositions onto `empty` before the rule can inspect them.

```python
source = Frame.dst(["t1", "t2", "t3"])
t1, t2, t3 = source.symbols()
m1 = source.mass({t1: 0.1, t2: 0.4, t3: 0.2, t1 | t2: 0.3})
m2 = source.mass({t1: 0.5, t2: 0.1, t3: 0.3, t1 | t2: 0.1})

target = Frame.hybrid(["t1", "t2", "t3"], exclusive=True, empty=["t3"])
result = m1.dsmh(m2, model=target)
# {'t1': 0.34, 't1|t2': 0.41, 't2': 0.25}
```

The same explicit target-model mechanism is available on `conjunctive()`,
`smets()`, `dempster()`, and `yager()`.

## Dubois-Prade

```python
m1.dubois_prade(m2)
```

Dubois-Prade is implemented as a static, exactly-two-source rule. In static
Shafer-style problems it coincides with the corresponding DSmH transfer. It is
not DSmH in a dynamic problem: the literature example where a hypothesis later
becomes empty loses mass under Dubois-Prade. Passing a distinct `model=...`
therefore raises `ValueError` instead of returning a mislabeled DSmH result.

> **Use when:** you model constraints with `Frame.hybrid(...)`.

## PCR5 and PCR6

```python
m1.pcr5(m2)
m1.pcr6(m2, m3)
```

PCR rules redistribute partial conflict only to the propositions involved in
that conflict, proportionally to the masses that created it.

`pcr5()` accepts two sources. `pcr6()` supports two or more sources.
Both require source assignments with `m(empty) = 0`; combine or normalize raw
TBM conflict before selecting a PCR rule.

> **Use when:** assigning conflict to total ignorance would be too coarse.
