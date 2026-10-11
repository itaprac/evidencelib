# Reproducing the SoftwareX article

Run `make reproduce` from the repository root after `uv sync --extra dev`. The target executes `example_1_weld_dst.py`, `example_2_pump_dsmt.py`, and `example_3_pump_hybrid.py`; together they regenerate the LaTeX tables and vector PDF figures used in Section 3 under `output/`. Each script is also independently runnable and accepts `--output-dir PATH` for writing the artifacts elsewhere.

`example_4_pcr_plus_update.py` reproduces the illustrative example of the software-update article for version 1.3 (PCR5 and PCR6 versus PCR5+ and PCR6+ with three sources, followed by reliability discounting and the decision criteria). It prints its results and writes no files.
