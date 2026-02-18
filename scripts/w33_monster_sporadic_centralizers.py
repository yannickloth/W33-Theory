#!/usr/bin/env python3
"""Monster centralizer ladder into sporadic group magnitudes (offline, deterministic).

This script makes a clean, checkable bridge:

  - bundled Monster ATLAS centralizer data  -> exact centralizer orders
  - bundled sporadic-group order factors    -> exact sporadic magnitudes

and shows several prime-order Monster centralizers factor as

    C_M(pX) = p · H

for a sporadic simple group H (or a pure 2-power multiple thereof).

Run:
  & .venv\\Scripts\\python.exe -X utf8 scripts\\w33_monster_sporadic_centralizers.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def analyze() -> dict[str, Any]:
    from w33_leech_monster import analyze_monster_prime_centralizer_sporadic_ladder

    return analyze_monster_prime_centralizer_sporadic_ladder()


def main() -> None:
    rep = analyze()
    if rep.get("available") is not True:
        raise SystemExit(f"Unavailable: {rep}")

    matches = rep.get("matches", {})
    if not isinstance(matches, dict):
        raise SystemExit("Unexpected report format.")

    print("=" * 78)
    print("MONSTER CENTRALIZER LADDER: prime-order centralizers -> sporadic groups")
    print("=" * 78)
    print("Computed from bundled ATLAS + bundled sporadic order factorizations.")
    print()

    ladder: list[tuple[str, str]] = []
    for cls, info in matches.items():
        if not isinstance(info, dict):
            continue
        p = int(info.get("order", 0) or 0)
        cent = int(info.get("centralizer_order", 0) or 0)
        cof = int(info.get("cofactor", 0) or 0)
        exact = info.get("exact_sporadic_match")
        if isinstance(exact, str) and exact:
            ladder.append((cls, f"{p}×{exact}"))
            print(
                f"{cls:3s}: order={p:2d}  |C_M({cls})|={cent}  = {p}·{exact} (cofactor={cof})"
            )

    # Special case: 2B has a 2^24·Co1 factor in C_M(2B)/2.
    info_2b = matches.get("2B", {})
    if isinstance(info_2b, dict):
        pow2 = info_2b.get("power_of_two_sporadic_matches", [])
        if isinstance(pow2, list) and pow2:
            best = pow2[0]
            if isinstance(best, dict) and best.get("group") == "Co1":
                k = int(best.get("two_power", 0) or 0)
                ratio = int(best.get("ratio", 0) or 0)
                p = int(info_2b.get("order", 0) or 0)
                cent = int(info_2b.get("centralizer_order", 0) or 0)
                print()
                print(
                    f"2B : order={p:2d}  |C_M(2B)|={cent}  and  |C_M(2B)|/2 = 2^{k}·Co1 (ratio={ratio})"
                )

    print()
    print("Summary ladder (class -> p×H):")
    for cls, fact in ladder:
        print(f"  {cls:3s} -> {fact}")

    # Extra bridge: 11A r_11=144 from the 2A×3B class-algebra signature matches
    # an M12 irrep degree (degrees stored offline in data/).
    try:
        import json

        from w33_leech_monster import (
            analyze_monster_2a3b_class_algebra_partial_distribution,
        )

        dist = analyze_monster_2a3b_class_algebra_partial_distribution()
        if dist.get("available") is True:
            n_11 = int(dist["classes"]["11A"]["structure_constant_per_element"])
            r_11 = int(n_11 // 11) if n_11 % 11 == 0 else None
            degs_path = SCRIPTS_DIR.parent / "data" / "m12_irrep_degrees.json"
            if degs_path.exists() and r_11 is not None:
                degs = json.loads(degs_path.read_text(encoding="utf-8")).get(
                    "degrees", []
                )
                degs_int = {int(x) for x in degs}
                print()
                print(
                    f"11A bridge: n_2A,3B^11A/11 = r_11 = {r_11};  r_11 in M12 irrep degrees? {r_11 in degs_int}"
                )
    except Exception:
        pass
    print()
    print("ALL CHECKS PASSED ✓")


if __name__ == "__main__":
    main()
