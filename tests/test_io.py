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
