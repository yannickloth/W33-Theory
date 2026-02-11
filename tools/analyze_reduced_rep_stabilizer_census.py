#!/usr/bin/env python3
"""Census stabilizers for reduced-orbit (1296) minimal-certificate representatives.

This is a targeted group/graph bridge:
- reduced reps have stabilizer size 2 under the 2592-element action
  (AGL(2,3) on points) x (Aff(Z3) on z),
- the unique nontrivial stabilizer is an order-2 element (affine involution + z-map).

We restrict search to the order-2 subset:
- AGL det=2 involutions (36 elements),
- z maps of order dividing 2 (identity + three involutions).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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
        out.append(
            (
                line,
                int(w.get("z", 0)),
                int(w.get("sign_pm1", 1)),
                ltype,
            )
        )
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


def _fixed_point_line_type(
    elem: tuple[tuple[int, int, int, int, int], tuple[int, int]],
) -> str:
    points = [(x, y) for x in range(3) for y in range(3)]
    mat, shift = elem
    fixed = tuple(sorted(p for p in points if analyze._map_point(mat, shift, p) == p))
    return str(analyze._line_equation_type(fixed)[0])


def build_report(in_json: Path) -> dict[str, Any]:
    payload = _load_json(in_json)
    representatives = list(payload.get("representatives", []))
    reduced = [r for r in representatives if int(r.get("orbit_size", 0)) == 1296]

    points = [(x, y) for x in range(3) for y in range(3)]
    agl = [(m, s) for m in analyze._gl2_3() for s in points]
    agl_involutions = [
        e for e in agl if int(e[0][4]) == 2 and analyze._affine_order(e) == 2
    ]
    z_order2 = [(1, 0), (2, 0), (2, 1), (2, 2)]

    z_hist = Counter()
    fixed_row_hist = Counter()
    unique_lines_hist = Counter()
    full_z_line_hist = Counter()
    fixed_point_line_type_hist = Counter()
    z_vs_fixed_rows = Counter()
    z_vs_unique_lines = Counter()
    stabilizer_found_count_hist = Counter()

    # Track which stabilizer elements appear (canonical rep order biases this).
    stabilizer_affine_hist = Counter()

    for rec in reduced:
        rep = list(rec.get("canonical_orbit_rep", []))
        canon = _canonicalize_rep(rep)

        found: list[
            tuple[
                tuple[tuple[int, int, int, int, int], tuple[int, int]], tuple[int, int]
            ]
        ] = []
        for elem in agl_involutions:
            for z_map in z_order2:
                if _act_on_rep(rep, elem, z_map) == canon:
                    found.append((elem, z_map))

        stabilizer_found_count_hist[int(len(found))] += 1
        if len(found) != 1:
            continue

        elem, z_map = found[0]
        z_hist[z_map] += 1
        stabilizer_affine_hist[(elem[0], elem[1])] += 1

        # Fixed witness rows under the full stabilizer element (order 2).
        fixed_rows = sum(1 for row in canon if _apply_row(row, elem, z_map) == row)
        fixed_row_hist[int(fixed_rows)] += 1

        unique_lines = int(rec.get("geotype", {}).get("unique_lines_count", 0))
        has_full_z_line = bool(rec.get("geotype", {}).get("has_full_z_line", False))
        unique_lines_hist[unique_lines] += 1
        full_z_line_hist[int(has_full_z_line)] += 1

        fixed_line_type = _fixed_point_line_type(elem)
        fixed_point_line_type_hist[fixed_line_type] += 1

        z_vs_fixed_rows[(z_map, int(fixed_rows))] += 1
        z_vs_unique_lines[(z_map, int(unique_lines))] += 1

    z_hist_norm = {str(list(k)): int(v) for k, v in sorted(z_hist.items())}
    checks = {
        "reduced_rep_count_is_55": bool(len(reduced) == 55),
        "all_reduced_reps_have_unique_stabilizer": bool(
            stabilizer_found_count_hist == Counter({1: len(reduced)})
        ),
        "zmap_22_absent": bool(z_hist.get((2, 2), 0) == 0),
        "zmap_support_subset_expected": bool(
            set(z_hist.keys()).issubset({(1, 0), (2, 0), (2, 1)})
        ),
        "fixed_row_counts_are_odd": bool(
            all(int(k) % 2 == 1 for k in fixed_row_hist.keys())
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
            str(k): int(v) for k, v in sorted(stabilizer_found_count_hist.items())
        },
        "z_map_histogram": z_hist_norm,
        "fixed_witness_row_count_histogram": {
            str(k): int(v) for k, v in sorted(fixed_row_hist.items())
        },
        "geotype": {
            "unique_lines_count_histogram": {
                str(k): int(v) for k, v in sorted(unique_lines_hist.items())
            },
            "has_full_z_line_histogram": {
                "false": int(full_z_line_hist.get(0, 0)),
                "true": int(full_z_line_hist.get(1, 0)),
            },
        },
        "fixed_point_line_type_histogram": {
            str(k): int(v) for k, v in sorted(fixed_point_line_type_hist.items())
        },
        "cross_tabs": {
            "z_map_vs_fixed_witness_rows": {
                str([list(k[0]), k[1]]): int(v)
                for k, v in sorted(z_vs_fixed_rows.items())
            },
            "z_map_vs_unique_lines_count": {
                str([list(k[0]), k[1]]): int(v)
                for k, v in sorted(z_vs_unique_lines.items())
            },
        },
        "stabilizer_affine_distinct_count": int(len(stabilizer_affine_hist)),
        "claim_checks": checks,
        "claim": (
            "Each reduced-orbit representative (orbit 1296) has exactly one nontrivial "
            "order-2 stabilizer in the restricted search (AGL det=2 involutions x z-order-2 maps); "
            "the observed z-map support excludes (2,2) and fixed witness-row counts are always odd."
        ),
        "claim_holds": bool(all(checks.values())),
    }


def render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Reduced-Rep Stabilizer Census (2026-02-11)")
    lines.append("")
    lines.append(f"- source: `{report['source_json']}`")
    lines.append(f"- reduced reps: `{report['reduced_rep_count']}`")
    lines.append(f"- search space: `{report['search_space']}`")
    lines.append(f"- claim holds: `{report['claim_holds']}`")
    lines.append("")
    lines.append("## Stabilizers")
    lines.append("")
    lines.append(f"- z-map histogram: `{report['z_map_histogram']}`")
    lines.append(
        "- fixed witness-row histogram: "
        f"`{report['fixed_witness_row_count_histogram']}`"
    )
    lines.append(
        f"- fixed-point line type histogram: `{report['fixed_point_line_type_histogram']}`"
    )
    lines.append("")
    lines.append("## Geotype")
    lines.append("")
    lines.append(
        "- unique-lines histogram: "
        f"`{report['geotype']['unique_lines_count_histogram']}`"
    )
    lines.append(
        f"- has-full-z-line histogram: `{report['geotype']['has_full_z_line_histogram']}`"
    )
    lines.append("")
    lines.append("## Cross Tabs")
    lines.append("")
    lines.append(
        "- z-map vs fixed rows: "
        f"`{report['cross_tabs']['z_map_vs_fixed_witness_rows']}`"
    )
    lines.append(
        "- z-map vs unique lines: "
        f"`{report['cross_tabs']['z_map_vs_unique_lines_count']}`"
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
        default=ROOT / "artifacts" / "reduced_rep_stabilizer_census_2026_02_11.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "docs" / "REDUCED_REP_STABILIZER_CENSUS_2026_02_11.md",
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
