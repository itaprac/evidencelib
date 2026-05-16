# Propositions

A proposition is a symbolic event over a frame.

```python
frame = Frame.dsmt(["A", "B", "C"])
A, B, C = frame.symbols()
```

Use `|` for union/disjunction and `&` for intersection/conjunction:

```python
A | B
A & B
(A | B) & C
```

This is idiomatic for Python symbolic DSLs because Python does not allow
overloading `and` and `or`.

## String expressions

String parsing is also supported:

```python
frame.proposition("A | B")
frame.proposition("A & (B | C)")
frame.proposition("A ∩ (B ∪ C)")
```

The parser is intentionally small and does not execute Python code. It supports:

- atom names from the frame,
- `&`, `∩`, `∧` for intersection,
- `|`, `∪`, `∨` for union,
- parentheses,
- `empty` or `∅`.

## Formatting

```python
str(A | B)       # "A|B"
str(A & B)       # "A&B" in free DSmT, "empty" in DST
format(A | B)    # same string formatting behavior as str(...)
```

In hybrid models, formatting respects empty constraints and avoids displaying
forced-empty atoms as if they still carried mass.

