#!/usr/bin/env python3
"""Check involution-based rule for reduced minimal-certificate orbits.

Rule under test:
  A representative has reduced orbit size (< 2592) iff it is fixed by at least
  one symmetry whose affine part has det=2 and order 2, combined with a z-map
  in {(1,0), (2,0), (2,1)}.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze

Z_INVOLUTIONS = [(1, 0), (2, 0), (2, 1)]


def _pack_witnesses(rows: list[dict[str, Any]]) -> tuple:
    packed = []
    for row in rows:
        line = tuple(sorted((int(p[0]), int(p[1])) for p in row["line"]))
        z = int(row["z"])
        sign = int(row.get("sign_pm1", row.get("sign", 1)))
        packed.append((line, z, sign))
    return tuple(sorted(packed))


def _transform(
    packed: tuple,
    affine_elem: tuple[tuple[int, int, int, int, int], tuple[int, int]],
    z_map: tuple[int, int],
) -> tuple:
    mat, shift = affine_elem
    out = []
    for line, z, sign in packed:
        mapped_line = tuple(sorted(analyze._map_point(mat, shift, p) for p in line))
        mapped_z = int(analyze._map_z(z_map, int(z)))
        out.append((mapped_line, mapped_z, int(sign)))
    return tuple(sorted(out))


def _candidate_affine_involutions() -> (
    list[tuple[tuple[int, int, int, int, int], tuple[int, int]]]
):
    points = [(x, y) for x in range(3) for y in range(3)]
    out = []
    for mat in analyze._gl2_3():
        for shift in points:
            elem = (mat, shift)
            if mat[4] == 2 and analyze._affine_order(elem) == 2:
                out.append(elem)
    return sorted(out)


def _affine_elem_json(
    elem: tuple[tuple[int, int, int, int, int], tuple[int, int]]
) -> dict[str, Any]:
    (a, b, c, d, det), shift = elem
    return {
        "A": [int(a), int(b), int(c), int(d)],
        "det": int(det),
        "shift": [int(shift[0]), int(shift[1])],
        "order": int(analyze._affine_order(elem)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in-json", type=Path, required=True)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=ROOT
        / "artifacts"
        / "e6_f3_trilinear_min_cert_orbit_involution_rule_check.json",
    )
    parser.add_argument("--full-orbit-size", type=int, default=2592)
    args = parser.parse_args()

    payload = json.loads(args.in_json.read_text(encoding="utf-8"))
    reps = payload.get("representatives", [])
    involutions = _candidate_affine_involutions()

    orbit_hist: Counter[str] = Counter()
    first_match_z_hist: Counter[str] = Counter()
    first_match_det_hist: Counter[str] = Counter()
    first_match_order_hist: Counter[str] = Counter()
    match_count_hist: Counter[str] = Counter()
    mismatches: list[dict[str, Any]] = []
    predicted_reduced_count = 0
    observed_reduced_count = 0

    for idx, entry in enumerate(reps):
        rows = entry.get("canonical_repr") or []
        packed = _pack_witnesses(rows)
        orbit_size = int(entry.get("orbit_size", args.full_orbit_size))
        observed_reduced = orbit_size < int(args.full_orbit_size)
        orbit_hist[str(orbit_size)] += 1
        if observed_reduced:
            observed_reduced_count += 1

        matches: list[
            tuple[
                tuple[tuple[int, int, int, int, int], tuple[int, int]], tuple[int, int]
            ]
        ] = []
        for affine_elem in involutions:
            for z_map in Z_INVOLUTIONS:
                if _transform(packed, affine_elem, z_map) == packed:
                    matches.append((affine_elem, z_map))

        predicted_reduced = len(matches) > 0
        if predicted_reduced:
            predicted_reduced_count += 1

        match_count_hist[str(len(matches))] += 1
        if matches:
            first = sorted(matches)[0]
            affine_elem, z_map = first
            first_match_z_hist[str(tuple(int(v) for v in z_map))] += 1
            first_match_det_hist[str(int(affine_elem[0][4]))] += 1
            first_match_order_hist[str(int(analyze._affine_order(affine_elem)))] += 1

        if predicted_reduced != observed_reduced:
            mismatches.append(
                {
                    "index": int(idx),
                    "orbit_size": int(orbit_size),
                    "observed_reduced": bool(observed_reduced),
                    "predicted_reduced": bool(predicted_reduced),
                    "matching_symmetry_count": int(len(matches)),
                }
            )

    out = {
        "status": "ok",
        "source": str(args.in_json),
        "rule_under_test": (
            "reduced orbit iff certificate is fixed by at least one symmetry with "
            "affine part det=2 and order 2, and z-map in {(1,0),(2,0),(2,1)}"
        ),
        "full_orbit_size": int(args.full_orbit_size),
        "representative_count": int(len(reps)),
        "candidate_affine_involution_count": int(len(involutions)),
        "candidate_z_involution_count": int(len(Z_INVOLUTIONS)),
        "observed_orbit_histogram": dict(orbit_hist),
        "observed_reduced_count": int(observed_reduced_count),
        "predicted_reduced_count": int(predicted_reduced_count),
        "matching_symmetry_count_histogram": dict(match_count_hist),
        "first_matching_symmetry_profiles": {
            "z_map_histogram": dict(first_match_z_hist),
            "det_histogram": dict(first_match_det_hist),
            "affine_order_histogram": dict(first_match_order_hist),
        },
        "mismatch_count": int(len(mismatches)),
        "mismatches": mismatches,
        "rule_holds": len(mismatches) == 0,
        "notes": {
            "non_identity_z_involutions": [list(z) for z in Z_INVOLUTIONS],
            "affine_involution_profile_example": (
                _affine_elem_json(involutions[0]) if involutions else None
            ),
        },
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(
        f"Wrote {args.out_json} | reps={len(reps)} | "
        f"mismatches={len(mismatches)} | rule_holds={len(mismatches) == 0}"
    )


if __name__ == "__main__":
    main()
