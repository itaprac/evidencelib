"""Conformance tests for the SoftwareX article and reviewer analyses.

Numbers quoted in the manuscript or its reproducible reviewer analyses are
pinned here, so any library change that would silently invalidate the paper or
response letter fails CI.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from pytest import approx

from evidencelib import Frame


def _weld_sources(frame):
    acceptance, repair, rejection = frame.symbols()
    visual = frame.mass(
        {
            acceptance: 0.70,
            acceptance | repair: 0.15,
            acceptance | repair | rejection: 0.15,
        }
    )
    ultrasonic = frame.mass(
        {
            repair: 0.65,
            acceptance | repair: 0.20,
            acceptance | repair | rejection: 0.15,
        }
    )
    return visual, ultrasonic


def test_weld_rule_values_from_section_3_1() -> None:
    """Pin every numerical row of the article's weld decision table."""

    frame = Frame.dst(["A", "R", "J"])
    visual, ultrasonic = _weld_sources(frame)
    results = {
        "Smets/TBM": visual.smets(ultrasonic),
        "Dempster": visual.dempster(ultrasonic),
        "Yager": visual.yager(ultrasonic),
        "Dubois--Prade": visual.dubois_prade(ultrasonic),
        "PCR5": visual.pcr5(ultrasonic),
    }
    expected = {
        "Smets/TBM": (
            0.455,
            0.5389908256880733,
            0.4472477064220183,
            0.013761467889908256,
        ),
        "Dempster": (
            0.0,
            0.5389908256880734,
            0.4472477064220184,
            0.013761467889908258,
        ),
        "Yager": (
            0.0,
            0.4454166666666667,
            0.39541666666666664,
            0.15916666666666665,
        ),
        "Dubois--Prade": (0.0, 0.5212499999999999, 0.47125, 0.0075),
        "PCR5": (0.0, 0.5296759259259258, 0.4628240740740741, 0.0075),
    }

    for label, result in results.items():
        conflict, betp_a, betp_r, betp_j = expected[label]
        scores = result.pignistic()
        assert result.conflict == approx(conflict)
        assert scores["A"] == approx(betp_a)
        assert scores["R"] == approx(betp_r)
        assert scores["J"] == approx(betp_j)


