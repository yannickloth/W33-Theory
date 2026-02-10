#!/usr/bin/env python3
"""Classify canonical representatives with geotype & orbit summaries.

Usage:
  py -3 tools/classify_canonical_reps.py --in-json artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_20k.json --out-json artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_20k_with_geotypes.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze


def canonical_to_witness_rows(canon):
    # convert representation item to the witnesses format used by analyzers
    return [
        {
            "line": [list(p) for p in r["line"]],
            "z": int(r["z"]),
            "sign_pm1": int(r.get("sign", r.get("sign_pm1", 1))),
            "line_type": r.get("line_type"),
        }
        for r in canon
    ]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--in-json", type=Path, required=True)
    p.add_argument(
        "--out-json",
        type=Path,
        default=ROOT
        / "artifacts"
        / "e6_f3_trilinear_min_cert_enumeration_with_geotypes.json",
    )
    args = p.parse_args()

    payload = json.loads(args.in_json.read_text(encoding="utf-8"))
    reps = payload.get("representatives", [])

    out = {
        "status": "ok",
        "source": str(args.in_json),
        "k_min": payload.get("k_min"),
        "distinct_representatives": len(reps),
        "representatives": [],
    }
    for idx, entry in enumerate(reps):
        canon = entry.get("canonical_repr") or []
        # ensure canonical list uses expected keys
        # convert to analyzer's expected input
        witness_rows = canonical_to_witness_rows(canon)
        geotype = analyze._classify_certificate_witnesses(witness_rows)
        orbit = analyze._witness_orbit_stats(witness_rows)
        out_entry = {
            "canonical_repr": canon,
            "geotype": geotype,
            "orbit_size": orbit.get("orbit_size"),
            "canonical_orbit_rep": orbit.get("canonical_rep"),
        }
        out["representatives"].append(out_entry)

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {args.out_json} (geotypes for {len(reps)} representatives)")


if __name__ == "__main__":
    main()
