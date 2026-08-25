from pytest import approx, raises

from evidencelib import Frame, MassFunction


def assert_masses_equal(left, right):
    assert left.keys() == right.keys()
    for key in left:
        assert left[key] == approx(right[key])


def test_mass_from_dict_accepts_plain_and_schema_wrapped_data():
    frame = Frame.dst(["A", "B"])

    plain = MassFunction.from_dict(frame, {"A": 0.2, "A|B": 0.8})
    assert plain.to_dict() == {"A": 0.2, "A|B": 0.8}

    wrapped = {
        "schema": "evidencelib.mass.v1",
        "frame": {
            "atoms": ["A", "B"],
            "model": "dst",
            "region_count": 2,
        },
        "masses": {"A": 0.2, "A|B": 0.8},
    }
    restored = MassFunction.from_dict(frame, wrapped)

    assert_masses_equal(restored.to_dict(), plain.to_dict())
    with raises(ValueError):
        MassFunction.from_dict(Frame.dsmt(["A", "B"]), wrapped)


def test_mass_json_round_trip_validates_schema_and_frame_metadata():
    frame = Frame.dst(["A", "B"])
    mass = frame.mass({"A": 0.2, "B": 0.3, "A|B": 0.5})

    text = mass.to_json(indent=None)
    restored = MassFunction.from_json(frame, text)

    assert_masses_equal(restored.to_dict(), mass.to_dict())
    with raises(ValueError):
        MassFunction.from_json(frame, '{"schema": "unknown", "masses": {}}')
    with raises(ValueError):
        MassFunction.from_json(Frame.dst(["B", "A"]), text)


def test_mass_csv_round_trip_with_and_without_header():
    frame = Frame.dst(["A", "B"])
    mass = frame.mass({"A": 0.2, "B": 0.3, "A|B": 0.5})

    csv_text = mass.to_csv()
    restored = MassFunction.from_csv(frame, csv_text)
    no_header = MassFunction.from_csv(
        frame,
        mass.to_csv(include_header=False),
        has_header=False,
    )

    assert "A,0.2\n" in csv_text
    assert_masses_equal(restored.to_dict(), mass.to_dict())
    assert_masses_equal(no_header.to_dict(), mass.to_dict())

    with raises(ValueError):
        MassFunction.from_csv(frame, "bad,mass\nA,1")
    with raises(ValueError):
        MassFunction.from_csv(frame, "proposition,mass\nA,not-a-number\n")


def test_mass_latex_export_formats_publication_table():
    frame = Frame.dst(["H_1", "H_2"])
    mass = frame.mass({"H_1": 0.2, "H_2": 0.3, "H_1|H_2": 0.5})

    latex = mass.to_latex(
        columns=("mass", "belief", "pl", "q"),
        caption="Mass & belief_1",
        label="tab:mass",
    )

    assert r"\begin{table}[htbp]" in latex
    assert r"\caption{Mass \& belief\_1}" in latex
    assert r"\label{tab:mass}" in latex
    assert r"\toprule" in latex
    assert "Mass & Belief & Plausibility & Commonality" in latex
    assert r"$H\_1 \cup H\_2$" in latex
    assert "0.2000" in latex

    all_rows = mass.to_latex(rows="all", booktabs=False)
    assert r"$\emptyset$" in all_rows
    assert r"\hline" in all_rows


def test_mass_latex_export_validates_options():
    frame = Frame.dst(["A", "B"])
    mass = frame.mass({"A": 0.5, "B": 0.5})

    with raises(ValueError):
        mass.to_latex(columns=("unknown",))
    with raises(ValueError):
        mass.to_latex(rows="stored")


def test_mass_comparison_latex_export_supports_wide_and_long_layouts():
    frame = Frame.dst(["A", "B"])
    first = frame.mass({"A": 0.6, "A|B": 0.4})
    second = frame.mass({"B": 0.3, "A|B": 0.7})

    wide = first.comparison_to_latex(
        second,
        labels=("camera", "expert"),
        propositions=("A", "B", "A|B"),
        caption="Source masses",
        label="tab:sources",
        float_format=".2f",
        source_header="Sensor",
    )

    assert r"\begin{table}[htbp]" in wide
    assert r"Sensor & $A$ & $B$ & $A \cup B$" in wide
    assert r"camera & 0.60 & 0.00 & 0.40" in wide
    assert r"\caption{Source masses}" in wide

    long = first.comparison_to_latex(
        second,
        labels=("camera", "expert"),
        orientation="long",
        float_format=".2f",
        font_size="small",
        arraystretch=1.1,
    )

    assert r"\small" in long
    assert r"\renewcommand{\arraystretch}{1.1}" in long
    assert "Source & Proposition & Mass" in long
    assert r"camera & $A$ & 0.60" in long
    assert r"\addlinespace" in long


def test_mass_comparison_latex_export_validates_options():
    frame = Frame.dst(["A", "B"])
    first = frame.mass({"A": 0.6, "A|B": 0.4})
    second = frame.mass({"B": 0.3, "A|B": 0.7})

    with raises(ValueError, match="orientation"):
        first.comparison_to_latex(second, orientation="diagonal")
    with raises(ValueError, match="labels"):
        first.comparison_to_latex(second, labels=("only one",))
    with raises(ValueError, match="font_size"):
        first.comparison_to_latex(second, font_size="tiny")
    with raises(ValueError, match="arraystretch"):
        first.comparison_to_latex(second, arraystretch=0)
    with raises(ValueError, match="same frame"):
        first.comparison_to_latex(Frame.dst(["A", "B"]).mass({"A": 1.0}))


def test_pignistic_comparison_latex_export_formats_decision_results():
    frame = Frame.dst(["A", "B"])
    first = frame.mass({"A": 0.75, "A|B": 0.25})
    second = frame.mass({"B": 0.6, "A|B": 0.4})

    latex = first.pignistic_comparison_to_latex(
        second,
        labels=("first", "second"),
        actions=("Accept", "Check & repair"),
        caption="Decision comparison",
        label="tab:decisions",
        float_format=".3f",
        source_header="Rule",
    )

    assert r"Rule & $m(\emptyset)$ & $\mathrm{BetP}(A)$ & $\mathrm{BetP}(B)$" in latex
    assert r"first & 0.000 & 0.875 & 0.125 & Accept" in latex
    assert r"second & 0.000 & 0.200 & 0.800 & Check \& repair" in latex
    assert r"\label{tab:decisions}" in latex

    with raises(ValueError, match="actions"):
        first.pignistic_comparison_to_latex(second, actions=("one",))
    with raises(ValueError, match="Unknown frame hypothesis"):
        first.pignistic_comparison_to_latex(second, hypotheses=("C",))
