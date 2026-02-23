#!/usr/bin/env python3
"""Monster (2X,3Y) pair selection rule: mass vs cofactor-spectrum signatures.

This is a thin reporting layer on top of:
  - `scripts/w33_monster_ogg_pipeline.py` (Δ(2,3,p) support + replicability)
  - `scripts/w33_monster_prime_ratio_signatures.py` (r_p ∈ irrep/perm spectra on rungs)
  - `scripts/w33_monster_centralizer_cofactor_groups.py` (cofactor recognition + perm hits)

Key idea:
  "Best by probability mass" and "best by cofactor-spectrum hit" can differ.
  Example: for 11A (C_M(11A)=11·M12), the nontrivial signature r_11=144 occurs for
  2A×3B even though 2A×3A is best by mass.

Run:
  & .venv\\Scripts\\python.exe -X utf8 scripts\\w33_monster_pair_selection_rule.py
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
for p in (ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max-q-exp",
        type=int,
        default=5,
        help="q-exp truncation used in prime replicability checks",
    )
    parser.add_argument("--out-json", type=Path, default=None)
    args = parser.parse_args()

    from scripts.w33_monster_ogg_pipeline import analyze

    rep = analyze(max_q_exp=int(args.max_q_exp))
    if rep.get("available") is not True:
        raise SystemExit(str(rep.get("reason") or "analysis unavailable"))

    results = rep.get("results", [])
    if not isinstance(results, list):
        raise SystemExit("Unexpected report payload.")

    print("=" * 78)
    print("MONSTER PAIR SELECTION RULE: mass-best vs signature-best")
    print("=" * 78)
    print(f"Primes: {rep.get('scan_primes')}")
    print(f"Replicability max_q_exp: {rep.get('replicability_max_q_exp')}")
    print()

    perm_ctr: Counter[str] = Counter()
    irrep_ctr: Counter[str] = Counter()

    rows: list[dict[str, Any]] = []
    for rec in results:
        if not isinstance(rec, dict):
            continue
        p = int(rec.get("p", 0) or 0)
        best = str(rec.get("best_pair") or "?")
        perm = rec.get("recommended_pair_perm_hit")
        irrep = rec.get("recommended_pair_nontrivial_irrep_hit")
        classes = rec.get("classes", [])
        cof = rec.get("cofactor_perm_hits", {})

        if isinstance(perm, str) and perm:
            perm_ctr[perm] += 1
        if isinstance(irrep, str) and irrep:
            irrep_ctr[irrep] += 1

        rows.append(
            {
                "p": p,
                "best_by_mass": best,
                "recommended_perm_hit": perm,
                "recommended_irrep_hit": irrep,
                "classes": classes,
                "cofactor_perm_hits": cof,
            }
        )

        delta = ""
        if isinstance(perm, str) and perm and perm != best:
            delta = "  <-- perm-hit differs"

        print(f"p={p:2d}: best_by_mass={best:6s}  perm_hit={perm!s:6s}  irrep_hit={irrep!s:6s}{delta}")
        if isinstance(classes, list) and classes:
            for cls in classes:
                if not isinstance(cls, str):
                    continue
                grp = None
                if isinstance(cof, dict):
                    ci = cof.get(cls, {})
                    if isinstance(ci, dict):
                        grp = ci.get("cofactor_group_recognized")
                if isinstance(grp, str) and grp:
                    print(f"      {cls}: H={grp}")
                else:
                    print(f"      {cls}")
        print()

    print("-" * 78)
    print("Permutation-hit recommendations (frequency):")
    for k, v in perm_ctr.most_common():
        print(f"  {k:6s}: {v}")
    if not perm_ctr:
        print("  (none)")
    print()

    print("Nontrivial irrep-hit recommendations (frequency):")
    for k, v in irrep_ctr.most_common():
        print(f"  {k:6s}: {v}")
    if not irrep_ctr:
        print("  (none)")
    print("-" * 78)

    if args.out_json is not None:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps({"summary": rows}, indent=2), encoding="utf-8")
        print(f"Wrote {args.out_json}")


if __name__ == "__main__":
    main()

