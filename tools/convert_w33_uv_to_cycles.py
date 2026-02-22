#!/usr/bin/env python3
"""Convert w33_uv_parser_det1_results.json -> cycles JSON suitable for extract_e8_rootword_cocycle.py

Writes analysis/minimal_commutator_cycles/w33_uv_parser_det1_results_cycles_for_e8.json
"""
from __future__ import annotations

import json
from pathlib import Path

IN = Path("analysis/minimal_commutator_cycles/w33_uv_parser_det1_results.json")
OUT = Path(
    "analysis/minimal_commutator_cycles/w33_uv_parser_det1_results_cycles_for_e8.json"
)

js = json.loads(IN.read_text(encoding="utf-8"))
rows = js.get("rows", [])
cycles = []
for r in rows:
    cyc = {"cycle": r.get("cycle")}
    if r.get("status") == "ok":
        cyc["k"] = r.get("k_canonical")
    else:
        cyc["k"] = None
    cycles.append(cyc)
OUT.write_text(json.dumps(cycles, indent=2), encoding="utf-8")
print("Wrote", OUT, "with", len(cycles), "cycles")
