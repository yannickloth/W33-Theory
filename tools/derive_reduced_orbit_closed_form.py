#!/usr/bin/env python3
"""Derive candidate closed-form rules for the reduced (1296) Hessian orbit class.

This script analyzes classified minimal-certificate representatives from a
Hessian exhaustive classification, locates involutive symmetries that fix
reduced-orbit representatives, and summarizes the fixed/swapped line patterns
and z-map statistics to propose a compact rule description.

Outputs a JSON summary intended for human inspection and a short markdown
snippet noting the candidate closed-form description.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
Z_INVOLUTIONS = [(1, 0), (2, 0), (2, 1)]
FULL_ORBIT = 2592


def _pack_witnesses(rows: List[Dict[str, Any]]) -> Tuple[Tuple, ...]:
    packed = []
    for row in rows:
        line = tuple(sorted((int(p[0]), int(p[1])) for p in row["line"]))
        z = int(row.get("z", 0))
        sign = int(row.get("sign_pm1", row.get("sign", 1)))
        packed.append((line, z, sign))
    return tuple(sorted(packed))


def _candidate_affine_involutions():
    import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze

    pts = [(x, y) for x in range(3) for y in range(3)]
    out = []
    for mat in analyze._gl2_3():
        for shift in pts:
            elem = (mat, shift)
            if mat[4] == 2 and analyze._affine_order(elem) == 2:
                out.append(elem)
    return sorted(out)


def _transform(packed, affine_elem, z_map):
    import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze

    mat, shift = affine_elem
    out = []
    for line, z, sign in packed:
        mapped_line = tuple(sorted(analyze._map_point(mat, shift, p) for p in line))
        mapped_z = int(analyze._map_z(z_map, int(z)))
        out.append((mapped_line, mapped_z, int(sign)))
    return tuple(sorted(out))


def analyze_hessian_classified(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    reps = payload.get("representatives", [])

    involutions = _candidate_affine_involutions()

    summary = {
        "status": "ok",
        "source": str(path),
        "full_orbit_size": FULL_ORBIT,
        "representative_count": len(reps),
        "reduced_representative_count": 0,
        "matched_by_involution_count": 0,
        "involution_match_z_map_hist": {},
        "fixed_line_type_hist": {},
        "fixed_line_count_hist": {},
        "swapped_pair_type_hist": {},
        "examples": [],
    }

    z_hist = Counter()
    fixed_type_hist = Counter()
    fixed_count_hist = Counter()
    swapped_pair_type_hist = Counter()
    matched_count = 0
    reduced_count = 0

    for idx, entry in enumerate(reps):
        rows = entry.get("canonical_repr") or []
        packed = _pack_witnesses(rows)
        orbit_size = int(entry.get("orbit_size", FULL_ORBIT))
        is_reduced = orbit_size < FULL_ORBIT
        if is_reduced:
            reduced_count += 1

        matches = []
        for affine_elem in involutions:
            for z_map in Z_INVOLUTIONS:
                if _transform(packed, affine_elem, z_map) == packed:
                    matches.append((affine_elem, z_map))

        if matches:
            matched_count += 1
            # pick the first match to collect structural stats
            affine_elem, z_map = sorted(matches)[0]
            z_hist[str(tuple(int(v) for v in z_map))] += 1

            # compute fixed lines and swapped pairs
            mat, shift = affine_elem
            import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze

            fixed_lines = []
            swapped_pairs = []
            mapped = {}
            for line, z, sign in packed:
                mapped_line = tuple(
                    sorted(analyze._map_point(mat, shift, p) for p in line)
                )
                mapped[(line, z, sign)] = (
                    mapped_line,
                    int(analyze._map_z(z_map, z)),
                    sign,
                )
            # group by lines under affine elem
            line_map = {}
            for line, z, sign in packed:
                mapped_line = tuple(
                    sorted(analyze._map_point(mat, shift, p) for p in line)
                )
                line_map.setdefault(line, set()).add(mapped_line)
            # fixed lines are those where the image line equals itself (for some representative rows)
            lines_fixed = set()
            for line, z, sign in packed:
                mapped_line = tuple(
                    sorted(analyze._map_point(mat, shift, p) for p in line)
                )
                if mapped_line == line:
                    lines_fixed.add(line)
            fixed_count_hist[len(lines_fixed)] += 1
            for L in lines_fixed:
                # classify line type
                lt = analyze._line_equation_type(L)[0]
                fixed_type_hist[lt] += 1

            # swapped pairs: lines where mapped_line != line, record (type(type))
            swapped = []
            for line, z, sign in packed:
                mapped_line = tuple(
                    sorted(analyze._map_point(mat, shift, p) for p in line)
                )
                if mapped_line != line:
                    lt1 = analyze._line_equation_type(line)[0]
                    lt2 = analyze._line_equation_type(mapped_line)[0]
                    swapped.append((lt1, lt2))
            for a, b in swapped:
                swapped_pair_type_hist[f"{a}<-{b}"] += 1

            if len(summary["examples"]) < 4:
                summary["examples"].append(
                    {
                        "index": idx,
                        "orbit_size": orbit_size,
                        "z_map": list(z_map),
                        "fixed_line_count": len(lines_fixed),
                        "fixed_line_types_sample": list(sorted(fixed_type_hist.keys()))[
                            :3
                        ],
                    }
                )

    summary["reduced_representative_count"] = int(reduced_count)
    summary["matched_by_involution_count"] = int(matched_count)
    summary["involution_match_z_map_hist"] = dict(z_hist)
    summary["fixed_line_type_hist"] = dict(fixed_type_hist)
    summary["fixed_line_count_hist"] = dict(fixed_count_hist)
    summary["swapped_pair_type_hist"] = dict(swapped_pair_type_hist)

    # Candidate textual rule
    if matched_count == reduced_count and matched_count > 0:
        rule_text = (
            "Candidate rule: reduced orbit representatives are exactly those "
            "invariant under at least one affine involution (det=2, order=2) "
            "combined with one of the z-involutions (1,0),(2,0),(2,1)."
        )
        summary["candidate_rule"] = rule_text
        summary["rule_holds"] = True
    else:
        summary["candidate_rule"] = (
            "No single involution-based rule detected that exactly matches all "
            "observed reduced representatives; further refinement required."
        )
        summary["rule_holds"] = False

    return summary


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--in-json",
        type=Path,
        default=ROOT
        / "committed_artifacts"
        / "min_cert_census_medium_2026_02_10"
        / "e6_f3_trilinear_min_cert_exact_hessian_full_with_geotypes.json",
    )
    p.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "e6_f3_trilinear_reduced_orbit_rule_summary.json",
    )
    p.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "docs" / "MIN_CERT_REDUCED_ORBIT_RULE_2026_02_10.md",
    )
    args = p.parse_args()

    summary = analyze_hessian_classified(args.in_json)

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "# Candidate closed-form rule: reduced 1296 Hessian orbit class",
        "",
        f"Source: {args.in_json}",
        "",
        "## Summary",
        "",
    ]
    lines.append(summary.get("candidate_rule", "(none)"))
    lines.append("")
    lines.append("## Observed statistics")
    lines.append("")
    lines.append(
        f"- reduced_representative_count: {summary['reduced_representative_count']}"
    )
    lines.append(
        f"- matched_by_involution_count: {summary['matched_by_involution_count']}"
    )
    lines.append("")
    lines.append("### z-map histogram")
    for k, v in summary.get("involution_match_z_map_hist", {}).items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("### fixed line type histogram")
    for k, v in summary.get("fixed_line_type_hist", {}).items():
        lines.append(f"- {k}: {v}")

    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {args.out_json} and {args.out_md}")


if __name__ == "__main__":
    main()
