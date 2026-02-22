#!/usr/bin/env python3
"""Run the l3 coordinate tuner with exception capture for debugging."""
import importlib.util
import traceback

spec = importlib.util.spec_from_file_location(
    "tune", "tools/tune_l3_coeffs_coordinate_search.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

try:
    mod.main()
except Exception:
    traceback.print_exc()
    raise
