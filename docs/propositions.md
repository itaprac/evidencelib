# Propositions

A proposition is a symbolic event over a frame.

```python
frame = Frame.dsmt(["A", "B", "C"])
A, B, C = frame.symbols()
```

## Operators

Use `|` for union and `&` for intersection:

```python
A | B
A & B
(A | B) & C
```

> **Small habit, fewer surprises:** use parentheses in compound expressions,
> especially when mixing `|` and `&`.

## Model-dependent meaning

The frame decides whether intersections are possible.

```python
dst = Frame.dst(["A", "B"])
dsmt = Frame.dsmt(["A", "B"])

dst_a, dst_b = dst.symbols()
dsmt_a, dsmt_b = dsmt.symbols()

str(dst_a & dst_b)   # "empty"
str(dsmt_a & dsmt_b) # "A&B"
```

## String expressions

String parsing is useful for config files, notebooks, and user input:

```python
frame.proposition("A | B")
frame.proposition("A & (B | C)")
frame.proposition("A ∩ (B ∪ C)")
```

Supported syntax:

- atom names from the frame,
- `&`, `∩`, `∧` for intersection,
- `|`, `∪`, `∨` for union,
- parentheses,
- `empty` or `∅`.

The parser uses the same precedence as the object operators: intersection binds
before union.

## Coercion

Most methods accept propositions, strings, or iterables of atom names:

```python
frame.mass({"A": 0.4, "B": 0.2, "A | B": 0.4})
frame.mass({A: 0.4, B: 0.2, A | B: 0.4})
frame.proposition(["A", "B"]) # A|B
```

> **Best default:** use object expressions in library code and string
> expressions when reading from outside the program.

## Display

```python
str(A | B)       # "A|B"
str(A & B)       # "A&B" in free DSmT, "empty" in DST
format(A | B)    # same string formatting behavior as str(...)
```

Hybrid model constraints are reflected in the displayed proposition.
