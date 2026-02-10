#!/usr/bin/env python3
"""Exact size-k minimal-certificate enumeration wrapper.

This script uses the shared branch-and-bound exhaustive engine in
`tools/enumerate_minimal_certificates.py` and writes a standalone JSON artifact.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze
from tools.enumerate_minimal_certificates import exhaustive_enumeration


def _canon_to_json(canon):
    rows = []
    for item in canon:
        rows.append(
            {
                "line": [list(p) for p in item[0]],
                "z": int(item[1]),
                "sign": int(item[2]),
                "line_type": item[3],
            }
        )
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--in-json", type=Path, required=True)
    p.add_argument(
        "--candidate-space", type=str, choices=("hessian", "agl"), default="hessian"
    )
    p.add_argument(
        "--out-json",
        type=Path,
        default=ROOT
        / "artifacts"
        / "e6_f3_trilinear_min_cert_enumeration_hessian_exhaustive2.json",
    )
    p.add_argument(
        "--progress-interval",
        type=int,
        default=100000,
        help="Progress/checkpoint interval in checked combinations.",
    )
    p.add_argument(
        "--max-solutions",
        type=int,
        default=0,
        help="Stop after this many covering combinations (0 = no cap).",
    )
    p.add_argument(
        "--time-limit-sec",
        type=float,
        default=0.0,
        help="Stop after this wall-clock limit in seconds (0 = no limit).",
    )
    p.add_argument("--workers", type=int, default=1)
    p.add_argument("--progress", action="store_true")
    args = p.parse_args()

    lines, sign_field = analyze._load_sign_field(args.in_json)
    gl = analyze._gl2_3()
    sl = [m for m in gl if m[4] == 1]
    mats = sl if args.candidate_space == "hessian" else gl

    full_cert = analyze._full_sign_obstruction_certificate(
        lines, sign_field, mats, "exhaustive"
    )
    assert full_cert[
        "exact_min_certificate_found"
    ], "No exact minimal certificate found"
    k = int(full_cert["exact_min_certificate_size"])

    found, checked, covers, trunc_max, trunc_time = exhaustive_enumeration(
        lines,
        sign_field,
        mats,
        k,
        workers=args.workers,
        checkpoint_interval=args.progress_interval,
        out_json_path=None,
        progress=args.progress,
        max_solutions=args.max_solutions,
        time_limit_sec=args.time_limit_sec,
    )

    rep_rows = []
    for canon, count in sorted(found.items(), key=lambda kv: (-kv[1], kv[0])):
        rep_rows.append(
            {"hit_count": int(count), "canonical_repr": _canon_to_json(canon)}
        )

    out = {
        "status": "ok",
        "candidate_space": args.candidate_space,
        "k_min": k,
        "total_combinations_checked": int(checked),
        "combinations_tried_after_pruning": int(checked),
        "combinations_that_cover": int(covers),
        "distinct_canonical_representatives_found": len(found),
        "truncated_by_max_solutions": bool(trunc_max),
        "truncated_by_time_limit": bool(trunc_time),
        "max_solutions": int(args.max_solutions),
        "time_limit_sec": float(args.time_limit_sec),
        "representatives": rep_rows,
        "counts": {"repr_count": {str(c): int(v) for c, v in found.items()}},
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(
        "Wrote {} (reps={}, covers={}, checked={})".format(
            args.out_json, len(found), covers, checked
        )
    )


if __name__ == "__main__":
    main()
