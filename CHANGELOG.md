# Changelog

All notable changes to `evidencelib` are documented here. The project follows
semantic versioning.

## [1.3.0] - 2026-10-09

This release completes the proportional conflict redistribution (PCR) family,
adds source discounting, distance, and probabilistic transformations, and
aligns several existing rules with their published definitions. Every new or
changed method reproduces the numerical examples of its source paper.

### Added

- `pcr5_plus()` and `pcr6_plus()`: the improved PCR5+ and PCR6+ rules of
  Dezert, Dezert and Smarandache (JAIF 2021). A binary keeping index excludes
  propositions that do not take part in a partial conflict, so the vacuous
  assignment is a neutral element. The index depends only on the structure of
  the focal elements and is cached.
- `conflict_redistribution(..., rule=...)` and the `ConflictTransfer` record:
  a per-product trace of how PCR5, PCR6, PCR5+, or PCR6+ redistributes each
  conflicting product.
- `pcr1()`, `pcr2()`, `pcr3()`, `pcr4()`: the earlier PCR rules of
  Smarandache and Dezert (2004/2006) for two or more sources, including
  dynamic fusion (`model=`) and sources with mass on `empty`.
- `disjunctive()`: the TBM disjunctive rule (Dubois and Prade 1986; Smets
  1993).
- `discount(reliability)`: Shafer's reliability discounting.
- `dsmp()`, `dsmp_of()`, `dsmp_regions()`: the DSmP probabilistic
  transformation of Dezert and Smarandache (2008).
- `jousselme_distance()`: the distance of Jousselme, Grenier and Bosse (2001).
- `decision(criterion)`, `decisions()`, `decision_scores()`: decisions by
  BetP (default, unchanged), DSmP, maximum belief, or maximum plausibility,
  with explicit tie reporting.
- `exact=True` on `from_dict()`, `from_json()`, and `from_csv()` restores a
  computed assignment losslessly (no dropping, no rescaling).
- Conformance tests reproducing the numerical examples of the source papers
  (`tests/test_pcr_plus.py`, `tests/test_literature_methods.py`,
  `tests/test_fidelity.py`).
- Examples `examples/pcr_plus_vacuous_sources.py` (PCR6 versus PCR6+ with
  nearly vacuous sources) and `examples/pcr_family_comparison.py` (Dempster
  and PCR1-PCR6+ side by side).
- Documentation page on discounting, distance, DSmP, and decision criteria,
  and a "Citing evidencelib" section in the README.

### Changed

- `pcr5()` has its own implementation of the general PCR5 rule (Smarandache
  and Dezert 2004, eq. 33; JAIF 2021, eq. 14) and accepts two or more sources.
  It previously called `pcr6()`, which is numerically equal only for two
  sources, and rejected more than two sources. Two-source results are
  unchanged.
- `dubois_prade()` accepts two or more sources and a target `model=`. In a
  dynamic model change, products whose union becomes empty are lost as in the
  original rule (the result sums to less than one) instead of raising.

### Fixed

- Fusion results are returned exactly as computed. Previously every result
  went through the input validation, which dropped masses at or below
  `tolerance` (1e-9) and silently rescaled the rest; Dempster's normalization
  amplified the error (e.g. `{B: 1.0}` instead of `{A: 0.45, B: 0.55}`) and
  raised `TotalConflictError` for conflicts such as `1 - 9e-10`. Dempster's
  rule and the pignistic transformation now raise only at total conflict, and
  `dempster()` normalizes scaled products, so products that underflow in
  floating point no longer cause a false `TotalConflictError`.
- `dsmc()` raises `ValueError` outside the free DSm model, where DSmC is not
  defined; it previously returned the TBM conjunctive result on Shafer's and
  hybrid models.
- `yager()` rejects sources with `m(empty) > 0`, like the other rules that
  assume normal sources; it previously moved that mass to total ignorance.
- Rules that assume normal sources (Yager, Dubois-Prade, DSmH, DSmC, PCR5,
  PCR6, PCR5+, PCR6+) and the uncertainty measures reject any positive
  `m(empty)`, not only values above `tolerance`. PCR1-PCR4 accept such
  sources, as in their original definition.
- `pcr6()` no longer skips conflicting products whose masses sum to at most
  `tolerance`, and computes shares without premature underflow.
- Fusion rules, the pignistic transformation, and the measures reject
  incomplete assignments (masses not summing to one) instead of silently
  rescaling them. A dynamic Dubois-Prade result records its lost mass (also in
  JSON), so an incomplete assignment is detected however small the loss.
