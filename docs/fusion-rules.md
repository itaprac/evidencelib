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
| `disjunctive()` | At least one source is reliable, but you do not know which. | Creates no new conflict: masses combine by union. |
| `dempster()` | Classical DST normalization is acceptable. | Removes `empty` conflict and renormalizes. |
| `yager()` | Conflict should become uncertainty. | Moves conflict to total ignorance. |
| `dsmc()` | Free DSm model only. | Keeps mass on intersections; no conflict exists. |
| `dsmh()` | Static or dynamic hybrid constraints matter. | Applies the complete `S1 + S2 + S3` transfer. |
| `dubois_prade()` | Conflicts should become the union of the hypotheses involved. | Transfers each conflict to the union of its focal elements. |
| `pcr1()` ... `pcr4()` | Comparing the historical PCR family. | Redistribute total or partial conflict by column sums or conjunctive masses. |
| `pcr5()` / `pcr6()` | High conflict should stay local. | Redistributes conflict to involved propositions. |
| `pcr5_plus()` / `pcr6_plus()` | More than two sources, some of them (nearly) vacuous. | Redistributes conflict only to propositions that effectively take part in it. |

## Conjunctive / DSmC / Smets

```python
m1.conjunctive(m2)
m1.dsmc(m2)
m1.smets(m2)
```

The unnormalized conjunctive rule intersects propositions and multiplies their
masses. On a DST frame, conflicting intersections accumulate on `empty`.

