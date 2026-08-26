UV ?= uv

.PHONY: reproduce
reproduce:
	$(UV) run python examples/example_1_weld_dst.py
	$(UV) run python examples/example_2_pump_dsmt.py
	$(UV) run python examples/example_3_pump_hybrid.py
