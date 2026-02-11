#!/usr/bin/env python3
"""Self-contained symbolic exclusion of z=(2,2).

Provides a pure-symbolic check (no artifacts required) that the affine z-map
`z -> 2*z + 2` cannot preserve the full sign field in any adapted gauge when
paired with an affine involution with linear part conjugate to diag(-1,1).

This implements the short x=0 contradiction used in the docs.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze


def z_map(z: int) -> int:
    """Affine z-map `z -> 2*z + 2` reduced mod 3."""
    return (2 * int(z) + 2) % 3


def symbolic_exclude_z22_check() -> Dict[str, Any]:
    """Return a small report asserting the contradiction for L: x=0 and z_map=(2,2).

    The vertical line L has normalized abc = (1,0,0). The coordinate-free product
    law implies P(L)=+1. The full-sign closed form predicts s(L,1) = -1. Hence
    P(L) != s1, a contradiction for any supposed invariance under
    (A, z_map=(2,2)).
    """
    # vertical line x=0
    L = tuple(sorted(((0, 0), (0, 1), (0, 2))))

    a, b, c = analyze._normalized_line_abc(L)

    # product sign closed form: P(line)=+1 iff b*c == 0 (normalized a*x+b*y=c)
    P = 1 if (b * c) % 3 == 0 else -1

    # full-sign closed form predicts s(L,1)
    s1 = analyze._predict_full_sign_closed_form(L, 1)

    holds = P != s1
    reason = (
        f"Normalized abc={(a,b,c)} => P(L)={P}; full-sign s(L,1)={s1}; contradiction"
        if holds
        else "No contradiction found"
    )

    return {
        "line": [[int(p[0]), int(p[1])] for p in L],
        "abc": (int(a), int(b), int(c)),
        "P": int(P),
        "s(L,1)": int(s1),
        "holds": bool(holds),
        "reason": reason,
        "z_map_fix_1": z_map(1) == 1,
    }


def main() -> None:
    report = symbolic_exclude_z22_check()
    print(report.get("reason"))
    if report.get("holds"):
        raise SystemExit(0)
    else:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
