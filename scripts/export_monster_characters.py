#!/usr/bin/env python3
"""Export the full Monster character table to JSON (data/monster_characters.json).

Requires GAP (or Sage/libgap). Produces a compact JSON containing:
  - class_names: ["1A","2A",...]
  - irreps: [{"degree": 1, "values": [..]}, ...]

Usage:
    python scripts/export_monster_characters.py

Run locally, then commit `data/monster_characters.json` to the repo when ready.
"""
from __future__ import annotations

import ast
import json
import shutil
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "monster_characters.json"

if __name__ == "__main__":
    if shutil.which("gap") is None:
        raise SystemExit("GAP not found on PATH — install GAP or use Sage/libgap")

    gap_code = (
        't := CharacterTable("M"); '
        "cn := ClassNames(t); "
        "irr := Irr(t); "
        "degs := List(irr, chi->chi[1]); "
        "vals := List(irr, chi->List(chi, x->x)); "
        'Print("GAP:CLASS_NAMES:", cn, "\n"); '
        'Print("GAP:IRREP_DEGREES:", degs, "\n"); '
        'Print("GAP:CHAR_VALUES:", vals, "\n"); '
        "quit;"
    )

    proc = subprocess.run(
        ["gap", "-q"], input=gap_code, text=True, capture_output=True, check=True
    )
    class_names = None
    degrees = None
    char_values = None

    for line in proc.stdout.splitlines():
        if line.startswith("GAP:CLASS_NAMES:"):
            class_names = ast.literal_eval(line.split(":", 1)[1].strip())
        elif line.startswith("GAP:IRREP_DEGREES:"):
            degrees = ast.literal_eval(line.split(":", 1)[1].strip())
        elif line.startswith("GAP:CHAR_VALUES:"):
            char_values = ast.literal_eval(line.split(":", 1)[1].strip())

    if class_names is None or degrees is None or char_values is None:
        raise SystemExit("Failed to extract Monster character table from GAP output")

    irreps = []
    for deg, vals in zip(degrees, char_values):
        irreps.append({"degree": int(deg), "values": [int(v) for v in vals]})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"class_names": class_names, "irreps": irreps}, indent=2))
    print(
        f"Wrote Monster character table to {OUT} (classes: {len(class_names)}, irreps: {len(irreps)})"
    )
