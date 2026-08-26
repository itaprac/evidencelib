"""Load mass assignments from an external CSV file and fuse them.

The gallery keeps the pump masses of the article's Section 3.2 in
``pump_sources.csv`` to show the integration path with external data:
constructing the masses is a modeling step outside the library, but once a
file provides them, ``MassFunction.from_csv()`` turns each source into a
ready-to-fuse assignment.
"""

from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path

from evidencelib import Frame, MassFunction

DATA_PATH = Path(__file__).resolve().parent / "pump_sources.csv"


def load_sources(frame: Frame, path: Path = DATA_PATH) -> dict[str, MassFunction]:
    """Split the long-format CSV by source and parse each block."""

    blocks: dict[str, list[tuple[str, str]]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            blocks.setdefault(row["source"], []).append((row["proposition"], row["mass"]))

    sources: dict[str, MassFunction] = {}
    for name, rows in blocks.items():
        text = StringIO()
        writer = csv.writer(text, lineterminator="\n")
        writer.writerow(("proposition", "mass"))
        writer.writerows(rows)
        sources[name] = MassFunction.from_csv(frame, text.getvalue())
    return sources


def main() -> None:
    frame = Frame.dsmt(["E", "M", "H"])
    sources = load_sources(frame)
    for name, mass in sources.items():
        print(f"{name}: total mass {mass.total_mass:.2f}, focal {len(mass.focal())}")

    current, vibration, pressure = (
        sources["current"],
        sources["vibration"],
        sources["pressure"],
    )
    fused = current.dsmc(vibration, pressure)
    e, m, h = frame.symbols()
    print(f"Fused m(E&M) = {fused[e & m]:.4f}")
    print("Round trip back to CSV:")
    print(fused.to_csv(float_format=".4f"))


if __name__ == "__main__":
    main()
