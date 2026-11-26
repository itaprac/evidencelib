# evidencelib

[![CI](https://github.com/itaprac/evidencelib/actions/workflows/ci.yml/badge.svg)](https://github.com/itaprac/evidencelib/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/evidencelib.svg)](https://pypi.org/project/evidencelib/)
[![Python Version](https://img.shields.io/pypi/pyversions/evidencelib.svg)](https://pypi.org/project/evidencelib/)
[![Documentation Status](https://readthedocs.org/projects/evidencelib/badge/?version=latest)](https://evidencelib.readthedocs.io/en/latest/?badge=latest)
[![DOI](https://img.shields.io/badge/DOI-10.1016%2Fj.softx.2026.103019-blue)](https://doi.org/10.1016/j.softx.2026.103019)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/itaprac/evidencelib/blob/main/LICENSE)

**evidencelib** is a Python library for belief-function calculations in
Dempster-Shafer theory (DST) and Dezert-Smarandache theory (DSmT). It provides
a zero-dependency, fully typed core for modelling evidence, combining sources,
and making decisions under uncertainty on Shafer's, free DSm, and hybrid DSm
models. Each method follows the definition in the cited source, and the test
suite reproduces the numerical examples published there.

[Documentation](https://evidencelib.readthedocs.io) ·
[PyPI](https://pypi.org/project/evidencelib/) ·
[Examples](https://github.com/itaprac/evidencelib/tree/main/examples) ·
[Changelog](https://github.com/itaprac/evidencelib/blob/main/CHANGELOG.md) ·
[Issues](https://github.com/itaprac/evidencelib/issues)

## Table of contents

- [Installation](#installation)
- [Quick start](#quick-start)
- [Available methods](#available-methods)
  - [Frames of discernment](#frames-of-discernment)
  - [Belief functions](#belief-functions)
  - [Combination rules](#combination-rules)
  - [Probabilistic transformations and decision](#probabilistic-transformations-and-decision)
  - [Source handling and distances](#source-handling-and-distances)
  - [Uncertainty measures](#uncertainty-measures)
  - [Import, export, and plotting](#import-export-and-plotting)
- [Citing evidencelib](#citing-evidencelib)
- [References](#references)
- [License](#license)

## Installation

```bash
pip install evidencelib            # core, no dependencies
pip install "evidencelib[plot]"    # optional Matplotlib plots
```

evidencelib requires Python 3.10 or later.

## Quick start

Two sources assess three exclusive hypotheses. Different combination rules
handle the conflict between them differently and may lead to different
decisions:

```python
from evidencelib import Frame

frame = Frame.dst(["A", "B", "C"])
A, B, C = frame.symbols()

sensor = frame.mass({A: 0.6, B: 0.1, A | B | C: 0.3})
expert = frame.mass({B: 0.5, C: 0.2, A | B | C: 0.3})

sensor.belief(A)                           # 0.6
sensor.plausibility(A)                     # 0.9
sensor.smets(expert).conflict              # 0.44

sensor.dempster(expert).decision()         # 'B'
sensor.yager(expert).decision()            # 'B'
sensor.pcr6(expert).decision()             # 'A'
sensor.pcr6(expert).pignistic()            # {'A': 0.464, 'B': 0.403, 'C': 0.133}
```

Values in comments are rounded to three decimals.

Overlapping hypotheses use the free DSm model, and integrity constraints use a
hybrid model:

```python
free = Frame.dsmt(["A", "B"])
hybrid = Frame.hybrid(["A", "B", "C"], exclusive=True, empty=["C"])
```

See the [quick start guide](https://evidencelib.readthedocs.io/en/latest/quickstart.html)
for a step-by-step introduction.

## Available methods

The numbers in brackets refer to the [References](#references).

### Frames of discernment

| Model | Constructor | Reference |
|---|---|:---:|
| Shafer's model (exhaustive, exclusive hypotheses) | `Frame.dst(atoms)` | [2] |
| Free DSm model (hyper-power set) | `Frame.dsmt(atoms)` | [8] |
| Hybrid DSm model (exclusivity and non-existence constraints) | `Frame.hybrid(atoms, exclusive=..., empty=...)` | [8] |

Propositions are built with `|` (union) and `&` (intersection) or parsed from
strings such as `frame.proposition("A ∩ (B ∪ C)")`.

### Belief functions

| Function | Method | Reference |
|---|---|:---:|
| Mass (basic belief assignment) | `mass(X)` | [2] |
| Belief | `belief(X)` | [2] |
| Plausibility | `plausibility(X)` | [2] |
| Commonality | `commonality(X)` | [2] |
| Conflict, mass of the empty set | `conflict` | [3] |

### Combination rules

| Acronym | Rule | Method | Reference |
|---|---|---|:---:|
| — | Unnormalized conjunctive rule (TBM) | `conjunctive()`, `smets()` | [3] |
| DS | Dempster's rule | `dempster()` | [1], [2] |
| — | Yager's rule | `yager()` | [6] |
| — | Disjunctive rule | `disjunctive()` | [4], [5] |
| DP | Dubois-Prade rule | `dubois_prade()` | [7] |
| DSmC | Classic DSm rule (free model) | `dsmc()` | [8] |
| DSmH | Hybrid DSm rule, static and dynamic | `dsmh(model=...)` | [8] |
| PCR1–PCR4 | Proportional conflict redistribution rules 1–4 | `pcr1()` … `pcr4()` | [9] |
| PCR5 | Proportional conflict redistribution rule 5 | `pcr5()` | [9], [11] |
| PCR6 | Proportional conflict redistribution rule 6 | `pcr6()` | [10], [11] |
| PCR5+, PCR6+ | Improved PCR5 and PCR6 | `pcr5_plus()`, `pcr6_plus()` | [11] |

All rules accept two or more sources. `conflict_redistribution(..., rule=...)` traces how PCR5,
PCR6, PCR5+, or PCR6+ redistributes each conflicting product. Rules that accept `model=` combine
sources elicited on one frame under constraints learned later (dynamic fusion).

### Probabilistic transformations and decision

| Acronym | Method | Function | Reference |
|---|---|---|:---:|
| BetP / GPT | (Generalized) pignistic transformation | `pignistic()`, `pignistic_of(X)`, `pignistic_regions()` | [8], [12] |
| DSmP | DSmP probabilistic transformation | `dsmp()`, `dsmp_of(X)`, `dsmp_regions()` | [13] |
| — | Decision by BetP, DSmP, maximum belief, or maximum plausibility | `decision(criterion)`, `decisions(criterion)` | [2], [12], [13] |

### Source handling and distances

| Method | Function | Reference |
|---|---|:---:|
| Reliability discounting | `discount(reliability)` | [2], [14] |
| Jousselme distance | `jousselme_distance(other)` | [15] |

### Uncertainty measures

On free and hybrid DSm frames the measures use the DSm cardinality, so they
stay consistent across all three models.

| Measure | Function | Reference |
|---|---|:---:|
| Deng entropy | `deng_entropy()` | [16] |
| Time fractal-based (TFB) entropy of order *k* | `tfb_entropy(order=k)` | [17] |
| Fractal-based belief (FB) entropy | `fractal_belief_entropy()` | [18] |
| Information volume | `information_volume()` | [19] |
| Nonspecificity (generalized Hartley measure) | `nonspecificity()` | [20] |
| Strife | `strife()` | [20] |

### Import, export, and plotting

| Feature | Functions |
|---|---|
| JSON and CSV round trips (`exact=True` restores computed results losslessly) | `to_json()`, `from_json()`, `to_csv()`, `from_csv()` |
| Publication-ready LaTeX tables | `to_latex()`, `comparison_to_latex()`, `pignistic_comparison_to_latex()` |
| Plots (requires `evidencelib[plot]`) | `plot()`, `plot_comparison()`, `plot_venn()`, `plot_belief_plausibility()`, `plot_pignistic_decision()` |

## Citing evidencelib

If evidencelib contributes to a scientific publication, please cite:

> Śniegowski, S., Świder, A., Shekhovtsov, A., & Sałabun, W. (2026).
> evidencelib: A python library for evidence modeling and fusion under
> uncertainty. *SoftwareX*, 36, 103019.
> https://doi.org/10.1016/j.softx.2026.103019

```bibtex
@article{sniegowski2026evidencelib,
  title={evidencelib: A python library for evidence modeling and fusion under uncertainty},
  author={{\'S}niegowski, Szymon and {\'S}wider, Adrianna and Shekhovtsov, Andrii and Sa{\l}abun, Wojciech},
  journal={SoftwareX},
  volume={36},
  pages={103019},
  year={2026},
  publisher={Elsevier},
  doi={10.1016/j.softx.2026.103019}
}
```

## References

[1] Dempster, A. P. (1967). Upper and lower probabilities induced by a
multivalued mapping. *The Annals of Mathematical Statistics*, 38(2), 325–339.
https://doi.org/10.1214/aoms/1177698950

[2] Shafer, G. (1976). *A Mathematical Theory of Evidence*. Princeton
University Press.

[3] Smets, P., & Kennes, R. (1994). The transferable belief model.
*Artificial Intelligence*, 66(2), 191–234.
https://doi.org/10.1016/0004-3702(94)90026-4

[4] Smets, P. (1993). Belief functions: the disjunctive rule of combination
and the generalized Bayesian theorem. *International Journal of Approximate
Reasoning*, 9(1), 1–35.
https://doi.org/10.1016/0888-613X(93)90005-X

[5] Dubois, D., & Prade, H. (1986). A set-theoretic view of belief functions.
*International Journal of General Systems*, 12(3), 193–226.
https://doi.org/10.1080/03081078608934937

[6] Yager, R. R. (1987). On the Dempster-Shafer framework and new combination
rules. *Information Sciences*, 41(2), 93–137.
https://doi.org/10.1016/0020-0255(87)90007-7

[7] Dubois, D., & Prade, H. (1988). Representation and combination of
uncertainty with belief functions and possibility measures. *Computational
Intelligence*, 4(3), 244–264.
https://doi.org/10.1111/j.1467-8640.1988.tb00279.x

[8] Dezert, J., & Smarandache, F. (2009). An introduction to DSmT. In
F. Smarandache & J. Dezert (Eds.), *Advances and Applications of DSmT for
Information Fusion: Collected Works*, Vol. 3. American Research Press.
[arXiv:0903.0279](https://arxiv.org/abs/0903.0279).

[9] Smarandache, F., & Dezert, J. (2004). Proportional conflict
redistribution rules for information fusion. [arXiv:cs/0408064](https://arxiv.org/abs/cs/0408064). Also in
F. Smarandache & J. Dezert (Eds.), *Advances and Applications of DSmT for
Information Fusion: Collected Works*, Vol. 2 (2006), Ch. 1.

[10] Martin, A., & Osswald, C. (2006). A new generalization of the
proportional conflict redistribution rule stable in terms of decision. In
F. Smarandache & J. Dezert (Eds.), *Advances and Applications of DSmT for
Information Fusion: Collected Works*, Vol. 2 (pp. 69–88). American Research
Press. [arXiv:0806.1797](https://arxiv.org/abs/0806.1797).

[11] Dezert, T., Dezert, J., & Smarandache, F. (2021). Improvement of
proportional conflict redistribution rules of combination of basic belief
assignments. *Journal of Advances in Information Fusion*, 16(1), 48–74.

[12] Smets, P. (2005). Decision making in the TBM: the necessity of the
pignistic transformation. *International Journal of Approximate Reasoning*,
38(2), 133–147.
https://doi.org/10.1016/j.ijar.2004.05.003

[13] Dezert, J., & Smarandache, F. (2008). A new probabilistic transformation
of belief mass assignment. *Proceedings of the 11th International Conference
on Information Fusion*, 1–8. [arXiv:0807.3669](https://arxiv.org/abs/0807.3669).

[14] Smarandache, F., Dezert, J., & Tacnet, J.-M. (2010). Fusion of sources of
evidence with different importances and reliabilities. *Proceedings of the
13th International Conference on Information Fusion*, 1–8.
https://doi.org/10.1109/ICIF.2010.5712071

[15] Jousselme, A.-L., Grenier, D., & Bossé, É. (2001). A new distance between
two bodies of evidence. *Information Fusion*, 2(2), 91–101.
https://doi.org/10.1016/S1566-2535(01)00026-4

[16] Deng, Y. (2016). Deng entropy. *Chaos, Solitons & Fractals*, 91,
549–553.
https://doi.org/10.1016/j.chaos.2016.07.014

[17] Zhou, Q., & Deng, Y. (2022). Higher order information volume of mass
function. *Information Sciences*, 586, 501–513.
https://doi.org/10.1016/j.ins.2021.12.005

[18] Zhou, Q., & Deng, Y. (2022). Fractal-based belief entropy.
*Information Sciences*, 587, 265–282.
https://doi.org/10.1016/j.ins.2021.12.032

[19] Deng, Y. (2020). Information volume of mass function. *International
Journal of Computers Communications & Control*, 15(6), 3983.
https://doi.org/10.15837/ijccc.2020.6.3983

[20] Klir, G. J., & Wierman, M. J. (1999). *Uncertainty-Based Information:
Elements of Generalized Information Theory*. Physica-Verlag.
https://doi.org/10.1007/978-3-7908-1869-7

## License

evidencelib is released under the [MIT License](https://github.com/itaprac/evidencelib/blob/main/LICENSE).