def test_reproduction_scripts_write_section_3_artifacts(tmp_path: Path) -> None:
    """Run all article examples and verify their declared artifacts."""

    root = Path(__file__).resolve().parents[1]
    scripts_and_outputs = {
        "example_1_weld_dst.py": (
            "weld_input_masses.tex",
            "weld_decisions.tex",
            "weld_input_masses.pdf",
            "weld_rule_comparison.pdf",
        ),
        "example_2_pump_dsmt.py": (
            "pump_input_masses.tex",
            "pump_fused_masses.pdf",
            "pump_venn_regions.pdf",
        ),
        "example_3_pump_hybrid.py": (
            "pump_hybrid_masses.tex",
            "pump_hybrid_venn_regions.pdf",
        ),
    }

    for script_name, output_names in scripts_and_outputs.items():
        output_dir = tmp_path / script_name.removesuffix(".py")
        subprocess.run(
            [
                sys.executable,
                str(root / "examples" / script_name),
                "--output-dir",
                str(output_dir),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        for output_name in output_names:
            artifact = output_dir / output_name
            assert artifact.is_file()
            if artifact.suffix == ".pdf":
                assert artifact.read_bytes().startswith(b"%PDF")
            else:
                assert "\\begin{table}" in artifact.read_text(encoding="utf-8")


def test_hyper_power_set_scale_table_from_reviewer_1_comment_3_1() -> None:
    """Pin every cardinality proposed for the manuscript's scale table."""

    script = Path(__file__).resolve().parents[1] / "examples" / "hyper_power_set_scale.py"
    completed = subprocess.run(
        [sys.executable, str(script)],
        check=True,
        capture_output=True,
        text=True,
    )
    data_rows = [
        line
        for line in completed.stdout.splitlines()
        if line.startswith("| ") and line[2:3].isdigit()
    ]

    assert data_rows == [
        "| 2 | 4 | 5 | trivial | Frame.elements() and independent count |",
        "| 3 | 8 | 19 | Section 3.2 case | Frame.elements() and independent count |",
        "| 4 | 16 | 167 | practical | Frame.elements() and independent count |",
        "| 5 | 32 | 7580 | borderline | Frame.elements() and independent count |",
        "| 6 | 64 | 7828353 | infeasible to materialize | independent count; propositions not materialized |",
    ]


def test_conflict_sweep_values_from_reviewer_1_comment_2_2() -> None:
    """Pin the sweep endpoints and the Section 3.1 operating point."""

    script = Path(__file__).resolve().parents[1] / "examples" / "conflict_sweep.py"
    completed = subprocess.run(
        [sys.executable, str(script)],
        check=True,
        capture_output=True,
        text=True,
    )
    data_rows = [line for line in completed.stdout.splitlines() if line.startswith("t=")]

    assert data_rows == [
        "t=0.10, K=0.005000: Dempster=0.468593, Yager=0.467917, "
        "Dubois-Prade=0.468750, PCR5=0.469583, Smets/TBM=0.468593",
        "t=0.70, K=0.455000: Dempster=0.538991, Yager=0.445417, "
        "Dubois-Prade=0.521250, PCR5=0.529676, Smets/TBM=0.538991",
        "t=0.80, K=0.600000: Dempster=0.560417, Yager=0.424167, "
        "Dubois-Prade=0.524167, PCR5=0.533844, Smets/TBM=0.560417",
    ]

def _pump_sources(frame):
    e, m, h = frame.symbols()
    current = frame.mass({e: 0.65, e | m: 0.20, e | m | h: 0.15})
    vibration = frame.mass({m: 0.60, e | m: 0.25, e | m | h: 0.15})
    pressure = frame.mass({h: 0.25, e | h: 0.15, m | h: 0.10, e | m | h: 0.50})
    return current, vibration, pressure


def test_pump_free_model_dsmc_masses_from_section_3_2() -> None:
    frame = Frame.dsmt(["E", "M", "H"])
    e, m, h = frame.symbols()
    current, vibration, pressure = _pump_sources(frame)

    assert len(frame.elements()) == 19

    result = current.dsmc(vibration, pressure)

    assert result[e & m] == approx(0.2925)
    assert result[e & m & h] == approx(0.0975)
    assert result[e & h] == approx(0.0650)
    assert result[frame.empty] == approx(0.0)
    assert result.total_mass == approx(1.0)


def test_pump_free_model_pignistic_regions_from_section_3_2() -> None:
    frame = Frame.dsmt(["E", "M", "H"])
    current, vibration, pressure = _pump_sources(frame)

    regions = current.dsmc(vibration, pressure).pignistic_regions()

    assert regions["E&M&H"] == approx(0.425, abs=5e-4)
    assert regions["E&M"] == approx(0.257, abs=5e-4)
    assert sum(regions.values()) == approx(1.0)


def test_pump_hybrid_model_dsmh_masses_from_section_3_2() -> None:
    free = Frame.dsmt(["E", "M", "H"])
    current, vibration, pressure = _pump_sources(free)
    hybrid = Frame.hybrid(["E", "M", "H"], empty=["E&H"])
    e, m, h = hybrid.symbols()

    assert len(hybrid.elements()) == 13
    assert not e & h
    assert not e & m & h

    result = current.dsmh(vibration, pressure, model=hybrid)

    expected = {
        e & m: 0.3185,
        e: 0.169,
        m: 0.13775,
        m & h: 0.081875,
        (e & m) | (m & h): 0.0315,
        e | (m & h): 0.017625,
        e | m: 0.05875,
        e | h: 0.003375,
        m | h: 0.00225,
        h: 0.005625,
        e | m | h: 0.17375,
    }
    assert set(result.focal()) == set(expected)
    for proposition, value in expected.items():
        assert result[proposition] == approx(value)
    assert result.total_mass == approx(1.0)


def test_pump_deng_entropy_before_and_after_the_hybrid_constraint() -> None:
    free = Frame.dsmt(["E", "M", "H"])
    current, vibration, pressure = _pump_sources(free)
    hybrid = Frame.hybrid(["E", "M", "H"], empty=["E&H"])

    free_result = current.dsmc(vibration, pressure)
    hybrid_result = current.dsmh(vibration, pressure, model=hybrid)

    assert free_result.deng_entropy() == approx(5.8371, abs=5e-5)
    assert hybrid_result.deng_entropy() == approx(4.5523, abs=5e-5)


def test_pump_hybrid_model_pignistic_regions_from_section_3_2() -> None:
    free = Frame.dsmt(["E", "M", "H"])
    current, vibration, pressure = _pump_sources(free)
    hybrid = Frame.hybrid(["E", "M", "H"], empty=["E&H"])

    result = current.dsmh(vibration, pressure, model=hybrid)
    regions = result.pignistic_regions()

    assert set(regions) == {"E", "M", "H", "E&M", "M&H"}
    assert regions["E&M"] == approx(0.521, abs=5e-4)
    assert regions["M&H"] == approx(0.203, abs=5e-4)
    assert regions["E"] == approx(0.1407, abs=5e-4)
    assert regions["M"] == approx(0.0959, abs=5e-4)
    assert regions["H"] == approx(0.0390, abs=5e-4)
    assert sum(regions.values()) == approx(1.0)


def test_ci_versions_and_coverage_gate_reported_in_section_2() -> None:
    workflow = (
        Path(__file__).resolve().parents[1] / ".github" / "workflows" / "ci.yml"
    ).read_text(encoding="utf-8")

    assert 'python-version: ["3.10", "3.11", "3.12", "3.13", "3.14"]' in workflow
    assert "coverage report --fail-under=90" in workflow