`smets()` is the same unnormalized rule (Smets' TBM conjunctive rule).
`dsmc()` is the classic DSm rule, defined only on the free DSm model, where no
intersection is empty; on Shafer's or a hybrid model it raises `ValueError`
(use `conjunctive()`/`smets()` or `dsmh()` there).

Fusion results are returned exactly as computed: products are never dropped
for being small, and results are never rescaled. Rules that assume normal
sources (Yager, Dubois-Prade, DSmH, DSmC, PCR5, PCR6, PCR5+, PCR6+) reject a
source with any positive mass on `empty`, however small. PCR1-PCR4 accept such
sources, as in their original definition.

> **Use when:** you want to inspect conflict explicitly before deciding how to
> handle it.

## Disjunctive

```python
m1.disjunctive(m2, m3)
```

The TBM disjunctive rule sends each product of masses to the union of the
focal elements: `m(A) = sum over A_1 | ... | A_s = A of prod m_i(A_i)` (Dubois
and Prade, 1986; Smets, 1993). It creates no new conflict: the result has mass
on `empty` only if every source has some. The rule is associative and assumes
only that at least one source is reliable. Sources may carry mass on `empty`,
which is the neutral element of the rule.

> **Use when:** you cannot rely on every source, only on at least one.

## Dempster

```python
m1.dempster(m2)
```

Dempster's rule removes empty-set conflict and normalizes the remaining masses.
It is defined for any conflict `K < 1`, however close to one; only total
conflict (no non-empty product) raises `TotalConflictError`.

> **Use when:** the frame is exclusive and normalized conflict handling matches
> your application.

## Yager

```python
m1.yager(m2)
```

Yager's rule transfers total conflict to total ignorance. This keeps the result
normalized while representing conflict as uncertainty instead of assigning it to
specific hypotheses. Like the original rule, it combines normal sources: a
source with `m(empty) > 0`, such as a raw `smets()` result, is rejected.

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
`smets()`, `dempster()`, `yager()`, and `dubois_prade()`.

## Dubois-Prade

```python
m1.dubois_prade(m2, m3)
m1.dubois_prade(m2, model=target)   # constraints learned later
```

Dubois-Prade sends each non-conflicting product to its intersection and each
conflicting product to the union of the focal elements involved. It accepts
two or more sources. In static Shafer-style problems it coincides with the
corresponding DSmH transfer.

With a target `model=...`, propositions are projected onto the constrained
model first. A product whose union also becomes empty is lost, as in the
original rule, so the result can sum to less than one. This is the known
limitation of Dubois-Prade in dynamic fusion (Dezert and Smarandache, *An
introduction to DSmT*, Sec. 2.6.3: the result sums to 0.94); `dsmh()` keeps
that mass through its `S2` term.

Such an incomplete assignment is returned as computed, and the lost mass is
recorded (also in `to_json()`), so even a loss of `1e-12` is detected. Fusion
rules, the uncertainty measures, and everything built on the pignistic
transformation (`pignistic*()`, `decision()`, `pignistic_comparison_to_latex()`,
`plot_venn()`, `plot_pignistic_decision()`, and `plot_belief_plausibility()`
with its default pignistic markers) are defined for basic belief assignments and
raise `InvalidMassError`. Direct readings still work: `mass()`, `belief()`,
`plausibility()`, `commonality()`, `to_dict()`, `to_json()`, `to_csv()`,
`to_latex()`, `comparison_to_latex()`, `plot()`, and `plot_comparison()`. Call
`normalize()` only if rescaling the remaining masses is what you intend.

```python
source = Frame.dsmt(["t1", "t2", "t3"])
t1, t2, t3 = source.symbols()
m1 = source.mass({t1: 0.1, t2: 0.4, t3: 0.2, t1 | t2: 0.3})
m2 = source.mass({t1: 0.5, t2: 0.1, t3: 0.3, t1 | t2: 0.1})
target = Frame.hybrid(["t1", "t2", "t3"], exclusive=True, empty=["t3"])

m1.dubois_prade(m2, model=target).to_dict()
# {'t1': 0.34, 't1|t2': 0.35, 't2': 0.25}, total 0.94
m1.dsmh(m2, model=target).to_dict()
# {'t1': 0.34, 't1|t2': 0.41, 't2': 0.25}
```

> **Use when:** conflict between hypotheses should become uncertainty about
> exactly those hypotheses.

## PCR1 to PCR4

```python
m1.pcr1(m2, m3)
m1.pcr2(m2, m3)
m1.pcr3(m2, m3)
m1.pcr4(m2, m3)
m1.pcr3(m2, model=target)   # constraints learned later
```

The first four proportional conflict redistribution rules (Smarandache and
Dezert, 2004/2006) are kept for comparison studies; their authors recommend
PCR5/PCR6. All accept two or more sources:

| Rule | Conflict redistributed | To | In proportion to |
| --- | --- | --- | --- |
| PCR1 | total | every non-empty focal proposition | column sums `c(X) = sum_i m_i(X)` |
| PCR2 | total | propositions involved in some conflict | column sums |
| PCR3 | each partial conflict | propositions in its canonical form | column sums |
| PCR4 | each partial conflict | propositions in its canonical form | conjunctive masses `m_12...s(X)`; column sums if one of them is zero |

The canonical form of a conflict keeps its minimal focal elements: in
`A & B & (A|B)`, `A|B` is absorbed, so only `A` and `B` receive mass. PCR2,
PCR3, and PCR4 are therefore neutral to the vacuous source; PCR1 is not.
Composite DSm propositions are not split into conjunctive-normal-form clauses:
the rules redistribute to focal elements, weighted by their column sums.

The rules also cover dynamic fusion and unnormalized sources, as in the
original paper. With `model=target`, the canonical form of each conflict is
taken on the source propositions (an empty source proposition absorbs
nothing), projected onto the constrained model, and reduced again there; in
PCR2-PCR4 total ignorance never receives a proportional share of a conflict,
and propositions that become empty receive nothing. This keeps PCR2-PCR4 neutral to the vacuous source
under a model change. A conflict with no non-empty
proposition left goes, as specified for each rule, to the disjunctive form
`u(X_1) | ... | u(X_k)` (PCR1, PCR2, PCR3) or to the partial ignorance
`X_1 | ... | X_k` (PCR4); PCR3 and PCR4 then fall back to total ignorance.
If no non-empty proposition can receive it at all, the problem is void and,
as in the original rules, the conflict stays on `empty`. Sources may carry
mass on `empty` (for example TBM results); that mass enters the conflict.

## PCR5 and PCR6

```python
m1.pcr5(m2, m3)
m1.pcr6(m2, m3)
```

PCR rules redistribute partial conflict only to the propositions involved in
that conflict, proportionally to the masses that created it.

`pcr5()` and `pcr6()` support two or more sources and combine them jointly;
`pcr5()` implements the general formula of Smarandache and Dezert (2004,
eq. 33), in the equivalent form of Dezert, Dezert and Smarandache (2021,
eq. 14): every distinct focal element of a conflicting product receives a
share. Some worked examples of the 2004 paper (Secs. 11.4-11.5) instead
redistribute only to the canonical form of the conflict (as PCR3 and PCR4 do)
and report that a vacuous source is neutral. For more than two sources those
examples do not follow the paper's own general formula: with the general
formula, a vacuous source is not neutral, which is the weakness that PCR5+ and
PCR6+ address.
PCR rules are not associative, so `m1.pcr6(m2, m3)` generally differs from
`m1.pcr6(m2).pcr6(m3)`. The two rules differ only when the same proposition
appears in several sources of a conflicting product: PCR5 weights it by the
*product* of its masses, PCR6 by their *sum*. For two sources they coincide;
each rule nevertheless has its own implementation, so the coincidence can be
checked. Both require source assignments with `m(empty) = 0`; combine or normalize raw
TBM conflict before selecting a PCR rule.

> **Use when:** assigning conflict to total ignorance would be too coarse.

## PCR5+ and PCR6+

```python
m1.pcr6_plus(m2, m3)
m1.pcr5_plus(m2, m3)
```

With more than two sources, PCR5 and PCR6 can give part of a conflict to a
proposition that is not itself in conflict. In the product
`m1(A) m2(B) m3(A|B)`, the proposition `A|B` contains both `A` and `B`, yet
PCR5 and PCR6 still give it a share. As a result, the vacuous assignment
`m(Theta) = 1` is not neutral: adding it as an extra source changes the
result and inflates the mass of uncertain propositions.

PCR5+ and PCR6+ (Dezert, Dezert and Smarandache, 2021) compute a binary
keeping index for each proposition in a conflicting product. A proposition
that contains every other proposition of no greater cardinality in that
product, without a kept larger proposition above it, is discarded from the
redistribution. The remaining propositions share the conflict exactly as in
PCR5 or PCR6. Consequences:

- the vacuous assignment is a neutral element:
  `m1.pcr6_plus(m2, vacuous).to_dict()` equals `m1.pcr6_plus(m2).to_dict()`
  up to floating-point rounding;
- `Theta` never receives a share of a conflict, and a proposition receives no
  share of a conflict in which its keeping index is zero;
- nearly vacuous sources still change the result, but only through their
  informative focal elements, so their effect stays small (Example 5: one
  source with `m(Theta) = 0.99` leaves `m(Theta)` at 0 instead of 0.381 under
  PCR6);
- for two sources, PCR5+ = PCR5 = PCR6 = PCR6+.

```python
frame = Frame.dst(["A", "B"])
A, B = frame.symbols()
m1 = frame.mass({A: 0.6, B: 0.1, A | B: 0.3})
m2 = frame.mass({A: 0.5, B: 0.3, A | B: 0.2})
m3 = frame.mass({A: 0.4, B: 0.1, A | B: 0.5})
vacuous = frame.mass({A | B: 1.0})

m1.pcr6(m2, m3)[A | B]                # 0.094259
m1.pcr6(m2, m3, vacuous)[A | B]       # 0.224545, the vacuous source matters
m1.pcr6_plus(m2, m3)[A | B]           # 0.03
m1.pcr6_plus(m2, m3, vacuous)[A | B]  # 0.03, the vacuous source is neutral
```

The keeping index depends only on which propositions occur in a product, not
on their masses, so it is cached across fusions. On DSm frames the
cardinality used by the index is the DSm cardinality.

> **Use when:** fusing three or more sources, especially when some sources are
> vague or close to total ignorance.

## Explaining a PCR fusion

```python
for transfer in m1.conflict_redistribution(m2, m3, rule="pcr6+"):
    print(transfer.focal, transfer.conflict, transfer.shares)
```

`conflict_redistribution()` returns one `ConflictTransfer` per conflicting
product, with the focal element taken from each source, the conflicting mass,
the propositions kept by the rule, and the share each of them receives.
`rule` is `"pcr5"`, `"pcr6"`, `"pcr5+"`, or `"pcr6+"`. Adding the shares to
the non-empty conjunctive masses reproduces the fusion result, which makes the
trace useful for checking hand calculations and for teaching.
