#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _hist_int(hist: dict[str, Any], key: int) -> int:
    return _safe_int(hist.get(str(key), 0))


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return float(numerator) / float(denominator)


def _orbit_histograms(payload: dict[str, Any]) -> tuple[dict[int, int], dict[int, int]]:
    orbit_hist: dict[int, int] = {}
    weighted_orbit_hist: dict[int, int] = {}
    for row in payload.get("representatives", []):
        orbit_size = _safe_int(row.get("orbit_size"), 0)
        if orbit_size <= 0:
            continue
        hit_count = _safe_int(row.get("hit_count"), 1)
        orbit_hist[orbit_size] = orbit_hist.get(orbit_size, 0) + 1
        weighted_orbit_hist[orbit_size] = (
            weighted_orbit_hist.get(orbit_size, 0) + hit_count
        )
    return orbit_hist, weighted_orbit_hist


def _stabilizer_histogram(
    orbit_hist: dict[int, int], action_orbit_ceiling: int
) -> dict[int, int]:
    out: dict[int, int] = {}
    if action_orbit_ceiling <= 0:
        return out
    for orbit_size, count in orbit_hist.items():
        if orbit_size > 0 and action_orbit_ceiling % orbit_size == 0:
            stabilizer_size = action_orbit_ceiling // orbit_size
            out[stabilizer_size] = out.get(stabilizer_size, 0) + int(count)
    return out


def build_report(hessian: dict[str, Any], agl: dict[str, Any]) -> dict[str, Any]:
    h_source = hessian.get("source", {})
    a_source = agl.get("source", {})
    h_aggregate = hessian.get("aggregate", {})
    a_aggregate = agl.get("aggregate", {})

    h_total = _safe_int(hessian.get("total_representatives"), 0)
    a_total = _safe_int(agl.get("total_representatives"), 0)

    h_exact = _safe_int(h_source.get("exact_solutions_count"), 0)
    a_exact = _safe_int(a_source.get("exact_solutions_count"), 0)

    h_family_hist = h_aggregate.get("striation_family_count_hist", {})
    a_family_hist = a_aggregate.get("striation_family_count_hist", {})
    h_unique_lines_hist = h_aggregate.get("unique_lines_count_hist", {})
    a_unique_lines_hist = a_aggregate.get("unique_lines_count_hist", {})

    h_full_z = _safe_int(h_aggregate.get("has_full_z_line_count"), 0)
    a_full_z = _safe_int(a_aggregate.get("has_full_z_line_count"), 0)
    h_orbit_hist, h_weighted_orbit_hist = _orbit_histograms(hessian)
    a_orbit_hist, a_weighted_orbit_hist = _orbit_histograms(agl)
    action_orbit_ceiling = 0
    if h_orbit_hist or a_orbit_hist:
        action_orbit_ceiling = max(
            ([0] + list(h_orbit_hist.keys()) + list(a_orbit_hist.keys()))
        )
    h_stabilizer_hist = _stabilizer_histogram(h_orbit_hist, action_orbit_ceiling)
    a_stabilizer_hist = _stabilizer_histogram(a_orbit_hist, action_orbit_ceiling)
    h_reduced = sum(
        count
        for orbit_size, count in h_orbit_hist.items()
        if orbit_size < action_orbit_ceiling
    )
    a_reduced = sum(
        count
        for orbit_size, count in a_orbit_hist.items()
        if orbit_size < action_orbit_ceiling
    )

    comparison = {
        "hessian_representatives": h_total,
        "agl_representatives": a_total,
        "hessian_exact_covering_combinations": h_exact,
        "agl_exact_covering_combinations": a_exact,
        "representative_ratio_hessian_over_agl": (
            float(h_total) / float(a_total) if a_total > 0 else None
        ),
        "covering_combination_ratio_hessian_over_agl": (
            float(h_exact) / float(a_exact) if a_exact > 0 else None
        ),
        "hessian_full_striation_reps": _hist_int(h_family_hist, 4),
        "agl_full_striation_reps": _hist_int(a_family_hist, 4),
        "hessian_full_striation_rep_rate": _ratio(_hist_int(h_family_hist, 4), h_total),
        "agl_full_striation_rep_rate": _ratio(_hist_int(a_family_hist, 4), a_total),
        "hessian_two_striation_reps": _hist_int(h_family_hist, 2),
        "agl_two_striation_reps": _hist_int(a_family_hist, 2),
        "hessian_four_plus_unique_lines_reps": sum(
            _safe_int(count)
            for line_count, count in h_unique_lines_hist.items()
            if int(line_count) >= 4
        ),
        "agl_four_plus_unique_lines_reps": sum(
            _safe_int(count)
            for line_count, count in a_unique_lines_hist.items()
            if int(line_count) >= 4
        ),
        "hessian_has_full_z_line_count": h_full_z,
        "agl_has_full_z_line_count": a_full_z,
        "hessian_has_full_z_line_rate": _ratio(h_full_z, h_total),
        "agl_has_full_z_line_rate": _ratio(a_full_z, a_total),
        "hessian_striation_family_count_hist": h_family_hist,
        "agl_striation_family_count_hist": a_family_hist,
        "hessian_unique_lines_count_hist": h_unique_lines_hist,
        "agl_unique_lines_count_hist": a_unique_lines_hist,
        "action_orbit_ceiling": int(action_orbit_ceiling),
        "hessian_orbit_size_hist": {
            str(k): int(v) for k, v in sorted(h_orbit_hist.items())
        },
        "agl_orbit_size_hist": {
            str(k): int(v) for k, v in sorted(a_orbit_hist.items())
        },
        "hessian_weighted_orbit_size_hist": {
            str(k): int(v) for k, v in sorted(h_weighted_orbit_hist.items())
        },
        "agl_weighted_orbit_size_hist": {
            str(k): int(v) for k, v in sorted(a_weighted_orbit_hist.items())
        },
        "hessian_stabilizer_size_hist": {
            str(k): int(v) for k, v in sorted(h_stabilizer_hist.items())
        },
        "agl_stabilizer_size_hist": {
            str(k): int(v) for k, v in sorted(a_stabilizer_hist.items())
        },
        "hessian_reduced_orbit_reps": int(h_reduced),
        "agl_reduced_orbit_reps": int(a_reduced),
        "hessian_reduced_orbit_rep_rate": _ratio(h_reduced, h_total),
        "agl_reduced_orbit_rep_rate": _ratio(a_reduced, a_total),
        "hessian_has_reduced_orbit_layer": bool(h_reduced > 0),
        "agl_all_full_orbit": bool(a_reduced == 0 and a_total > 0),
    }
    return {"status": "ok", "comparison": comparison}


