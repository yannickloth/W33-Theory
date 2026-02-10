#!/usr/bin/env python3
"""
Compatibility wrapper for exhaustive minimal-certificate enumeration.

This script delegates to the shared exact search in
`tools/enumerate_minimal_certificates.py` and emits exhaustive-oriented field
names used by prior artifacts.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze
import tools.enumerate_minimal_certificates as enum


def _rows_from_reps(representative_counts: dict[tuple, int]) -> list[dict]:
    rows: list[dict] = []
    for canonical_tuple, hit_count in sorted(
        representative_counts.items(), key=lambda item: (-item[1], item[0])
    ):
        rows.append(
            {
                "hit_count": int(hit_count),
                "canonical_repr": enum.canonical_tuple_to_json(canonical_tuple),
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in-json", type=Path, required=True)
    parser.add_argument(
        "--candidate-space", type=str, choices=("hessian", "agl"), default="hessian"
    )
    parser.add_argument("--max-solutions", type=int, default=0)
    parser.add_argument("--time-limit-sec", type=float, default=0.0)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=ROOT
        / "artifacts"
        / "e6_f3_trilinear_min_cert_enumeration_exhaustive.json",
    )
    args = parser.parse_args()

    lines, sign_field = analyze._load_sign_field(args.in_json)
    gl = analyze._gl2_3()
    sl = [matrix for matrix in gl if matrix[4] == 1]
    matrices = sl if args.candidate_space == "hessian" else gl

    obstruction = analyze._full_sign_obstruction_certificate(
        lines, sign_field, matrices, "exhaustive-wrapper"
    )
    assert obstruction[
        "exact_min_certificate_found"
    ], "No exact minimal certificate found"
    k_min = int(obstruction["exact_min_certificate_size"])

    exact = enum.exact_min_enumeration(
        lines,
        sign_field,
        matrices,
        k_min,
        max_exact_solutions=int(args.max_solutions),
        time_limit_sec=float(args.time_limit_sec),
    )
    representative_counts = exact["found_canonical_reps"]

    output = {
        "status": "ok",
        "mode": "exact_wrapper",
        "candidate_space": args.candidate_space,
        "k_min": k_min,
        "exact_solutions_count": int(exact["exact_solutions_count"]),
        "combinations_that_cover": int(exact["exact_solutions_count"]),
        "distinct_canonical_representatives_found": int(len(representative_counts)),
        "representatives": _rows_from_reps(representative_counts),
        "search_nodes_explored": int(exact["search_nodes_explored"]),
        "truncated_by_max_solutions": bool(exact["truncated_by_max_solutions"]),
        "truncated_by_time_limit": bool(exact["truncated_by_time_limit"]),
        "limits": {
            "max_solutions": int(args.max_solutions),
            "time_limit_sec": float(args.time_limit_sec),
        },
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(
        "Wrote {} (covers={}, reps={})".format(
            args.out_json,
            output["combinations_that_cover"],
            output["distinct_canonical_representatives_found"],
        )
    )


if __name__ == "__main__":
    main()
