#!/usr/bin/env python3
"""Verify reduced-orbit equivalence against the canonical involution form.

Closed-form criterion under test:
  A representative has reduced orbit size (1296) iff it is invariant under at
  least one affine involution (det=2, order=2) paired with z-map in
  {(1,0),(2,0),(2,1)}.

Algebraic refinement:
  Every such affine involution has linear part GL(2,3)-conjugate to
  diag(-1,1), so the reduction mechanism is a conjugate-reflection symmetry.
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

Z_INVOLUTIONS = [(1, 0), (2, 0), (2, 1)]
FULL_ORBIT = 2592


def _pack_witnesses(rows: list[dict[str, Any]]) -> tuple[tuple, ...]:
    packed = []
    for row in rows:
        line = tuple(sorted((int(p[0]), int(p[1])) for p in row["line"]))
        z = int(row.get("z", 0))
        sign = int(row.get("sign_pm1", row.get("sign", 1)))
        packed.append((line, z, sign))
    return tuple(sorted(packed))


def _transform_packed(
    packed: tuple[tuple, ...],
    affine_elem: tuple[tuple[int, int, int, int, int], tuple[int, int]],
    z_map: tuple[int, int],
) -> tuple[tuple, ...]:
    import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze

    mat, shift = affine_elem
    out = []
    for line, z, sign in packed:
        mapped_line = tuple(sorted(analyze._map_point(mat, shift, p) for p in line))
        mapped_z = int(analyze._map_z(z_map, z))
        out.append((mapped_line, mapped_z, int(sign)))
    return tuple(sorted(out))


def _candidate_affine_involutions() -> (
    list[tuple[tuple[int, int, int, int, int], tuple[int, int]]]
):
    import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze

    points = [(x, y) for x in range(3) for y in range(3)]
    out = []
    for mat in analyze._gl2_3():
        for shift in points:
            elem = (mat, shift)
            if mat[4] == 2 and analyze._affine_order(elem) == 2:
                out.append(elem)
    return sorted(out)


def _is_conjugate_to_diag(mat: tuple[int, int, int, int, int]) -> bool:
    import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze

    diag = (2, 0, 0, 1, 2)  # diag(-1,1) over F3
    for u in analyze._gl2_3():
        u_inv = analyze._inverse_affine((u, (0, 0)))[0]
        conj = analyze._compose_affine((u_inv, (0, 0)), (mat, (0, 0)))
        conj = analyze._compose_affine(conj, (u, (0, 0)))
        if conj[0] == diag:
            return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--in-json",
        type=Path,
        default=ROOT
        / "artifacts"
        / "e6_f3_trilinear_min_cert_enumeration_hessian_exhaustive2_with_geotypes.json",
    )
    parser.add_argument(
        "--sign-map-json",
        type=Path,
        default=ROOT / "artifacts" / "e6_f3_trilinear_map.json",
        help="Deprecated compatibility arg; not required by this checker.",
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=ROOT
        / "artifacts"
        / "e6_f3_trilinear_reduced_orbit_closed_form_equiv.json",
    )
    args = parser.parse_args()

    payload = json.loads(args.in_json.read_text(encoding="utf-8"))
    reps = payload.get("representatives", [])
    involutions = _candidate_affine_involutions()

    observed_reduced = 0
    predicted_reduced = 0
    mismatches = []
    matched_mats: set[tuple[int, int, int, int, int]] = set()
    match_count_hist = Counter()
    full_orbit_match_hist = Counter()
    reduced_orbit_match_hist = Counter()

    for idx, entry in enumerate(reps):
        rows = entry.get("canonical_repr") or []
        packed = _pack_witnesses(rows)
        orbit_size = int(entry.get("orbit_size", FULL_ORBIT))
        observed = orbit_size < FULL_ORBIT
        if observed:
            observed_reduced += 1

        match_count = 0
        for affine_elem in involutions:
            for z_map in Z_INVOLUTIONS:
                if _transform_packed(packed, affine_elem, z_map) == packed:
                    match_count += 1
                    matched_mats.add(affine_elem[0])
        found = match_count > 0

        if found:
            predicted_reduced += 1
        match_count_hist[str(int(match_count))] += 1
        if observed:
            reduced_orbit_match_hist[str(int(match_count))] += 1
        else:
            full_orbit_match_hist[str(int(match_count))] += 1

        if found != observed:
            mismatches.append(
                {
                    "index": int(idx),
                    "orbit_size": int(orbit_size),
                    "observed_reduced": bool(observed),
                    "predicted_reduced": bool(found),
                    "matching_symmetry_count": int(match_count),
                }
            )

    pulled_back_matrices = []
    for mat in sorted(matched_mats):
        pulled_back_matrices.append(
            {
                "A": [int(v) for v in mat[:4]],
                "det": int(mat[4]),
                "conjugate_to_diag": bool(_is_conjugate_to_diag(mat)),
            }
        )

    full_all_zero = all(
        int(k) == 0 for k, v in full_orbit_match_hist.items() if int(v) > 0
    )
    reduced_all_positive = all(
        int(k) > 0 for k, v in reduced_orbit_match_hist.items() if int(v) > 0
    )
    reduced_all_exactly_one = all(
        int(k) == 1 for k, v in reduced_orbit_match_hist.items() if int(v) > 0
    )
    strict_profile_holds = (
        (len(mismatches) == 0) and full_all_zero and reduced_all_exactly_one
    )

    out = {
        "status": "ok",
        "source": str(args.in_json),
        "representative_count": len(reps),
        "candidate_affine_involution_count": len(involutions),
        "observed_reduced_count": int(observed_reduced),
        "predicted_reduced_count": int(predicted_reduced),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "equivalent": len(mismatches) == 0,
        "match_count_histogram": dict(
            sorted(match_count_hist.items(), key=lambda item: int(item[0]))
        ),
        "symmetry_profile": {
            "full_orbit_match_count_histogram": dict(
                sorted(full_orbit_match_hist.items(), key=lambda item: int(item[0]))
            ),
            "reduced_orbit_match_count_histogram": dict(
                sorted(reduced_orbit_match_hist.items(), key=lambda item: int(item[0]))
            ),
            "full_orbit_all_zero_matches": bool(full_all_zero),
            "reduced_orbit_all_positive_matches": bool(reduced_all_positive),
            "reduced_orbit_all_exactly_one_match": bool(reduced_all_exactly_one),
            "strict_profile_holds": bool(strict_profile_holds),
        },
        "pulled_back_matrix_count": len(pulled_back_matrices),
        "pulled_back_matrices": pulled_back_matrices,
        "matrix_conjugacy_all_true": all(
            bool(rec.get("conjugate_to_diag")) for rec in pulled_back_matrices
        ),
        "closed_form_rule": (
            "reduced iff invariant under some affine involution (det=2, order=2) "
            "with z-map in {(1,0),(2,0),(2,1)}; matched involution linear parts "
            "are GL(2,3)-conjugate to diag(-1,1)"
        ),
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(
        f"Wrote {args.out_json} | mismatches={len(mismatches)} | "
        f"equivalent={len(mismatches)==0} | matrix_count={len(pulled_back_matrices)}"
    )


if __name__ == "__main__":
    main()