def to_markdown(report: dict[str, Any], hessian_path: Path, agl_path: Path) -> str:
    comparison = report["comparison"]
    lines = [
        "# Minimal-Certificate Census Report",
        "",
        f"- Hessian input: `{hessian_path}`",
        f"- AGL input: `{agl_path}`",
        "",
        "## Headline",
        "",
        "- Hessian canonical representatives: "
        f"`{comparison['hessian_representatives']}`",
        "- AGL canonical representatives: " f"`{comparison['agl_representatives']}`",
        "- Representative ratio Hessian/AGL: "
        f"`{comparison['representative_ratio_hessian_over_agl']}`",
        "- Hessian exact covering combinations: "
        f"`{comparison['hessian_exact_covering_combinations']}`",
        "- AGL exact covering combinations: "
        f"`{comparison['agl_exact_covering_combinations']}`",
        "- Covering-combination ratio Hessian/AGL: "
        f"`{comparison['covering_combination_ratio_hessian_over_agl']}`",
        "",
        "## Geometry Split",
        "",
        "- Hessian striation-family histogram: "
        f"`{comparison['hessian_striation_family_count_hist']}`",
        "- AGL striation-family histogram: "
        f"`{comparison['agl_striation_family_count_hist']}`",
        "- Hessian unique-line histogram: "
        f"`{comparison['hessian_unique_lines_count_hist']}`",
        "- AGL unique-line histogram: "
        f"`{comparison['agl_unique_lines_count_hist']}`",
        "- Hessian full-z-line rate: "
        f"`{comparison['hessian_has_full_z_line_rate']}`",
        "- AGL full-z-line rate: " f"`{comparison['agl_has_full_z_line_rate']}`",
        "",
        "## Orbit Stratification",
        "",
        "- Shared action-orbit ceiling: " f"`{comparison['action_orbit_ceiling']}`",
        "- Hessian orbit-size histogram: " f"`{comparison['hessian_orbit_size_hist']}`",
        "- AGL orbit-size histogram: " f"`{comparison['agl_orbit_size_hist']}`",
        "- Hessian stabilizer-size histogram (implied): "
        f"`{comparison['hessian_stabilizer_size_hist']}`",
        "- AGL stabilizer-size histogram (implied): "
        f"`{comparison['agl_stabilizer_size_hist']}`",
        "- Hessian reduced-orbit rep rate: "
        f"`{comparison['hessian_reduced_orbit_rep_rate']}`",
        "- AGL reduced-orbit rep rate: "
        f"`{comparison['agl_reduced_orbit_rep_rate']}`",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hessian-json", type=Path, required=True)
    parser.add_argument("--agl-json", type=Path, required=True)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "e6_f3_trilinear_min_cert_census_report.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "docs" / "MIN_CERT_CENSUS_REPORT_2026_02_10.md",
    )
    args = parser.parse_args()

    hessian = _load(args.hessian_json)
    agl = _load(args.agl_json)
    report = build_report(hessian, agl)
    markdown = to_markdown(report, args.hessian_json, args.agl_json)

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    args.out_md.write_text(markdown, encoding="utf-8")
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
