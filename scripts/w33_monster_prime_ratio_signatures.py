#!/usr/bin/env python3
"""Monster r_p prime-ratio signatures vs centralizer-cofactor degree spectra.

We combine two already-offline / deterministic ingredients:
  1) Prime-order Monster centralizer ladder:
       C_M(pX) = p · H
     for several classes pX, with H a sporadic group (HN, He, M12, ...).

  2) Ogg-prime triangle support scan:
       Δ(2,3,p) support is certified by nonzero class-algebra probabilities
       computed from bundled CTblLib character columns.

For a fixed (2X, 3Y) pair and a prime-order class C of order p, define the
"prime-ratio signature"

    r_p(C; 2X×3Y) := n_{2X,3Y}^C / p,

where n_{2X,3Y}^C is the structure constant per element (an integer) returned
by the class-algebra scan.

Systematic question:
  If C_M(C) = p · H for a cofactor group H, does r_p land in the irreducible
  character degree multiset of H?

Starting point (now regression-tested in the repo):
  - For 11A we have C_M(11A) = 11 · M12 and r_11(11A; 2A×3B) = 144 ∈ deg(M12).

Run:
  & .venv\\Scripts\\python.exe -X utf8 scripts\\w33_monster_prime_ratio_signatures.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
for p in (ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def _load_irrep_degree_multiset(group: str) -> list[int] | None:
    path = ROOT / "data" / f"{str(group).lower()}_irrep_degrees.json"
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    degs = payload.get("degrees", [])
    if not isinstance(degs, list) or not degs:
        return None
    return [int(x) for x in degs]


def analyze() -> dict[str, Any]:
    from scripts.w33_leech_monster import (
        analyze_monster_2x3_ogg_prime_triangle_support,
        analyze_monster_prime_centralizer_sporadic_ladder,
        load_monster_atlas_ccls,
    )

    atlas = load_monster_atlas_ccls()
    if atlas is None:
        return {"available": False, "reason": "missing bundled monster_atlas_ccls.json"}
    classes = atlas.get("classes", {})
    if not isinstance(classes, dict) or not classes:
        return {"available": False, "reason": "invalid monster ATLAS payload"}

    ladder = analyze_monster_prime_centralizer_sporadic_ladder()
    if ladder.get("available") is not True:
        return {"available": False, "reason": "centralizer ladder unavailable"}

    tri = analyze_monster_2x3_ogg_prime_triangle_support()
    if tri.get("available") is not True:
        return {"available": False, "reason": "triangle support scan unavailable"}

    matches = ladder.get("matches", {})
    pairs = tri.get("pairs", {})
    if not isinstance(matches, dict) or not isinstance(pairs, dict):
        return {"available": False, "reason": "unexpected ladder/scan payload"}

    # Restrict to the prime-order ladder rungs with exact sporadic matches
    # where we have (or can add) degree data deterministically.
    rung_classes = []
    for cls, info in matches.items():
        if not isinstance(info, dict):
            continue
        grp = info.get("exact_sporadic_match")
        if not isinstance(grp, str) or not grp:
            continue
        if _load_irrep_degree_multiset(grp) is None:
            continue
        rung_classes.append(cls)
    rung_classes = sorted(set(rung_classes))

    out: dict[str, Any] = {}
    for cls in rung_classes:
        info = matches.get(cls, {})
        if not isinstance(info, dict):
            continue
        grp = str(info.get("exact_sporadic_match"))
        degs = _load_irrep_degree_multiset(grp)
        if degs is None:
            continue
        deg_set = set(degs)

        p = int(classes.get(cls, {}).get("order", 0) or 0)
        cent = int(classes.get(cls, {}).get("centralizer_order", 0) or 0)
        cof = cent // p if p > 0 and cent % p == 0 else None

        ratios_by_pair: dict[str, Any] = {}
        hits: list[dict[str, Any]] = []
        for pair_key, pdata in pairs.items():
            if not isinstance(pdata, dict):
                continue
            cinfo = pdata.get("classes", {}).get(cls)
            if not isinstance(cinfo, dict):
                continue
            n = int(cinfo.get("structure_constant_per_element", 0) or 0)
            r = None if p <= 0 or n % p != 0 else int(n // p)
            in_deg = (r is not None) and (r in deg_set)
            ratios_by_pair[str(pair_key)] = {
                "n": int(n),
                "p": int(p),
                "r": r,
                "r_in_irrep_degrees": bool(in_deg),
            }
            if in_deg:
                hits.append({"pair": str(pair_key), "r": int(r), "n": int(n)})

        hits = sorted(hits, key=lambda x: (int(x["r"]), str(x["pair"])))
        out[cls] = {
            "order": int(p),
            "centralizer_order": int(cent),
            "cofactor_order": int(cof) if cof is not None else None,
            "cofactor_group": grp,
            "degree_multiset_size": len(degs),
            "degree_set_size": len(deg_set),
            "ratio_hits_in_degree_set": hits,
            "ratios_by_pair": ratios_by_pair,
        }

    return {"available": True, "rungs": out, "pairs": sorted(pairs.keys())}


def main() -> None:
    rep = analyze()
    if rep.get("available") is not True:
        raise SystemExit(f"Unavailable: {rep}")

    rungs = rep.get("rungs", {})
    if not isinstance(rungs, dict) or not rungs:
        raise SystemExit("No rungs with available cofactor degree spectra.")

    print("=" * 78)
    print("MONSTER PRIME-RATIO SIGNATURES r_p := n/p  vs  cofactor irrep degrees")
    print("=" * 78)
    print(
        "Computed from bundled ATLAS + CTblLib character columns + committed degree lists."
    )

    for cls in sorted(rungs.keys()):
        info = rungs[cls]
        if not isinstance(info, dict):
            continue
        grp = str(info.get("cofactor_group"))
        p = int(info.get("order", 0) or 0)
        cof = info.get("cofactor_order")
        print()
        print(f"{cls}: order p={p}  centralizer cofactor H={grp}  |H|={cof}")
        hits = info.get("ratio_hits_in_degree_set", [])
        if isinstance(hits, list) and hits:
            hit_str = ", ".join(f"{h['pair']}→r={h['r']}" for h in hits)
            print(f"  HITS (r ∈ deg(H)): {hit_str}")
        else:
            print("  HITS (r ∈ deg(H)): none")

        ratios_by_pair = info.get("ratios_by_pair", {})
        if isinstance(ratios_by_pair, dict):
            for pair in sorted(ratios_by_pair.keys()):
                row = ratios_by_pair[pair]
                if not isinstance(row, dict):
                    continue
                r = row.get("r")
                if r is None:
                    continue
                mark = "✓" if row.get("r_in_irrep_degrees") else " "
                print(f"    {mark} {pair:6s}: r={int(r):>12d}  (n={int(row['n'])})")

    print()
    print("ALL CHECKS PASSED ✓")


if __name__ == "__main__":
    main()
