"""Small parser for proposition expressions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from evidencelib.proposition import Proposition

if TYPE_CHECKING:
    from evidencelib.frame import Frame


@dataclass(frozen=True)
class _Token:
    kind: str
    value: str


class PropositionParser:
    """Parse proposition expressions without executing Python code.

    The parser accepts atom names from the frame, parentheses, ``&``/``∩``/``∧``
    for intersection, and ``|``/``∪``/``∨`` for union.
    """

    def __init__(self, frame: "Frame") -> None:
        self.frame = frame

    def parse(self, expression: str) -> Proposition:
        """Parse an expression into a proposition owned by the parser's frame."""

        self._tokens = self._tokenize(expression)
        self._position = 0
        result = self._parse_union()
        if self._peek().kind != "end":
            raise ValueError(f"Unexpected token {self._peek().value!r}.")
        return result

    def _parse_union(self) -> Proposition:
        result = self._parse_intersection()
        while self._accept("|"):
            result = result | self._parse_intersection()
        return result

    def _parse_intersection(self) -> Proposition:
        result = self._parse_primary()
        while self._accept("&"):
            result = result & self._parse_primary()
        return result

    def _parse_primary(self) -> Proposition:
        token = self._peek()
        if self._accept("("):
            result = self._parse_union()
            self._expect(")")
            return result
        if token.kind == "atom":
            self._position += 1
            if token.value in {"empty", "EMPTY"}:
                return Proposition(self.frame, frozenset())
            return self.frame.atom(token.value)
        raise ValueError(f"Expected proposition, got {token.value!r}.")

    def _accept(self, kind: str) -> bool:
        if self._peek().kind == kind:
            self._position += 1
            return True
        return False

    def _expect(self, kind: str) -> None:
        if not self._accept(kind):
            raise ValueError(f"Expected {kind!r}, got {self._peek().value!r}.")

    def _peek(self) -> _Token:
        return self._tokens[self._position]

    def _tokenize(self, expression: str) -> list[_Token]:
        tokens: list[_Token] = []
        i = 0
        while i < len(expression):
            char = expression[i]
            if char.isspace():
                i += 1
                continue
            if char in "()":
                tokens.append(_Token(char, char))
                i += 1
                continue
            if char in {"&", "∩", "∧"}:
                tokens.append(_Token("&", char))
                i += 1
                continue
            if char in {"|", "∪", "∨"}:
                tokens.append(_Token("|", char))
                i += 1
                continue
            if char == "∅":
                tokens.append(_Token("atom", "empty"))
                i += 1
                continue

            start = i
            while i < len(expression):
                current = expression[i]
                if current.isspace() or current in "()&|∩∧∪∨":
                    break
                i += 1
            value = expression[start:i]
            if value not in self.frame.atoms and value not in {"empty", "EMPTY"}:
                raise ValueError(f"Unknown proposition atom {value!r}.")
            tokens.append(_Token("atom", value))
        tokens.append(_Token("end", "end of expression"))
        return tokens
