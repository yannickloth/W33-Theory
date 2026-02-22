#!/usr/bin/env python3
"""Finite-case reduction: prove no Hessian canonical representative is
invariant under the canonical involution diag(-1,1) combined with z_map=(2,2).

This script performs a small symbolic reduction (fixed-line closure checks)
and then exhaustively tests all adapted gauges/pulled-back involutions against
the canonical representatives dataset. The check is intentionally small and
human-readable: if it finds any invariant representative it prints details and
exits nonzero; otherwise it prints a short success message and exits 0.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT))

Z22 = (2, 2)
A_GAUGE = ((2, 0, 0, 1, 2), (0, 0))  # diag(-1,1) in gauge coords
FULL_ORBIT = 2592


def _pack_witnesses(rows: List[Dict[str, Any]]) -> Tuple[Tuple, ...]:
    packed = []
    for row in rows:
        line = tuple(sorted((int(p[0]), int(p[1])) for p in row["line"]))
        z = int(row.get("z", 0))
        sign = int(row.get("sign_pm1", row.get("sign", 1)))
        packed.append((line, z, sign))
    return tuple(sorted(packed))


def _transform_packed(packed, affine_elem, z_map) -> Tuple[Tuple, ...]:
    import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze

    mat, shift = affine_elem
    out = []
    for line, z, sign in packed:
        mapped_line = tuple(sorted(analyze._map_point(mat, shift, p) for p in line))
        mapped_z = int(analyze._map_z(z_map, z))
        out.append((mapped_line, mapped_z, int(sign)))
    return tuple(sorted(out))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--classified-json",
        type=Path,
        default=ROOT
        / "committed_artifacts"
        / "min_cert_census_medium_2026_02_10"
        / "e6_f3_trilinear_min_cert_exact_hessian_full_with_geotypes.json",
    )
    p.add_argument(
        "--sign-map-json",
        type=Path,
        default=ROOT / "artifacts" / "e6_f3_trilinear_map.json",
        help=(
            "Optional sign-field JSON used to derive the canonical affine flag. "
            "If missing, the script falls back to the known flag (point=[2,2], direction='x')."
        ),
    )
    args = p.parse_args()

    import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze

    payload = json.loads(args.classified_json.read_text(encoding="utf-8"))
    reps = payload.get("representatives", [])

    # Locate the flag and adapted gauges from the global product sign if present.
    # Otherwise fall back to the known canonical flag from docs/NOVEL_CONNECTIONS_2026_02_10.md.
    lines = list(analyze._all_affine_lines())
    point = (2, 2)
    direction = "x"
    if args.sign_map_json.exists():
        try:
            lines_map, sign_field = analyze._load_sign_field(args.sign_map_json)
            product_sign = analyze._line_product_signs(lines_map, sign_field)
            flag = analyze._line_product_flag_geometry_check(
                lines_map, product_sign, []
            )
            raw_point = flag.get("missing_point") or flag.get(
                "unique_missing_point_from_negative_lines"
            )
            raw_direction = flag.get("full_positive_direction") or flag.get(
                "distinguished_direction_all_positive"
            )
            if raw_point is not None and raw_direction is not None:
                point = (int(raw_point[0]), int(raw_point[1]))
                direction = str(raw_direction)
                lines = list(lines_map)
        except Exception as exc:
            print(
                f"Warning: failed to load/derive flag from {args.sign_map_json}: {exc}; "
                "falling back to point=[2,2], direction='x'."
            )

    adapted_gauges = analyze._line_product_adapted_gauges(lines, point, direction)

    # For each adapted gauge, form the pulled-back affine involution A
    pulled_as = []
    for g in adapted_gauges:
        g_inv = analyze._inverse_affine(g)
        A = analyze._compose_affine(analyze._compose_affine(g_inv, A_GAUGE), g)
        pulled_as.append(A)

    # Quick symbolic closure test: any line fixed by A must have its z-label set closed under z_map
    bad_candidates = []
    for idx, entry in enumerate(reps):
        rows = entry.get("canonical_repr") or []
        packed = _pack_witnesses(rows)
        for A in pulled_as:
            # compute fixed lines under A
            mat, shift = A
            fixed_lines = set()
            for line, z, sign in packed:
                mapped_line = tuple(
                    sorted(analyze._map_point(mat, shift, p) for p in line)
                )
                if mapped_line == line:
                    fixed_lines.add(line)

            # check closure of z labels for fixed lines under z_map=(2,2)
            closure_ok = True
            for L in fixed_lines:
                zs = {z for (line, z, sign) in packed if line == L}
                mapped_zs = {analyze._map_z(Z22, z) for z in zs}
                # closure means mapped_zs subset of zs
                if not mapped_zs.issubset(zs):
                    closure_ok = False
                    break
            if not closure_ok:
                # cannot be invariant under (A, (2,2)) quickly
                continue

            # if closure passes, do full transform equality check
            transformed = _transform_packed(packed, A, Z22)
            if transformed == packed:
                bad_candidates.append({"index": idx, "A": A, "entry": entry})

    if bad_candidates:
        print("Found representatives invariant under diag(-1,1) + z_map=(2,2):")
        for rec in bad_candidates:
            print(
                json.dumps(
                    {
                        "index": rec["index"],
                        "A": rec["A"],
                        "orbit_size": rec["entry"].get("orbit_size"),
                    },
                    indent=2,
                )
            )
        sys.exit(1)

    print(
        "No representatives invariant under diag(-1,1) + z_map=(2,2) were found (finite-case check)."
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
