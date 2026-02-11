#!/usr/bin/env python3
"""Bridge Vogel-hit arithmetic with s12 and min-cert motif outputs.

This analysis is intentionally heuristic. It computes reproducible numeric
resonances across already-verified artifacts and reports exact equalities or
near misses without promoting them to theorem status.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _repo_rel(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT.resolve()))
    except ValueError:
        return str(resolved)


def _safe_int_list(values: list[Any]) -> list[int]:
    out: list[int] = []
    for raw in values:
        try:
            out.append(int(str(raw)))
        except ValueError:
            continue
    return out


def _a_family_rank_from_total_dim(total_dim: int) -> int | None:
    n2 = int(total_dim) + 1
    if n2 <= 0:
        return None
    root = math.isqrt(n2)
    if root * root != n2 or root < 2:
        return None
    return int(root - 1)


def _is_power_of_two(value: int) -> bool:
    return value > 0 and (value & (value - 1)) == 0


def _nearest_hit_rows(
    target_dim: int,
    positive_hit_dims: list[int],
    rows: dict[str, Any],
    neighbors: int,
) -> list[dict[str, Any]]:
    nearest = sorted(positive_hit_dims, key=lambda d: (abs(d - target_dim), d))[
        : int(neighbors)
    ]
    out: list[dict[str, Any]] = []
    for hit_dim in nearest:
        row = dict(rows.get(str(int(hit_dim)), {}))
        integral_roots = _safe_int_list(list(row.get("integral_roots", [])))
        out.append(
            {
                "hit_dim": int(hit_dim),
                "gap_signed": int(hit_dim - target_dim),
                "gap_abs": int(abs(hit_dim - target_dim)),
                "roots": list(row.get("roots", [])),
                "integral_roots": list(row.get("integral_roots", [])),
                "integral_roots_int": integral_roots,
                "has_classical_hit": bool(row.get("has_classical_hit", False)),
                "classical_hits": dict(row.get("classical_hits", {})),
                "has_direct_table_hit": bool(row.get("has_direct_table_hit", False)),
                "direct_table_hits": list(row.get("direct_table_hits", [])),
            }
        )
    return out


def _collect_orbit_sizes(min_cert_summary: dict[str, Any]) -> list[int]:
    out: set[int] = set()
    for run in list(min_cert_summary.get("runs", [])):
        raw_hist = dict(run.get("orbit_histograms", {}).get("raw", {}))
        for key in raw_hist.keys():
            try:
                out.add(int(str(key)))
            except ValueError:
                continue
    return sorted(out)


def build_report(
    s12_report_json: Path,
    vogel_crosswalk_json: Path,
    min_cert_summary_json: Path,
    nearest_neighbors: int = 3,
) -> dict[str, Any]:
    s12 = _load_json(s12_report_json)
    crosswalk = _load_json(vogel_crosswalk_json)
    min_cert = _load_json(min_cert_summary_json)

    dims = dict(s12.get("algebra_dimensions", {}))
    laws = dict(s12.get("universal_grade_laws", {}))
    positive_hits = [int(v) for v in list(crosswalk.get("positive_hit_dims", []))]
    rows = dict(crosswalk.get("rows", {}))

    target_dims = {
        "grade0": int(dims.get("grade0", 0)),
        "quotient_by_grade0": int(dims.get("quotient_by_grade0", 0)),
        "total_nonzero": int(dims.get("total_nonzero", 0)),
    }
    nearest_map: dict[str, Any] = {}
    for label, dim in target_dims.items():
        neighbors = _nearest_hit_rows(
            target_dim=dim,
            positive_hit_dims=positive_hits,
            rows=rows,
            neighbors=int(nearest_neighbors),
        )
        nearest_map[label] = {
            "target_dim": int(dim),
            "nearest_hits": neighbors,
            "nearest": neighbors[0] if neighbors else None,
        }

    a_rank = _a_family_rank_from_total_dim(target_dims["total_nonzero"])
    jacobi_failure_count = int(laws.get("jacobi_failure_count", 0))
    checked_grade_triples = int(laws.get("checked_grade_triples", 0))
    nonzero_grade_count = int(
        sum(1 for key in ("grade1", "grade2") if int(dims.get(key, 0)) > 0)
    )

    grade0_gap_abs = int(nearest_map["grade0"]["nearest"]["gap_abs"])
    quotient_gap_abs = int(nearest_map["quotient_by_grade0"]["nearest"]["gap_abs"])
    total_gap_abs = int(nearest_map["total_nonzero"]["nearest"]["gap_abs"])
    total_nearest_integral_roots = list(
        nearest_map["total_nonzero"]["nearest"].get("integral_roots_int", [])
    )
    grade0_direct_hits = list(
        nearest_map["grade0"]["nearest"].get("direct_table_hits", [])
    )

    g1 = int(dims.get("grade1", 0))
    r_squared = None
    r = None
    if g1 > 0 and g1 % 3 == 0:
        candidate = g1 // 3
        root = math.isqrt(candidate)
        if root * root == candidate:
            r_squared = int(candidate)
            r = int(root)

    orbit_sizes = _collect_orbit_sizes(min_cert)
    orbit_rows = []
    for orbit_size in orbit_sizes:
        if r_squared and orbit_size % r_squared == 0:
            factor = int(orbit_size // r_squared)
            factor_power = _is_power_of_two(factor)
        else:
            factor = None
            factor_power = False
        orbit_rows.append(
            {
                "orbit_size": int(orbit_size),
                "multiple_of_r_squared": bool(
                    r_squared is not None and orbit_size % r_squared == 0
                ),
                "factor_over_r_squared": factor,
                "factor_is_power_of_two": bool(factor_power),
            }
        )

    all_orbits_multiple = bool(
        orbit_rows and all(bool(row["multiple_of_r_squared"]) for row in orbit_rows)
    )
    all_integer_factors_power_two = bool(
        orbit_rows
        and all(
            bool(row["factor_is_power_of_two"])
            for row in orbit_rows
            if row["factor_over_r_squared"] is not None
        )
    )

    resonance_checks = {
        "grade0_gap_abs_equals_jacobi_failure_count": bool(
            grade0_gap_abs == jacobi_failure_count
        ),
        "quotient_gap_abs_equals_nonzero_grade_count": bool(
            quotient_gap_abs == nonzero_grade_count
        ),
        "total_gap_abs_equals_2x_checked_grade_triples": bool(
            total_gap_abs == 2 * checked_grade_triples
        ),
        "total_nearest_integral_root_matches_a_family_rank": bool(
            a_rank is not None and int(a_rank) in total_nearest_integral_roots
        ),
        "grade0_nearest_direct_hit_contains_E8": bool("E8" in grade0_direct_hits),
    }

    return {
        "status": "ok",
        "generated_utc": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "sources": {
            "s12_report_json": _repo_rel(s12_report_json),
            "vogel_crosswalk_json": _repo_rel(vogel_crosswalk_json),
            "min_cert_summary_json": _repo_rel(min_cert_summary_json),
        },
        "target_nearest_vogel_hits": nearest_map,
        "s12_counts": {
            "jacobi_failure_count": jacobi_failure_count,
            "checked_grade_triples": checked_grade_triples,
            "nonzero_grade_count": nonzero_grade_count,
            "a_family_rank_from_total_dim": a_rank,
        },
        "orbit_bridge": {
            "block_size_r_from_grade1_equals_3r2": r,
            "r_squared": r_squared,
            "orbit_sizes": orbit_sizes,
            "orbit_rows": orbit_rows,
            "all_orbits_multiple_of_r_squared": all_orbits_multiple,
            "all_integer_factors_power_of_two": all_integer_factors_power_two,
        },
        "resonance_checks": resonance_checks,
        "claim": (
            "This report tracks a reproducible arithmetic-resonance profile linking "
            "s12 grade-law counts, nearest Vogel-hit gaps, and min-cert orbit-size "
            "factorization over r^2 (with r inferred from the sl_(3r) equal-block bridge)."
        ),
        "claim_holds": bool(all(resonance_checks.values())),
        "web_sources": [
            {
                "title": "Vogel universality and beyond",
                "url": "https://arxiv.org/abs/2601.01612",
                "year": 2026,
            },
            {
                "title": "Vogel's universality and the classification problem for Jacobi identities",
                "url": "https://arxiv.org/abs/2506.15280",
                "year": 2025,
            },
            {
                "title": "Classification Problem on Vogel's Plane",
                "url": "https://doi.org/10.1140/epjc/s10052-025-14943-y",
                "year": 2025,
            },
            {
                "title": "On Refined Vogel's universality",
                "url": "https://arxiv.org/abs/2504.13831",
                "year": 2025,
            },
            {
                "title": "Macdonald deformation of Vogel's universality and link hyperpolynomials",
                "url": "https://arxiv.org/abs/2505.16569",
                "year": 2025,
            },
        ],
    }


def render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Vogel Resonance Bridge (2026-02-11)")
    lines.append("")
    lines.append(
        "- Source files: s12=`{}`, Vogel crosswalk=`{}`, min-cert summary=`{}`".format(
            report["sources"]["s12_report_json"],
            report["sources"]["vogel_crosswalk_json"],
            report["sources"]["min_cert_summary_json"],
        )
    )
    lines.append(
        "- claim holds (all resonance checks true): `{}`".format(report["claim_holds"])
    )
    lines.append("")

    lines.append("## Nearest Vogel Hits")
    lines.append("")
    for label, row in report.get("target_nearest_vogel_hits", {}).items():
        nearest = row.get("nearest") or {}
        lines.append(
            "- `{}` target `{}` -> nearest hit `{}` (gap `{:+d}`), direct hits `{}`, integral roots `{}`".format(
                label,
                row.get("target_dim"),
                nearest.get("hit_dim"),
                int(nearest.get("gap_signed", 0)),
                nearest.get("direct_table_hits", []),
                nearest.get("integral_roots", []),
            )
        )
    lines.append("")

    counts = report.get("s12_counts", {})
    lines.append("## Count Resonances")
    lines.append("")
    lines.append(
        "- Jacobi failure count: `{}`".format(counts.get("jacobi_failure_count"))
    )
    lines.append(
        "- Nonzero grade count: `{}`".format(counts.get("nonzero_grade_count"))
    )
    lines.append(
        "- Checked grade triples: `{}`".format(counts.get("checked_grade_triples"))
    )
    lines.append(
        "- A-family rank from total dim: `A_{}`".format(
            counts.get("a_family_rank_from_total_dim")
        )
    )
    lines.append("")
    for key, value in report.get("resonance_checks", {}).items():
        lines.append("- {}: `{}`".format(key, value))
    lines.append("")

    orbit = report.get("orbit_bridge", {})
    lines.append("## Orbit Factorization")
    lines.append("")
    lines.append(
        "- `r` from `grade1=3r^2`: `{}`; `r^2`: `{}`".format(
            orbit.get("block_size_r_from_grade1_equals_3r2"),
            orbit.get("r_squared"),
        )
    )
    lines.append("- Orbit sizes: `{}`".format(orbit.get("orbit_sizes", [])))
    lines.append(
        "- all orbits multiple of `r^2`: `{}`".format(
            orbit.get("all_orbits_multiple_of_r_squared")
        )
    )
    lines.append(
        "- all integer factors power-of-two: `{}`".format(
            orbit.get("all_integer_factors_power_of_two")
        )
    )
    for row in orbit.get("orbit_rows", []):
        lines.append(
            "- orbit `{}` -> factor `{}` over `r^2`, power-of-two `{}`".format(
                row["orbit_size"],
                row["factor_over_r_squared"],
                row["factor_is_power_of_two"],
            )
        )
    lines.append("")

    lines.append("## Sources")
    lines.append("")
    for src in report.get("web_sources", []):
        lines.append("- {}: [{}]({})".format(src["year"], src["title"], src["url"]))
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--s12-report-json",
        type=Path,
        default=ROOT / "artifacts" / "s12_universalization_report.json",
    )
    parser.add_argument(
        "--vogel-crosswalk-json",
        type=Path,
        default=ROOT / "artifacts" / "vogel_rational_hit_crosswalk_2026_02_11.json",
    )
    parser.add_argument(
        "--min-cert-summary-json",
        type=Path,
        default=ROOT / "artifacts" / "min_cert_census_summary.json",
    )
    parser.add_argument("--nearest-neighbors", type=int, default=3)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "vogel_resonance_bridge_2026_02_11.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "docs" / "VOGEL_RESONANCE_BRIDGE_2026_02_11.md",
    )
    args = parser.parse_args()

    report = build_report(
        s12_report_json=args.s12_report_json,
        vogel_crosswalk_json=args.vogel_crosswalk_json,
        min_cert_summary_json=args.min_cert_summary_json,
        nearest_neighbors=max(1, int(args.nearest_neighbors)),
    )

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_md(report), encoding="utf-8")

    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
