import pytest

from evidencelib import Frame, MassFunction, Proposition


def test_frame_rejects_invalid_atom_collections() -> None:
    with pytest.raises(ValueError, match="at least one"):
        Frame.dst([])
    with pytest.raises(ValueError, match="unique"):
        Frame.dst(["A", "A"])
    with pytest.raises(TypeError, match="strings"):
        Frame.dst([1])  # type: ignore[list-item]
    with pytest.raises(ValueError, match="must not be empty"):
        Frame.dst([""])


def test_partial_exclusive_groups_reject_bare_strings() -> None:
    with pytest.raises(TypeError, match="sequences"):
        Frame.hybrid(["A", "B"], exclusive=["A", "B"])


def test_frame_symbol_and_proposition_coercion_validation() -> None:
    frame = Frame.dst(["A", "B", "C"])
    other = Frame.dst(["A", "B", "C"])

    assert frame.symbols("A, C") == (frame.atom("A"), frame.atom("C"))
    assert frame.proposition(["A", "C"]) == frame.atom("A") | frame.atom("C")
    with pytest.raises(KeyError, match="Unknown"):
        frame.atom("D")
    with pytest.raises(ValueError, match="different frame"):
        frame.proposition(other.atom("A"))


def test_elements_limit_applies_before_and_after_cache() -> None:
    uncached = Frame.dst(["A", "B", "C"])
    with pytest.raises(RuntimeError, match="max_count"):
        uncached.elements(max_count=3)

    cached = Frame.dst(["A", "B", "C"])
    assert len(cached.elements()) == 8
    with pytest.raises(RuntimeError, match="max_count"):
        cached.elements(max_count=3)


def test_raw_proposition_regions_require_integer_masks() -> None:
    frame = Frame.dsmt(["A", "B"])

    with pytest.raises(TypeError, match="integer"):
        Proposition(frame, frozenset({"A"}))  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="integer"):
        Proposition(frame, frozenset({True}))
    with pytest.raises(ValueError, match="impossible"):
        Proposition(frame, frozenset({4}))


def test_mass_tolerance_cannot_erase_a_unit_assignment() -> None:
    frame = Frame.dst(["A", "B"])

    with pytest.raises(ValueError, match=r"\[0, 1\)"):
        MassFunction(frame, {"A": 1.0}, tolerance=1.0)


def test_parser_handles_parentheses_unicode_and_errors() -> None:
    frame = Frame.dsmt(["A", "B", "C"])
    a, b, c = frame.symbols()

    assert frame.proposition("A ∩ (B ∪ C)") == a & (b | c)
    assert frame.proposition("∅") == frame.empty
    with pytest.raises(ValueError, match="Could not parse"):
        frame.proposition("A B")
