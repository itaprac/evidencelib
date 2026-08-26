# Common errors

This page lists common validation failures, their exact messages, and the
corresponding fixes. The package-specific exception hierarchy is defined in
`evidencelib.exceptions`.

## Catching package-specific errors

`EvidenceLibError` is the base class for exceptions defined by the package. It
is not raised directly. Catch it when one handler should cover both invalid
mass assignments and undefined total-conflict normalization.

```python
from evidencelib import Frame
from evidencelib.exceptions import EvidenceLibError

frame = Frame.dst(["A", "B"])

try:
    frame.mass({"A": 0.5, "B": 0.25})
except EvidenceLibError as error:
    print(error)
```

Errors caused by incompatible frames, proposition syntax, or invalid argument
shapes are standard `ValueError` or `TypeError` exceptions.

## InvalidMassError: masses do not sum to one

```python
from evidencelib import Frame

frame = Frame.dst(["A", "B"])
mass = frame.mass({"A": 0.5, "B": 0.25})
```

Message:

```text
Mass values must sum to 1.0, got 0.75.
```

Fix the source values so they sum to one. Assign any unresolved support to the
total frame rather than silently renormalizing elicited data.

```python
mass = frame.mass({"A": 0.5, "B": 0.25, "A|B": 0.25})
```

`InvalidMassError` is also raised for negative, infinite, or `NaN` masses.

## TotalConflictError: Dempster normalization is undefined

```python
from evidencelib import Frame

frame = Frame.dst(["A", "B"])
A, B = frame.symbols()

first = frame.mass({A: 1.0})
second = frame.mass({B: 1.0})
first.dempster(second)
```

Message:

```text
Dempster normalization is undefined at total conflict.
```

Dempster's rule cannot divide by the remaining non-conflicting mass when that
mass is zero. Inspect the conflict with `first.smets(second)`, or select a rule
whose conflict treatment matches the application, such as `yager()`,
`dubois_prade()`, or `pcr5()`.

## Proposition outside the frame

```python
frame = Frame.dst(["A", "B"])
frame.mass({"C": 1.0})
```

Message:

```text
Could not parse proposition 'C'
```

Use only atom names declared in the frame. If `C` is a real hypothesis, create
a new frame containing it and reconstruct all source mass functions on that
frame.

## Invalid exclusive constraint

```python
Frame.hybrid(["A", "B"], exclusive=["A", "B"])
```

Message:

```text
exclusive groups must be sequences of atom names, not strings.
```

Each group must itself be a sequence. Use a tuple inside the outer list:

```python
Frame.hybrid(["A", "B"], exclusive=[("A", "B")])
```

The equivalent symbolic form is
`Frame.hybrid(["A", "B"], empty=["A&B"])`.

## Mass already assigned to the empty proposition

```python
frame = Frame.dst(["A", "B"])
A, B = frame.symbols()

conflicted = frame.mass({frame.empty: 0.1, A: 0.9})
other = frame.mass({A | B: 1.0})
conflicted.dsmh(other)
```

Message:

```text
DSmH cannot recover the origin of mass already collapsed onto empty. Create sources on their original frame and pass the constrained target explicitly with dsmh(..., model=target_frame).
```

DSmH must know which focal propositions produced a forbidden intersection.
Keep the original source assignments and pass a constrained target model to
`dsmh()` instead of using a source in which that provenance has already been
collapsed onto `empty`.

## Mixing different frame instances

```python
left = Frame.dst(["A", "B"])
right = Frame.dst(["A", "B"])

left.mass({"A": 1.0}).dempster(right.mass({"A": 1.0}))
```

Message:

```text
All mass functions must belong to the same frame.
```

Matching atom names are not sufficient. Reuse one `Frame` instance for every
source that will be fused.

## A target model relaxes source constraints

```python
source = Frame.dst(["A", "B"])
target = Frame.dsmt(["A", "B"])

first = source.mass({"A": 1.0})
second = source.mass({"A|B": 1.0})
first.dsmh(second, model=target)
```

Message:

```text
The DSmH target model may add constraints but cannot make regions possible that were absent from the source frame.
```

A target model may remove possible regions, but it cannot reconstruct overlap
that the source frame never represented. Build the sources on a free DSm frame
before applying a more constrained hybrid target.
