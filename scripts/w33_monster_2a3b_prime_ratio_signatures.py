#!/usr/bin/env python3
"""Monster 2A×3B prime-class structure constants factor into TOE invariants.

This is a *numerical* bridge between:
  - Monster class algebra (via bundled CTblLib character columns + ATLAS centralizers)
  - W(3,3)/E8-side invariants already established in the repo

Specifically, for the partial distribution of products a·b with a∈2A, b∈3B,
the per-element class-algebra structure constants n_{2A,3B}^C for prime-order
classes C often factor as:

    n_{2A,3B}^{pA} = p * r_p

where r_p hits familiar TOE numbers (e.g. Δ=4, dim_adj(G2)=14, dim_adj(so(6))=15).

Run:
  & .venv\\Scripts\\python.exe -X utf8 scripts\\w33_monster_2a3b_prime_ratio_signatures.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
for p in (ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def _leading_int(s: str) -> int | None:
    out = ""
    for ch in s:
        if "0" <= ch <= "9":
            out += ch
        else:
            break
    if not out:
        return None
    try:
        return int(out)
    except Exception:
        return None


def main() -> None:
    from w33_leech_monster import (
        analyze_monster_2a3b_class_algebra_partial_distribution,
    )
    from w33_padic_ads_cft import analyze_conformal_dimensions

    dist = analyze_monster_2a3b_class_algebra_partial_distribution()
    if dist.get("available") is not True:
        raise SystemExit(
            "Monster 2A×3B distribution unavailable (missing bundled data)."
        )
    classes = dist.get("classes", {})
    if not isinstance(classes, dict):
        raise SystemExit("Unexpected distribution format.")

    # Use the already-proved W33 spectral gap (Δ=4) as a reference constant.
    h = analyze_conformal_dimensions()
    dims = h.get("conformal_dimensions", {})
    if not isinstance(dims, dict):
        raise SystemExit("Unexpected conformal dimension report format.")
    delta = min(int(lam) for lam in dims.keys() if int(lam) > 0)
    assert int(delta) == 4

    targets = [
        "11A",
        "13A",
        "17A",
        "19A",
        "23A",
        "29A",
        "31A",
        "41A",
        "71A",
    ]

    print("=" * 78)
    print("MONSTER 2A×3B PRIME-CLASS RATIO SIGNATURES")
    print("=" * 78)
    print(f"W33 spectral gap Δ = {delta}")
    print()

    ratios: dict[str, int] = {}
    for cls in targets:
        info = classes.get(cls, {})
        if not isinstance(info, dict):
            raise SystemExit(f"Missing class info for {cls}")
        n = int(info.get("structure_constant_per_element", 0) or 0)
        p = _leading_int(cls)
        if p is None or p <= 1:
            raise SystemExit(f"Unexpected prime class label: {cls}")
        if n % p != 0:
            raise SystemExit(f"Non-integer ratio for {cls}: n={n} p={p}")
        r = n // p
        ratios[cls] = int(r)
        print(f"{cls:3s}: n={n:6d} = {p} × {r}")

    print()
    print("Notable exact hits (purely arithmetic facts):")
    print(f"- 23A: r=4 equals Δ={delta}")
    print("- 17A: r=14 (dim adjoint of G2)")
    print("- 31A: r=15 (dim adjoint of so(6))")
    print("- 29A: r=3 (dim adjoint of sl(2))")
    print("- 11A: r=144 = 12^2 (Golay length squared)")
    print("- 19A: r=48 = 2×24 (binary Golay length / Leech factor)")
    print("- 13A: r=156 = 12×13 = 2×78 (E6 adjoint is 78)")

    # Keep these as hard asserts so the report is self-verifying.
    assert ratios["23A"] == 4
    assert ratios["17A"] == 14
    assert ratios["31A"] == 15
    assert ratios["29A"] == 3
    assert ratios["41A"] == 2
    assert ratios["71A"] == 1
    assert ratios["11A"] == 144
    assert ratios["19A"] == 48
    assert ratios["13A"] == 156

    print()
    print("ALL CHECKS PASSED ✓")


if __name__ == "__main__":
    main()
