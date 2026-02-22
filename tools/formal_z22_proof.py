#!/usr/bin/env python3
"""Self-contained symbolic exclusion of z=(2,2).

Provides a pure-symbolic check (no artifacts required) that the affine z-map
`z -> 2*z + 2` cannot preserve the full sign field in any adapted gauge when
paired with an affine involution with linear part conjugate to diag(-1,1).

This implements the short x=0 contradiction used in the docs.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze


def z_map(z: int) -> int:
    """Affine z-map `z -> 2*z + 2` reduced mod 3."""
    return (2 * int(z) + 2) % 3


def z_map_table() -> Dict[int, int]:
    """Return explicit image table of z_map on Z/3Z."""
    return {z: z_map(z) for z in (0, 1, 2)}


def vertical_line_sign_profile() -> Dict[str, Any]:
    """Evaluate the vertical-line sign relation against all z labels.

    The line is L: x=0 with normalized abc=(1,0,0), so product-sign P(L)=+1.
    We compare P(L) against closed-form full-sign s(L,z) for z in {0,1,2} and
    track which z values are fixed by z_map.
    """
    line = tuple(sorted(((0, 0), (0, 1), (0, 2))))
    p_line = 1

    rows = []
    for z in (0, 1, 2):
        s_line = int(analyze._predict_full_sign_closed_form(line, z))
        row = {
            "z": int(z),
            "z_is_fixed_by_z_map": bool(z_map(z) == z),
            "P(L)": int(p_line),
            "s(L,z)": int(s_line),
            "P_equals_s": bool(p_line == s_line),
        }
        rows.append(row)

    fixed_point_candidates = [row for row in rows if row["z_is_fixed_by_z_map"]]
    fixed_point_stabilizers = [
        row for row in fixed_point_candidates if row["P_equals_s"]
    ]

    return {
        "line": [[0, 0], [0, 1], [0, 2]],
        "rows": rows,
        "fixed_point_candidates": fixed_point_candidates,
        "fixed_point_stabilizers": fixed_point_stabilizers,
        "no_fixed_point_stabilizer": len(fixed_point_stabilizers) == 0,
    }


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
    profile = vertical_line_sign_profile()

    return {
        "line": [[int(p[0]), int(p[1])] for p in L],
        "abc": (int(a), int(b), int(c)),
        "P": int(P),
        "s(L,1)": int(s1),
        "holds": bool(holds),
        "reason": reason,
        "z_map_table": z_map_table(),
        "z_map_is_involution": all(z_map(z_map(z)) == z for z in (0, 1, 2)),
        "z_map_fix_1": z_map(1) == 1,
        "vertical_line_sign_profile": profile,
        "no_fixed_point_stabilizer": bool(profile["no_fixed_point_stabilizer"]),
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
