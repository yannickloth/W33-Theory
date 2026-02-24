#!/usr/bin/env python3
"""Monster structure bridge report: (2X,3Y) selection -> cofactor actions -> stabilizers.

This is a deterministic, offline reporting script that ties together:
  - the Ogg-prime pipeline (Δ(2,3,p) support + mass / structure selection), and
  - the centralizer-cofactor recognition + permutation-degree hits.

The goal is to make the *group-theoretic content* of the "structure-best" pair
explicit: when r_p := n/p lands in a cofactor permutation degree, we can read
off a stabilizer magnitude |K| = |H|/r_p (often recognizable by order).

Run:
  & .venv\\Scripts\\python.exe -X utf8 scripts\\w33_monster_structure_bridge_report.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
for p in (ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def _find_perm_hit_for_pair(perm_hits: object, pair_x: str) -> dict[str, Any] | None:
    if not isinstance(perm_hits, list):
        return None
    for h in perm_hits:
        if not isinstance(h, dict):
            continue
        try:
            r = int(h.get("r", 0) or 0)
        except Exception:
            r = 0
        if r <= 1:
            continue
        if str(h.get("pair") or "").replace("×", "x") == str(pair_x):
            return dict(h)
    return None


def analyze(*, max_q_exp: int = 3) -> dict[str, Any]:
    from scripts.w33_monster_ogg_pipeline import analyze as analyze_pipeline

    rep = analyze_pipeline(max_q_exp=int(max_q_exp))
    if rep.get("available") is not True:
        return {"available": False, "reason": rep.get("reason")}

    results = rep.get("results", [])
    if not isinstance(results, list):
        return {"available": False, "reason": "unexpected pipeline payload"}

    rows: list[dict[str, Any]] = []
    for rec in results:
        if not isinstance(rec, dict):
            continue
        p = int(rec.get("p", 0) or 0)
        best_mass = str(rec.get("best_pair") or "?")
        best_struct = rec.get("best_pair_by_structure")
        why = rec.get("best_pair_by_structure_reason")

        masses = rec.get("mass_by_pair", {})
        m_mass = float(masses.get(best_mass, {}).get("float", 0.0) or 0.0) if isinstance(masses, dict) else 0.0
        m_struct = (
            float(masses.get(str(best_struct), {}).get("float", 0.0) or 0.0)
            if isinstance(masses, dict) and isinstance(best_struct, str)
            else 0.0
        )

        per_class: list[dict[str, Any]] = []
        cof = rec.get("cofactor_perm_hits", {})
        if isinstance(cof, dict) and isinstance(best_struct, str):
            for cls_name, info in cof.items():
                if not isinstance(cls_name, str) or not isinstance(info, dict):
                    continue
                perm_hit = _find_perm_hit_for_pair(info.get("perm_hits"), best_struct)
                per_class.append(
                    {
                        "class_name": cls_name,
                        "cofactor_group": info.get("cofactor_group_recognized"),
                        "cofactor_order": info.get("cofactor_order"),
                        "perm_hit_for_structure_pair": perm_hit,
                    }
                )

        rows.append(
            {
                "p": p,
                "best_by_mass": best_mass,
                "best_by_structure": best_struct,
                "best_by_structure_reason": why,
                "mass_best": m_mass,
                "mass_structure": m_struct,
                "mass_ratio_best_over_structure": (m_mass / m_struct) if (m_mass > 0 and m_struct > 0) else None,
                "classes": list(rec.get("classes", [])) if isinstance(rec.get("classes"), list) else [],
                "bridge": per_class,
            }
        )

    return {
        "available": True,
        "scan_primes": rep.get("scan_primes"),
        "replicability_max_q_exp": rep.get("replicability_max_q_exp"),
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-q-exp", type=int, default=3)
    parser.add_argument(
        "--include-monomial-lifts",
        action="store_true",
        help="Add slow, explicit monomial-lift checks (e.g., 11A -> 2.M12) to the report.",
    )
    parser.add_argument("--out-json", type=Path, default=None)
    args = parser.parse_args()

    rep = analyze(max_q_exp=int(args.max_q_exp))
    if rep.get("available") is not True:
        raise SystemExit(str(rep.get("reason") or "analysis unavailable"))

    lift_11a = None
    if bool(args.include_monomial_lifts):
        try:
            from scripts.w33_monster_11a_m12_golay_bridge import analyze as analyze_11a

            lift_11a = analyze_11a(compute_monomial_order=True)
            if lift_11a.get("available") is not True:
                lift_11a = None
        except Exception:
            lift_11a = None

    print("=" * 78)
    print("MONSTER STRUCTURE BRIDGE: structure-best pair -> cofactor perm degree -> stabilizer")
    print("=" * 78)
    print(f"Primes: {rep.get('scan_primes')}")
    print()

    rows = rep.get("rows", [])
    if not isinstance(rows, list):
        raise SystemExit("Unexpected report payload.")

    for row in rows:
        if not isinstance(row, dict):
            continue
        p = int(row.get("p", 0) or 0)
        mass = str(row.get("best_by_mass") or "?")
        struct = row.get("best_by_structure")
        why = row.get("best_by_structure_reason")
        r = row.get("mass_ratio_best_over_structure")
        tag = ""
        if isinstance(struct, str) and struct and struct != mass:
            tag = f"  (ratio best/structure ≈ {float(r):.3g})" if isinstance(r, (int, float)) else ""
        print(f"p={p:2d}: mass={mass}  structure={struct} ({why}){tag}")

        bridge = row.get("bridge", [])
        if isinstance(bridge, list):
            for b in bridge:
                if not isinstance(b, dict):
                    continue
                cls = str(b.get('class_name') or '?')
                H = b.get("cofactor_group")
                hit = b.get("perm_hit_for_structure_pair")
                if not isinstance(hit, dict):
                    continue
                rr = int(hit.get("r", 0) or 0)
                stab = int(hit.get("stabilizer_order", 0) or 0)
                stab_grp = hit.get("stabilizer_group_recognized")
                if isinstance(stab_grp, str) and stab_grp:
                    print(f"      {cls}: H={H}  r={rr}  |K|={stab} ({stab_grp})")
                else:
                    print(f"      {cls}: H={H}  r={rr}  |K|={stab}")
                if lift_11a is not None and cls == "11A":
                    golay = lift_11a.get("golay", {})
                    if isinstance(golay, dict):
                        order = golay.get("monomial_group_order")
                        is_2m12 = golay.get("is_2m12")
                        if isinstance(order, int) and order > 0:
                            print(f"            monomial lift: |G|={order}  is_2.M12? {bool(is_2m12)}")
        print()

    if args.out_json is not None:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(rep, indent=2), encoding="utf-8")
        print(f"Wrote {args.out_json}")


if __name__ == "__main__":
    main()