- The pignistic transformation, Deng/TFB entropy, and information volume
  handle subnormal masses without losing them.
- Long LaTeX comparisons and Venn annotations no longer hide masses below
  `tolerance`.

### Migration notes

Three calls that used to return a result now raise, because the previous
result did not follow the rule's definition:

```python
# DSmC on Shafer's or a hybrid frame: use the unnormalized conjunctive rule,
# which returns exactly what dsmc() returned before, or the hybrid DSm rule.
m1.conjunctive(m2)   # or m1.smets(m2), m1.dsmh(m2)

# Yager (and PCR5/PCR6, DSmH, ...) on a source with mass on empty, such as a
# raw TBM result: normalize it first if that is what you intend.
m1.smets(m2).normalize().yager(m3)

# A dynamic Dubois-Prade result sums to less than one and is not accepted by
# fusion, pignistic, or measures; rescale it explicitly if appropriate.
m1.dubois_prade(m2, model=target).normalize().pignistic()
```

Fusion results may now contain masses below `tolerance` that were dropped
before; other results change at most by floating-point rounding. Default
imports still clean data as elicited input; pass `exact=True` to restore a
saved fusion result unchanged.

## [1.2.0] - 2026-08-26

### Added

- Uncertainty measures on `MassFunction`: `deng_entropy()`,
  `tfb_entropy(order)` (k-order time fractal-based entropy, whose maximum is
  the higher-order information volume of a mass function),
  `fractal_belief_entropy()`, `information_volume()`, `nonspecificity()`, and
  `strife()`. On free and hybrid DSm frames the measures use DSm
  cardinalities, so they stay consistent across all three models. The
  implementations reproduce the numerical examples of the defining papers,
  pinned in `tests/test_measures.py`.
- `MassFunction.comparison_to_latex()` for publication-ready wide or long
  comparisons of several source assignments.
- `MassFunction.pignistic_comparison_to_latex()` for LaTeX tables containing
  empty-set conflict, singleton pignistic scores, and optional operational
  actions for several fusion results.
- The `proposition_types` mass-plot style for consistent type-based colors and
  an automatically generated proposition-kind legend.
- Article reproduction workflow: `examples/example_1_weld_dst.py`,
  `example_2_pump_dsmt.py`, and `example_3_pump_hybrid.py` regenerate the
  SoftwareX article's tables and vector figures; `make reproduce` runs all
  three. `examples/conflict_sweep.py` quantifies fusion-rule behavior under
  increasing conflict, and `examples/hyper_power_set_scale.py` verifies the
  hyper-power-set cardinalities by independent antichain counting.
- Gallery examples (`examples/gallery/`): loading mass assignments from CSV,
  a MYCIN-style medical diagnosis, and a high-conflict target-recognition
  scenario.
- Property-based invariant tests (`tests/test_properties.py`),
  article-conformance tests (`tests/test_article_examples.py`), and a hybrid
  constraint-closure test.
- Documentation: uncertainty-measure reference, step-by-step hybrid-DSm
  tutorial, and a troubleshooting page for common errors.

### Changed

- `Proposition` stores its Venn regions as an integer bitmask over a dense
  region index; union, intersection, and containment reduce to single integer
  operations and skip re-normalization. The public API is unchanged.
- `plot_mass_comparison()` draws the heatmap with `pcolormesh`, so exported
  PDFs stay fully vector.

## [1.1.0] - 2026-07-09

This release aligns the quantitative core with the definitions and numerical
examples in Dezert and Smarandache's *An Introduction to DSmT*, strengthens the
public data model, and replaces the previous release pipeline with reproducible
quality gates.

### Added

- Full model-aware DSmH fusion through `dsmh(..., model=target_frame)`.
  Source focal propositions remain on their original frame until the target
  constraints are applied, preserving the information required by the `S1`,
  `S2`, and `S3` terms.
- Optional target-model projection for `conjunctive()`, `smets()`,
  `dempster()`, and `yager()`.
- `MassFunction.pignistic_of(proposition)`, implementing generalized BetP for
  any proposition with the DSm-cardinality ratio `C_M(X & A) / C_M(X)`.
- Stable `Frame.model_signature` metadata and JSON schema
  `evidencelib.mass.v2` for exact hybrid-model validation.
- A paper-conformance suite covering hyper-power-set cardinalities, the hybrid
  DSm-cardinality table, DSmC, DSmH, Dempster, Smets, Yager, PCR5, PCR6, and GPT.
