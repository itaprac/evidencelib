"""Target recognition with two conflicting sensors on a DST frame.

The frame covers friend (F), hostile (H), and neutral (N). Radar strongly
supports hostile while the transponder check strongly supports friend, which
creates high conjunctive conflict. The example contrasts how Dempster's rule
and PCR5 redistribute that conflict. All masses are synthetic and
illustrative.
"""

from __future__ import annotations

from evidencelib import Frame


def main() -> None:
    frame = Frame.dst(["F", "H", "N"])
    friend, hostile, neutral = frame.symbols()

    radar = frame.mass(
        {
            hostile: 0.75,
            hostile | neutral: 0.15,
            frame.total: 0.10,
        }
    )
    transponder = frame.mass(
        {
            friend: 0.70,
            friend | neutral: 0.20,
            frame.total: 0.10,
        }
    )

    conflict = radar.smets(transponder).conflict
    print(f"Conjunctive conflict between the sensors: {conflict:.4f}")

    for label, fused in (
        ("Dempster", radar.dempster(transponder)),
        ("PCR5", radar.pcr5(transponder)),
    ):
        scores = fused.pignistic()
        print(f"{label}:")
        for name in ("F", "H", "N"):
            print(f"  BetP({name}) = {scores[name]:.4f}")
        print(f"  decision: {fused.decision()}")


if __name__ == "__main__":
    main()
