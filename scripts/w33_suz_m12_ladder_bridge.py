#!/usr/bin/env python3
"""Suzuki ↔ M12:2 arithmetic bridge inside the Monster 3B Heisenberg backbone.

Two verified ingredients already live in this repo:
  - Monster 3B centralizer: C_M(3B) = 3^{1+12} · 2.Suz
    (scripts/w33_monster_3b_s12_sl27_bridge.py)
  - Monster 11A bridge: M12 acts on the ternary Golay code only after a monomial
    sign lift, producing a 2-cover of order 190,080 (=2·|M12|)
    (scripts/w33_monster_11a_m12_golay_bridge.py)

This small script records the *order-level* compatibility that links those two
threads: the Suzuki group order is divisible by |M12:2|, and the quotient is an
integer index:

    |Suz| / |M12:2| = 2,358,720.

Externally (CTblLib/ATLAS), one finds that 3.Suz has a maximal subgroup
3 × M12.2, which matches this index. We keep the repo-side statement purely
arithmetic (offline) and let the external identification remain a citation.

Run:
  & .venv\\Scripts\\python.exe -X utf8 scripts\\w33_suz_m12_ladder_bridge.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
for p in (ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def _order_from_factorization(fac: dict[int, int]) -> int:
    out = 1
    for p, e in fac.items():
        out *= int(p) ** int(e)
    return int(out)


def analyze() -> dict[str, Any]:
    from scripts.w33_leech_monster import load_sporadic_group_orders

    spor = load_sporadic_group_orders()
    if spor is None or "Suz" not in spor:
        return {"available": False, "reason": "missing Suz in sporadic_group_orders.json"}

    suz_order = _order_from_factorization(spor["Suz"])
    m12_order = 95040
    m12_2_order = 2 * m12_order  # M12:2

    if suz_order % m12_2_order != 0:
        return {"available": False, "reason": "unexpected: |M12:2| ∤ |Suz|"}
    idx = suz_order // m12_2_order

    return {
        "available": True,
        "orders": {
            "M12": int(m12_order),
            "M12:2": int(m12_2_order),
            "Suz": int(suz_order),
            "2.Suz": int(2 * suz_order),
            "3.Suz": int(3 * suz_order),
        },
        "indices": {
            "Suz_over_M12_2": int(idx),
            "3Suz_over_3xM12_2": int(idx),
        },
    }


def main() -> None:
    rep = analyze()
    if rep.get("available") is not True:
        raise SystemExit(f"Unavailable: {rep}")

    o = rep["orders"]
    idx = rep["indices"]

    print("=" * 78)
    print("SUZUKI ↔ M12:2 ORDER BRIDGE (Monster 3B backbone)")
    print("=" * 78)
    print()
    print(f"|M12|    = {o['M12']}")
    print(f"|M12:2|  = {o['M12:2']}  (matches 2.M12 monomial lift order)")
    print(f"|Suz|    = {o['Suz']}")
    print(f"|2.Suz|  = {o['2.Suz']}  (Monster 3B cofactor)")
    print(f"|3.Suz|  = {o['3.Suz']}")
    print()
    print(f"|Suz| / |M12:2| = {idx['Suz_over_M12_2']}")
    print()
    print("ALL CHECKS PASSED ✓")


if __name__ == "__main__":
    main()

