#!/usr/bin/env python3
"""
Small human-readable report of the SU(3) (A2) structure extracted in
artifacts/canonical_su3_gauge_and_cubic.json.

Writes:
  artifacts/canonical_su3_structure_report.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Tuple

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    src = ROOT / "artifacts" / "canonical_su3_gauge_and_cubic.json"
    data = json.loads(src.read_text(encoding="utf-8"))
    if not data.get("counts", {}).get("solvable", False):
        raise RuntimeError(
            "canonical_su3_gauge_and_cubic.json is not solvable; run the solver first."
        )

    sol = data["solution"]
    eps_bits: Dict[str, int] = sol["su3_eps_bits"]
    lconst_bits: Dict[str, int] = sol["ladder_const_bits"]

    orbs_3 = [
        (int(x["orbit"]), tuple(int(t) for t in x["su3_weight"]))
        for x in data["orbits_3"]
    ]
    orbs_3bar = [
        (int(x["orbit"]), tuple(int(t) for t in x["su3_weight"]))
        for x in data["orbits_3bar"]
    ]
    singleton_roots = [
        (i, tuple(int(v) for v in r)) for i, r in enumerate(data["singleton_roots_k2"])
    ]

    # SU3 epsilon table (restricted to the 3 triangle).
    eps_table = {}
    for oa, _wa in orbs_3:
        row = {}
        for ob, _wb in orbs_3:
            if oa == ob:
                continue
            row[str(ob)] = int(eps_bits.get(f"{oa}+{ob}", 0))
        eps_table[str(oa)] = row

    # Ladder constants grouped by singleton root.
    ladder_table = {}
    for sid, rho in singleton_roots:
        entries = {}
        for k, v in lconst_bits.items():
            sid_s, rest = k.split(":", 1)
            if int(sid_s) != sid:
                continue
            entries[rest] = int(v)
        ladder_table[str(sid)] = {"rho_k2": list(rho), "transitions": entries}

    out = {
        "status": "ok",
        "orbits_3": [{"orbit": oi, "su3_weight": list(w)} for oi, w in orbs_3],
        "orbits_3bar": [{"orbit": oi, "su3_weight": list(w)} for oi, w in orbs_3bar],
        "su3_eps_bits_3_triangle": eps_table,
        "ladder_const_bits_by_singleton": ladder_table,
        "notes": [
            "su3_eps_bits_3_triangle gives the extra GF(2) antisymmetry bits needed to factor Lie-bracket signs into SU(3) epsilon ⊗ E6 cubic.",
            "ladder_const_bits are the uniform (per-transition) ladder coefficients after the solved phase gauge; they are not forced to all be +1.",
        ],
    }

    out_path = ROOT / "artifacts" / "canonical_su3_structure_report.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
