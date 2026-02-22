#!/usr/bin/env python3
"""Inspect the non-identity z-map stabilizers for reduced-orbit (1296) reps.

The stabilizer census (`tools/analyze_reduced_rep_stabilizer_census.py`) shows:
  - 55 reduced reps (orbit size 1296),
  - each has a unique nontrivial stabilizer in the restricted search space
    (det=2 AGL(2,3) involutions) x (z maps of order dividing 2),
  - and the z-map support is {(1,0),(2,0),(2,1)} with (2,2) absent.

This script drills into the outliers z != (1,0), extracting:
  - the stabilizer (affine elem + z-map),
  - its "reflection" parameters (axis line + fixed striation type),
  - fixed witness rows and basic geotype.

It also cross-checks that the affine part can be reconstructed deterministically
from (axis, fixed_striation_type) using the constructive reflection map in
`tools/analyze_agl23_det2_involution_class.py`.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tools.analyze_agl23_det2_involution_class as invclass
import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _repo_rel(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT.resolve()))
    except ValueError:
        return str(resolved)


def _canonicalize_rep(rep: list[dict[str, Any]]) -> tuple[tuple[Any, ...], ...]:
    out = []
    for w in rep:
        line = tuple(sorted(tuple(p) for p in w.get("line", [])))
        ltype = str(w.get("line_type", analyze._line_equation_type(line)[0]))
        out.append((line, int(w.get("z", 0)), int(w.get("sign_pm1", 1)), ltype))
    return tuple(sorted(out))


def _act_on_rep(
    rep: list[dict[str, Any]],
    elem: tuple[tuple[int, int, int, int, int], tuple[int, int]],
    z_map: tuple[int, int],
) -> tuple[tuple[Any, ...], ...]:
    mat, shift = elem
    out = []
    for w in rep:
        mapped = tuple(
            sorted(analyze._map_point(mat, shift, tuple(p)) for p in w.get("line", []))
        )
        out.append(
            (
                mapped,
                int(analyze._map_z(z_map, int(w.get("z", 0)))),
                int(w.get("sign_pm1", 1)),
                str(analyze._line_equation_type(mapped)[0]),
            )
        )
    return tuple(sorted(out))


def _apply_row(
    row: tuple[Any, ...],
    elem: tuple[tuple[int, int, int, int, int], tuple[int, int]],
    z_map: tuple[int, int],
) -> tuple[Any, ...]:
    line, z, sign, _ltype = row
    mat, shift = elem
    mapped = tuple(sorted(analyze._map_point(mat, shift, tuple(p)) for p in line))
    return (
        mapped,
        int(analyze._map_z(z_map, int(z))),
        int(sign),
        str(analyze._line_equation_type(mapped)[0]),
    )


def _row_to_json(row: tuple[Any, ...]) -> dict[str, Any]:
    line, z, sign, ltype = row
    return {
        "line": [list(p) for p in line],
        "z": int(z),
        "sign_pm1": int(sign),
        "line_type": str(ltype),
    }


def _affine_elem_json(
    elem: tuple[tuple[int, int, int, int, int], tuple[int, int]]
) -> list[list[int]]:
    mat, shift = elem
    return [list(mat), list(shift)]


def _fixed_points(
    elem: tuple[tuple[int, int, int, int, int], tuple[int, int]],
    points: list[tuple[int, int]],
) -> list[tuple[int, int]]:
    mat, shift = elem
    return sorted(p for p in points if analyze._map_point(mat, shift, p) == p)


def _fixed_lines(
    elem: tuple[tuple[int, int, int, int, int], tuple[int, int]],
    affine_lines: list[tuple[tuple[int, int], tuple[int, int], tuple[int, int]]],
) -> list[tuple[tuple[int, int], tuple[int, int], tuple[int, int]]]:
    mat, shift = elem
    return sorted(L for L in affine_lines if analyze._map_line(mat, shift, L) == L)


def _involution_stabilizer_for_rep(
    rep: list[dict[str, Any]],
    canon: tuple[tuple[Any, ...], ...],
    agl_involutions: list[tuple[tuple[int, int, int, int, int], tuple[int, int]]],
    z_order2: list[tuple[int, int]],
) -> list[
    tuple[tuple[tuple[int, int, int, int, int], tuple[int, int]], tuple[int, int]]
]:
    found = []
    for elem in agl_involutions:
        for z_map in z_order2:
            if _act_on_rep(rep, elem, z_map) == canon:
                found.append((elem, z_map))
    return found


def build_report(in_json: Path) -> dict[str, Any]:
    payload = _load_json(in_json)
    representatives = list(payload.get("representatives", []))
    reduced = [r for r in representatives if int(r.get("orbit_size", 0)) == 1296]

    points = [(x, y) for x in range(3) for y in range(3)]
    affine_lines = list(analyze._all_affine_lines())

    agl = [(m, s) for m in analyze._gl2_3() for s in points]
    agl_involutions = [
        e for e in agl if int(e[0][4]) == 2 and analyze._affine_order(e) == 2
    ]
    z_order2 = [(1, 0), (2, 0), (2, 1), (2, 2)]

    outliers: list[dict[str, Any]] = []
    z_hist = Counter()
    stabilizer_count_hist = Counter()

    for idx, rec in enumerate(reduced):
        rep = list(rec.get("canonical_orbit_rep", []))
        canon = _canonicalize_rep(rep)
        found = _involution_stabilizer_for_rep(rep, canon, agl_involutions, z_order2)
        stabilizer_count_hist[int(len(found))] += 1
        if len(found) != 1:
            continue

        elem, z_map = found[0]
        z_hist[z_map] += 1
        if z_map == (1, 0):
            continue

        fixed_rows = [row for row in canon if _apply_row(row, elem, z_map) == row]
        fixed_points = _fixed_points(elem, points)
        fixed_lines = _fixed_lines(elem, affine_lines)

        axis_type = str(analyze._line_equation_type(tuple(fixed_points))[0])
        fixed_line_type_hist = Counter(
            str(analyze._line_equation_type(L)[0]) for L in fixed_lines
        )
        striation_types = [t for t, c in fixed_line_type_hist.items() if int(c) == 3]
        fixed_striation_type = (
            str(striation_types[0]) if len(striation_types) == 1 else None
        )

        reconstructed_ok = False
        if fixed_striation_type is not None:
            try:
                reconstructed = invclass._construct_reflection_affine(
                    fixed_points, fixed_striation_type, points, affine_lines
                )
                reconstructed_ok = bool(reconstructed == elem)
            except Exception:
                reconstructed_ok = False

        # For z-map involutions, compute which z-value is fixed.
        z_fixed = None
        if z_map[0] == 2:
            # Solve z = 2z + b mod 3 -> 2z = b -> z = 2*b mod 3 (since 2^-1 = 2).
            z_fixed = int((2 * int(z_map[1])) % 3)

        outliers.append(
            {
                "reduced_rep_index": int(idx),
                "orbit_size": int(rec.get("orbit_size", 0)),
                "witness_count": int(len(rep)),
                "geotype": {
                    "unique_lines_count": int(
                        rec.get("geotype", {}).get("unique_lines_count", 0)
                    ),
                    "has_full_z_line": bool(
                        rec.get("geotype", {}).get("has_full_z_line", False)
                    ),
                },
                "stabilizer": {
                    "affine_elem": _affine_elem_json(elem),
                    "z_map": list(z_map),
                    "z_fixed": z_fixed,
                    "axis_fixed_points": [list(p) for p in fixed_points],
                    "axis_type": axis_type,
                    "fixed_line_type_histogram": {
                        str(k): int(v) for k, v in sorted(fixed_line_type_hist.items())
                    },
                    "fixed_striation_type": fixed_striation_type,
                    "reconstruction_matches": bool(reconstructed_ok),
                },
                "canonical_rep": [_row_to_json(row) for row in canon],
                "fixed_rows": [_row_to_json(row) for row in fixed_rows],
            }
        )

    z_hist_norm = {str(list(k)): int(v) for k, v in sorted(z_hist.items())}
    z_outlier_hist = Counter(tuple(o["stabilizer"]["z_map"]) for o in outliers)
    z_outlier_hist_norm = {
        str(list(k)): int(v) for k, v in sorted(z_outlier_hist.items())
    }

    checks = {
        "reduced_rep_count_is_55": bool(len(reduced) == 55),
        "restricted_unique_stabilizer_holds": bool(
            stabilizer_count_hist == Counter({1: len(reduced)})
        ),
        "z_map_support_excludes_22": bool(z_hist.get((2, 2), 0) == 0),
        "outlier_counts_match_census": bool(
            z_outlier_hist == Counter({(2, 0): 5, (2, 1): 1})
        ),
        "all_outliers_reconstruct": bool(
            all(o["stabilizer"]["reconstruction_matches"] for o in outliers)
        ),
        "all_outliers_have_fixed_row": bool(
            all(len(o["fixed_rows"]) >= 1 for o in outliers)
        ),
        "all_outliers_fixed_rows_have_z_fixed": bool(
            all(
                (o["stabilizer"]["z_fixed"] is None)
                or all(
                    int(r["z"]) == int(o["stabilizer"]["z_fixed"])
                    for r in o["fixed_rows"]
                )
                for o in outliers
            )
        ),
    }

    return {
        "status": "ok",
        "generated_utc": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "source_json": _repo_rel(in_json),
        "search_space": {
            "agl_involution_count": int(len(agl_involutions)),
            "z_order2_count": int(len(z_order2)),
        },
        "reduced_rep_count": int(len(reduced)),
        "stabilizer_found_count_histogram": {
            str(k): int(v) for k, v in sorted(stabilizer_count_hist.items())
        },
        "z_map_histogram_all_reduced": z_hist_norm,
        "outlier_z_map_histogram": z_outlier_hist_norm,
        "outliers": outliers,
        "claim_checks": checks,
        "claim": (
            "All reduced-orbit reps (orbit 1296) have a unique order-2 stabilizer in the "
            "restricted search; among the z-order-2 maps, only z=(2,0) and z=(2,1) occur "
            "as non-identity stabilizers (5 and 1 times, respectively), and z=(2,2) is absent. "
            "Each outlier affine stabilizer is a det=2 reflection and is reconstructible "
            "from its axis line and fixed striation type."
        ),
        "claim_holds": bool(all(checks.values())),
    }


def render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Reduced-Rep Stabilizer Outliers (2026-02-11)")
    lines.append("")
    lines.append(f"- source: `{report['source_json']}`")
    lines.append(f"- reduced reps: `{report['reduced_rep_count']}`")
    lines.append(f"- claim holds: `{report['claim_holds']}`")
    lines.append("")
    lines.append("## z-Map Support")
    lines.append("")
    lines.append(f"- all reduced reps: `{report['z_map_histogram_all_reduced']}`")
    lines.append(f"- outliers only: `{report['outlier_z_map_histogram']}`")
    lines.append("")
    lines.append("## Outliers (Non-Identity z)")
    lines.append("")
    for o in report.get("outliers", []):
        stab = o["stabilizer"]
        lines.append(
            f"- rep#{o['reduced_rep_index']}: z={stab['z_map']}, "
            f"axis={stab['axis_fixed_points']} ({stab['axis_type']}), "
            f"fixed_striation={stab['fixed_striation_type']}, "
            f"fixed_rows={len(o['fixed_rows'])}, "
            f"geotype(unique_lines={o['geotype']['unique_lines_count']}, "
            f"full_z_line={o['geotype']['has_full_z_line']})"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--in-json",
        type=Path,
        default=ROOT
        / "committed_artifacts"
        / "min_cert_census_medium_2026_02_10"
        / "e6_f3_trilinear_min_cert_exact_hessian_full_with_geotypes.json",
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "reduced_rep_stabilizer_outliers_2026_02_11.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "docs" / "REDUCED_REP_STABILIZER_OUTLIERS_2026_02_11.md",
    )
    args = parser.parse_args()

    report = build_report(args.in_json)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_md(report), encoding="utf-8")
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
