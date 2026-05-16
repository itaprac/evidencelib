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

Parentheses are recommended in compound expressions.

## String expressions

String parsing is also supported:

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

## Representation

```python
str(A | B)       # "A|B"
str(A & B)       # "A&B" in free DSmT, "empty" in DST
format(A | B)    # same string formatting behavior as str(...)
```

Hybrid model constraints are reflected in the displayed proposition.
