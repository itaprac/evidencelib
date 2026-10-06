# References

`evidencelib` implements concepts and rules from belief-function theory,
including Dempster-Shafer theory and Dezert-Smarandache theory.

Useful starting points:

- Shafer, G. (1976). *A Mathematical Theory of Evidence*. Princeton University Press.
- Smarandache, F., & Dezert, J. (eds.). *Advances and Applications of DSmT for Information Fusion*.
- Dezert, J., & Smarandache, F. (2011). *An Introduction to DSmT*. The
  conformance suite follows its definitions of generalized belief functions
  (2-3), DSmC (4), DSmH (5-8), PCR5/PCR6 (15-17), and GPT (27), together with
  the numerical examples on pages 15-23 and the DSm-cardinality table on page 28.
- Dezert, T., Dezert, J., & Smarandache, F. (2021). Improvement of proportional
  conflict redistribution rules of combination of basic belief assignments.
  *Journal of Advances in Information Fusion*, 16(1), 48-73. Source of the
  n-source PCR5/PCR6 formulas (14-15), the binary keeping index (23-24), and
  PCR5+/PCR6+ (25-26); `tests/test_pcr_plus.py` reproduces Examples 1-13.
- Smarandache, F., & Dezert, J. (2004). Proportional conflict redistribution
  rules for information fusion. arXiv:cs/0408064; also Ch. 1 of *Advances and
  Applications of DSmT for Information Fusion*, Vol. 2 (2006). PCR1-PCR5,
  eqs. 21-31; `tests/test_literature_methods.py` reproduces Examples 12.1-12.5
  and Secs. 8-10.
- Dezert, J., & Smarandache, F. (2008). A new probabilistic transformation of
  belief mass assignment. *Proc. Fusion 2008*; arXiv:0807.3669. DSmP, eq. 11,
  Examples 1-9.
- Smarandache, F., Dezert, J., & Tacnet, J.-M. (2010). Fusion of sources of
  evidence with different importances and reliabilities. *Proc. Fusion 2010*;
  hal-00559233. Shafer discounting (eq. 4, Table 3).
- Shafer, G. (1976), p. 252: reliability discounting.
- Dubois, D., & Prade, H. (1986). A set-theoretic view of belief functions.
  *Int. J. General Systems* 12(3); Smets, P. (1993), *Int. J. Approximate
  Reasoning* 9(1). TBM disjunctive rule; numerical example from Denoeux, T.
  (2008), *Artificial Intelligence* 172, eq. 13 and Table 5.
- Jousselme, A.-L., Grenier, D., & Bosse, E. (2001). A new distance between two
  bodies of evidence. *Information Fusion* 2(2), 91-101. Numerical examples as
  reproduced in Jiang, W. (2017), arXiv:1612.05497.
- Zadeh, L. A. (1986). A simple view of the Dempster-Shafer theory of evidence and its implication for the rule of combination. *AI Magazine*, 7(2), 85-90.
