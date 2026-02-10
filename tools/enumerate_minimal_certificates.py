#!/usr/bin/env python3
"""Enumerate (or sample) minimal full-sign obstruction certificates and report AGL-orbit canonical reps.

Usage:
  py -3 tools/enumerate_minimal_certificates.py --in-json artifacts/e6_f3_trilinear_map.json --candidate-space hessian --max-samples 200 --out-json artifacts/e6_f3_trilinear_min_cert_enumeration.json

Notes:
 - Uses a randomized greedy sampler to find minimal-size certificates and canonicalize them under AGL(2,3) x z-affine.
 - This is a heuristic enumerator (not exhaustive) but suitable for discovering distinct orbit types.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze


def build_witness_list(lines, sign_field):
    witnesses = []
    for line in lines:
        for z in (0, 1, 2):
            sign = int(sign_field.get((line, z), 1))
            witnesses.append(
                {
                    "line": [[int(p[0]), int(p[1])] for p in line],
                    "z": int(z),
                    "sign_pm1": int(sign),
                    "line_type": analyze._line_equation_type(line)[0],
                }
            )
    return witnesses


def build_reject_masks(lines, sign_field, mats):
    # replicate the mask building from analyzer to get reject masks per witness
    pts = [(x, y) for x in range(3) for y in range(3)]
    z_maps = [(az, bz) for az in (1, 2) for bz in range(3)]
    candidates = []
    for A in mats:
        for shift in pts:
            # ensure line map preserves the set of lines
            line_map = {line: analyze._map_line(A, shift, line) for line in lines}
            if set(line_map.values()) != set(lines):
                continue
            for z_map in z_maps:
                for eps in (1, -1):
                    candidates.append(((A, shift), z_map, int(eps), line_map))

    # identify stabilizers
    mismatch_masks_by_candidate = []
    stabilizer_indices = []
    witnesses = [(line, z) for line in lines for z in (0, 1, 2)]
    for idx, (u_map, z_map, eps, line_map) in enumerate(candidates):
        mask = 0
        for wi, (line, z) in enumerate(witnesses):
            lhs = sign_field[(line_map[line], analyze._map_z(z_map, z))]
            rhs = eps * sign_field[(line, z)]
            if lhs != rhs:
                mask |= 1 << wi
        mismatch_masks_by_candidate.append(mask)
        if mask == 0:
            stabilizer_indices.append(idx)

    non_stabilizer_indices = [
        idx for idx in range(len(candidates)) if idx not in set(stabilizer_indices)
    ]
    non_index = {idx: pos for pos, idx in enumerate(non_stabilizer_indices)}
    universe_size = len(non_stabilizer_indices)
    full_cover_mask = (1 << universe_size) - 1

    reject_masks_by_witness = [0 for _ in witnesses]
    for idx in non_stabilizer_indices:
        rej = mismatch_masks_by_candidate[idx]
        pos = non_index[idx]
        for wi in range(len(witnesses)):
            if (rej >> wi) & 1:
                reject_masks_by_witness[wi] |= 1 << pos

    return witnesses, reject_masks_by_witness, full_cover_mask


def canonicalize_via_orbit(witness_rows: List[Dict[str, Any]]):
    # reuse analyzer's orbit canonicalizer: _witness_orbit_stats
    res = analyze._witness_orbit_stats(witness_rows)
    # canonical_rep is a list-of-dicts; convert to a tuple repr for use in sets
    canon = tuple(
        (
            tuple(tuple(p) for p in d["line"]),
            int(d["z"]),
            int(d["sign_pm1"]),
            d.get("line_type"),
        )
        for d in res["canonical_rep"]
    )
    return canon, res


def randomized_greedy_enumeration(
    lines, sign_field, mats, target_k, max_samples, seed=0
):
    witnesses, reject_masks_by_witness, full_cover_mask = build_reject_masks(
        lines, sign_field, mats
    )
    n = len(witnesses)
    rnd = random.Random(seed)

    found_canonical_reps = dict()  # canonical->count

    for it in range(max_samples):
        order = list(range(n))
        rnd.shuffle(order)
        covered = 0
        selected = []
        for i in order:
            mask = reject_masks_by_witness[i]
            if ((covered | mask) ^ covered) != 0:
                covered |= mask
                selected.append(i)
            if covered == full_cover_mask:
                break
        # quick minimize: remove redundant elements
        changed = True
        while changed:
            changed = False
            for i in list(selected):
                # try remove i
                sel2 = [x for x in selected if x != i]
                cov2 = 0
                for j in sel2:
                    cov2 |= reject_masks_by_witness[j]
                if cov2 == full_cover_mask:
                    selected = sel2
                    changed = True
                    break
        if covered == full_cover_mask and len(selected) == target_k:
            # build witness_rows list for these indices
            rows = []
            for idx in selected:
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
            canon, rep_info = canonicalize_via_orbit(rows)
            found_canonical_reps[canon] = found_canonical_reps.get(canon, 0) + 1
    return found_canonical_reps


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--in-json", type=Path, required=True)
    p.add_argument(
        "--candidate-space", type=str, choices=("hessian", "agl"), default="hessian"
    )
    p.add_argument("--max-samples", type=int, default=2000)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "e6_f3_trilinear_min_cert_enumeration.json",
    )
    args = p.parse_args()

    lines, sign_field = analyze._load_sign_field(args.in_json)
    gl = analyze._gl2_3()
    sl = [m for m in gl if m[4] == 1]

    if args.candidate_space == "hessian":
        mats = sl
    else:
        mats = gl

    full_cert = analyze._full_sign_obstruction_certificate(
        lines, sign_field, mats, "sample-enum"
    )
    assert full_cert[
        "exact_min_certificate_found"
    ], "No exact minimal certificate found"
    k = int(full_cert["exact_min_certificate_size"])

    samples = randomized_greedy_enumeration(
        lines, sign_field, mats, k, args.max_samples, args.seed
    )

    out = {
        "status": "ok",
        "candidate_space": args.candidate_space,
        "k_min": k,
        "samples_tried": args.max_samples,
        "distinct_canonical_representatives_found": len(samples),
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
            for canon in samples.keys()
        ],
        "counts": {"repr_count": {str(c): int(v) for c, v in samples.items()}},
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {args.out_json} (found {len(samples)} distinct canonical reps)")


if __name__ == "__main__":
    main()
