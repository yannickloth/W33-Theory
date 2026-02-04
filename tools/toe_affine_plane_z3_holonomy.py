#!/usr/bin/env python3
"""
TOE: Z3 holonomy / curvature on the firewall affine-plane quotient.

Given the canonical AG(2,3) coordinate model + fitted Z3 lift laws from:
  artifacts/toe_affine_plane_z3_connection.json

we interpret the per-line lift slope `lambda` as a Z3-valued discrete connection A
on the translation geometry of F3^2.

For each point p and each pair of independent directions (d1,d2), we compute the
plaquette holonomy around the parallelogram:

  p -> p+d1 -> p+d1+d2 -> p+d2 -> p

using:
  hol(p; d1,d2) = A(p,d1) + A(p+d1,d2) - A(p+d2,d1) - A(p,d2)   (mod 3)

This is the discrete curl (curvature) of the Z3 connection.

Outputs:
  - artifacts/toe_affine_plane_z3_holonomy.json
  - artifacts/toe_affine_plane_z3_holonomy.md
"""

from __future__ import annotations

import json
import math
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Dict, Tuple

ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def _write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _mod3(x: int) -> int:
    return int(x) % 3


def _det2(d1: Tuple[int, int], d2: Tuple[int, int]) -> int:
    return _mod3(d1[0] * d2[1] - d1[1] * d2[0])


def main() -> None:
    conn_path = ROOT / "artifacts" / "toe_affine_plane_z3_connection.json"
    conn = _load_json(conn_path)
    if conn.get("status") != "ok":
        raise RuntimeError("toe_affine_plane_z3_connection.json status != ok")

    # Extract coordinate map block_id -> (x,y) and invert it.
    block_xy = {
        int(b["id"]): (int(b["coord_f3_2"][0]), int(b["coord_f3_2"][1]))
        for b in conn["blocks"]
    }
    xy_block = {xy: b for b, xy in block_xy.items()}
    if len(xy_block) != 9:
        raise RuntimeError("Coordinate model is not bijective on 9 blocks")

    # Lambda laws over F3: lam(c) = a*c + b (mod 3), keyed by family string.
    laws = conn["lambda_laws_f3"]
    fam_x = str(("x", None))
    fam_y = str(("y", None))
    fam_m1 = str(("y=mx+c", 1))
    fam_m2 = str(("y=mx+c", 2))
    for k in (fam_x, fam_y, fam_m1, fam_m2):
        if k not in laws:
            raise RuntimeError(f"Missing lambda law for family {k}")

    def lam_from_family_c(fam: str, c: int) -> int:
        law = laws[fam]
        return _mod3(int(law["a"]) * c + int(law["b"]))

    # Define four direction representatives in F3^2.
    # These correspond to the four parallel classes in AG(2,3).
    directions = [
        ((1, 0), fam_y),  # y = const, parameter x
        ((0, 1), fam_x),  # x = const, parameter y
        ((1, 1), fam_m1),  # y = x + c
        ((1, 2), fam_m2),  # y = 2x + c
    ]

    # Connection A(p,d): compute the intercept c of the line through p in direction d,
    # then apply the fitted lambda law for that family.
    def A(p: Tuple[int, int], d: Tuple[int, int], fam: str) -> int:
        x, y = p
        if fam == fam_x:
            c = x
        elif fam == fam_y:
            c = y
        elif fam == fam_m1:
            c = _mod3(y - x)
        elif fam == fam_m2:
            c = _mod3(y - 2 * x)
        else:
            raise RuntimeError(f"Unknown family: {fam}")
        return lam_from_family_c(fam, c)

    # Holonomy distribution across all points and direction pairs.
    hist = Counter()
    by_pair = []
    constant_curvature_minus_det = True
    points = list(xy_block.keys())

    for (d1, fam1), (d2, fam2) in combinations(directions, 2):
        if _det2(d1, d2) == 0:
            continue
        det = int(_det2(d1, d2))
        expected = _mod3(-det)
        pair_hist = Counter()
        for p in points:
            p1 = (_mod3(p[0] + d1[0]), _mod3(p[1] + d1[1]))
            p2 = (_mod3(p[0] + d2[0]), _mod3(p[1] + d2[1]))
            hol = _mod3(
                A(p, d1, fam1) + A(p1, d2, fam2) - A(p2, d1, fam1) - A(p, d2, fam2)
            )
            pair_hist[hol] += 1
            hist[hol] += 1
        if len(pair_hist) != 1:
            constant_curvature_minus_det = False
        else:
            hol_value = next(iter(pair_hist.keys()))
            if hol_value != expected:
                constant_curvature_minus_det = False
        by_pair.append(
            {
                "d1": list(d1),
                "d2": list(d2),
                "det": det,
                "expected_hol_minus_det": expected,
                "hist": {str(k): int(v) for k, v in sorted(pair_hist.items())},
            }
        )

    loops = sum(hist.values())
    probs = [hist[i] / loops for i in [0, 1, 2] if hist[i]]
    entropy = -sum(p * math.log(p, 2) for p in probs) if probs else 0.0

    out = {
        "status": "ok",
        "sources": {"toe_affine_plane_z3_connection": str(conn_path)},
        "counts": {
            "points": 9,
            "direction_pairs": len(by_pair),
            "loops": loops,
        },
        "holonomy_hist": {str(k): int(v) for k, v in sorted(hist.items())},
        "holonomy_entropy_bits": round(entropy, 6),
        "constant_curvature_minus_det": bool(constant_curvature_minus_det),
        "by_direction_pair": by_pair,
        "note": (
            "Holonomy is computed as a Z3 discrete curl using the fitted per-line lambda laws "
            "as a connection A(p,d) on F3^2."
        ),
    }

    json_path = ROOT / "artifacts" / "toe_affine_plane_z3_holonomy.json"
    md_path = ROOT / "artifacts" / "toe_affine_plane_z3_holonomy.md"
    _write_json(json_path, out)

    md = []
    md.append("# TOE affine-plane Z3 holonomy (derived artifact)")
    md.append("")
    md.append("## Counts")
    for k, v in out["counts"].items():
        md.append(f"- {k}: {v}")
    md.append("")
    md.append("## Holonomy histogram (Z3)")
    for k, v in out["holonomy_hist"].items():
        md.append(f"- {k}: {v}")
    md.append("")
    md.append(f"## Entropy\n- {out['holonomy_entropy_bits']} bits")
    _write_md(md_path, "\n".join(md) + "\n")

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
