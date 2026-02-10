#!/usr/bin/env python3
"""Exhaustively enumerate all size-k minimal full-sign obstruction certificates.

This is a standalone script to avoid worker/pickling complexities. It is intended
for single-machine runs and prints progress periodically.
"""
from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze
from tools.enumerate_minimal_certificates import (
    build_reject_masks,
    canonicalize_via_orbit,
)


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
        / "e6_f3_trilinear_min_cert_enumeration_hessian_exhaustive.json",
    )
    p.add_argument("--progress-interval", type=int, default=100000)
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

    witnesses, reject_masks_by_witness, full_cover_mask = build_reject_masks(
        lines, sign_field, mats
    )
    n = len(witnesses)

    found = {}
    tried = 0
    covers = 0
    print(
        f"Enumerating C({n},{k}) combos; will check for cover of universe mask of size {full_cover_mask.bit_length()} bits"
    )

    suffix_or = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        suffix_or[i] = suffix_or[i + 1] | reject_masks_by_witness[i]

    total_combos = 0
    for comb in combinations(range(n), k):
        total_combos += 1
        # quick prune using suffix_or: OR of comb+suffix must be full_cover_mask
        # but simple check: if suffix_or[comb[0]] != full_cover_mask, skip
        if suffix_or[comb[0]] != full_cover_mask:
            continue
        cov = 0
        for idx in comb:
            cov |= reject_masks_by_witness[idx]
            if cov == full_cover_mask:
                break
        tried += 1
        if cov != full_cover_mask:
            continue
        covers += 1
        rows = []
        for idx in comb:
            line, z = witnesses[idx]
            sign = int(sign_field[(line, z)])
            rows.append(
                {
                    "line": [[int(p[0]), int(p[1])] for p in line],
                    "z": int(z),
                    "sign_pm1": sign,
                    "line_type": analyze._line_equation_type(line)[0],
                }
            )
        canon, _ = canonicalize_via_orbit(rows)
        found[canon] = found.get(canon, 0) + 1
        if total_combos % args.progress_interval == 0:
            print(
                f"checked {total_combos} combos, tried {tried}, covers {covers}, distinct_reps={len(found)}"
            )

    out = {
        "status": "ok",
        "candidate_space": args.candidate_space,
        "k_min": k,
        "total_combinations_checked": total_combos,
        "combinations_tried_after_pruning": tried,
        "combinations_that_cover": covers,
        "distinct_canonical_representatives_found": len(found),
        "representatives": [
            {
                "canonical_repr": [
                    {
                        "line": [list(p) for p in item[0]],
                        "z": int(item[1]),
                        "sign": int(item[2]),
                        "line_type": item[3],
                    }
                    for item in canon
                ]
            }
            for canon in found.keys()
        ],
        "counts": {"repr_count": {str(c): int(v) for c, v in found.items()}},
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(
        f"Wrote {args.out_json} (found {len(found)} distinct canonical reps, covers={covers} of tried={tried})"
    )


if __name__ == "__main__":
    main()