- Regression tests for relative-empty propositions, partial intersections,
  TBM belief semantics, non-finite values, model serialization, PCR invariants,
  and large DST construction.
- CI gates for Ruff, strict Mypy, at least 90% statement coverage, Sphinx with
  warnings as errors, package inspection, Twine validation, and an installed
  wheel smoke test.

### Corrected

- Implemented the complete hybrid DSm `S1 + S2 + S3` behavior. In particular,
  `S2` now transfers products of relatively empty focal elements using their
  original `u(X)` rather than sending them unconditionally to total ignorance.
- Corrected `Proposition.union_atoms()`: atom support is derived from minimal
  canonical DNF terms, so `u(A&B)` is `A|B`, not `A|B|C` in a three-atom free
  model.
- Separated static Dubois-Prade from DSmH. `dubois_prade()` is now an
  exactly-two-source static rule and rejects an explicit dynamic target model
  instead of returning a mislabeled DSmH result.
- `belief()` excludes universal empty-set conflict. This is equivalent for a
  generalized bba with `m(empty)=0` and preserves `Bel(A) <= Pl(A)` for raw
  Smets/TBM results.
- Pignistic Venn plots now use the same empty-conflict normalization as
  `pignistic_regions()`.
- Non-finite mass values and invalid tolerances are rejected explicitly instead
  of being silently discarded.
- Fusion results preserve the initiating mass function's numerical tolerance.
- Public `Proposition` construction rejects non-canonical region sets outside
  the selected power/hyper-power space, preventing lossy string serialization.
- Hybrid JSON imports now compare the exact possible-region structure; models
  with equal atom names and region counts but different constraints no longer
  deserialize silently into one another.

### Changed

- Dynamic fusion should be expressed by creating source masses on their
  original frame and passing a separate constrained target frame. Creating
  sources directly on a frame where their focal elements have already collapsed
  to `empty` is rejected by DSmH because the original `u(X)` cannot be recovered.
- PCR5/PCR6 and Dubois-Prade reject source assignments carrying mass on the
  universal empty set, matching the closed-world source assumptions of their
  formulas.
- Legacy `evidencelib.mass.v1` JSON remains readable for DST and free DSmT.
  Hybrid v1 imports are rejected because that schema did not identify model
  constraints unambiguously.
- Bare strings are rejected as `exclusive` groups; use sequences such as
  `exclusive=[("A", "B")]`.
- Package and documentation versions are now synchronized at `1.1.0`.

### Performance

- `Frame.dst()` constructs singleton Shafer regions directly instead of first
  materializing the free `2**n - 1` Venn universe.
- Exclusive-frame element generation now builds the power set directly.
- Free DSm element generation enumerates the unique antichains of the Dedekind
  lattice directly; constrained closures use a frontier, and completed results
  are cached.

### Packaging and maintenance

- Source distributions and wheels explicitly exclude `tmp/`, `dist/`,
  `.clawpatch/`, and generated documentation.
- Removed the tracked full-text PDF extraction from `tmp/pdfs`; local untracked
  research files are ignored and are not modified or packaged.
- The package passes strict typing and retains its `py.typed` marker.
- Documentation versions are read from installed package metadata rather than
  duplicated manually.

### Migration notes

Dynamic DSmH before 1.1.0 commonly recreated masses on the constrained frame:

```python
target = Frame.hybrid(["A", "B", "C"], exclusive=True, empty=["C"])
# Do not recreate historical source masses on target.
```

Keep the original source frame instead:

```python
source = Frame.dst(["A", "B", "C"])
A, B, C = source.symbols()
m1 = source.mass({A: 0.1, B: 0.4, C: 0.2, A | B: 0.3})
m2 = source.mass({A: 0.5, B: 0.1, C: 0.3, A | B: 0.1})

target = Frame.hybrid(["A", "B", "C"], exclusive=True, empty=["C"])
result = m1.dsmh(m2, model=target)
```

If code previously used `dubois_prade()` as an alias for DSmH, choose the rule
explicitly: keep `dubois_prade()` for two-source static problems and use
`dsmh(..., model=target)` for dynamic model changes.

## [1.0.1] - 2026-05-17

- Initial `evidencelib` release with DST, free/hybrid DSmT, core fusion rules,
  proposition parsing, belief measures, and decision support.

[1.1.0]: https://github.com/itaprac/evidencelib/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/itaprac/evidencelib/releases/tag/v1.0.1
