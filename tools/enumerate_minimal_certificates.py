#!/usr/bin/env python3
"""
Enumerate minimal full-sign obstruction certificates and canonicalize them under
AGL(2,3) x affine z-maps.

Modes:
  - sample: randomized greedy sampler (heuristic, fast)
  - exact: exact size-k_min covering-set search with pruning and optional caps
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze


def build_reject_masks(lines, sign_field, mats):
    data = analyze._full_sign_obstruction_data(lines, sign_field, mats)
    return (
        data["witnesses"],
        data["reject_masks_by_witness"],
        data["full_cover_mask"],
    )


def witness_rows_from_indices(witnesses, sign_field, indices):
    rows = []
    for idx in indices:
        line, z = witnesses[idx]
        rows.append(
            {
                "line": [[int(p[0]), int(p[1])] for p in line],
                "z": int(z),
                "sign_pm1": int(sign_field[(line, z)]),
                "line_type": analyze._line_equation_type(line)[0],
            }
        )
    return rows


def canonicalize_via_orbit(witness_rows):
    res = analyze._witness_orbit_stats(witness_rows)
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


def canonical_tuple_to_json(canon):
    out = []
    for item in canon:
        out.append(
            {
                "line": [[int(p[0]), int(p[1])] for p in item[0]],
                "z": int(item[1]),
                "sign_pm1": int(item[2]),
                "line_type": str(item[3]),
            }
        )
    return out


def randomized_greedy_enumeration(lines, sign_field, mats, target_k, max_samples, seed=0):
    witnesses, reject_masks_by_witness, full_cover_mask = build_reject_masks(
        lines, sign_field, mats
    )
    n = len(witnesses)
    rnd = random.Random(seed)

    found_canonical_reps = {}

    for _ in range(max_samples):
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
        changed = True
        while changed:
            changed = False
            for i in list(selected):
                sel2 = [x for x in selected if x != i]
                cov2 = 0
                for j in sel2:
                    cov2 |= reject_masks_by_witness[j]
                if cov2 == full_cover_mask:
                    selected = sel2
                    changed = True
                    break
        if covered == full_cover_mask and len(selected) == target_k:
            rows = witness_rows_from_indices(witnesses, sign_field, selected)
            canon, _ = canonicalize_via_orbit(rows)
            found_canonical_reps[canon] = found_canonical_reps.get(canon, 0) + 1
    return found_canonical_reps


def exact_min_enumeration(
    lines,
    sign_field,
    mats,
    target_k,
    max_exact_solutions=0,
    time_limit_sec=0.0,
):
    witnesses, reject_masks_by_witness, full_cover_mask = build_reject_masks(
        lines, sign_field, mats
    )
    n = len(witnesses)
    order = sorted(
        range(n),
        key=lambda wi: reject_masks_by_witness[wi].bit_count(),
        reverse=True,
    )
    suffix_union = [0 for _ in range(n + 1)]
    for pos in range(n - 1, -1, -1):
        suffix_union[pos] = suffix_union[pos + 1] | reject_masks_by_witness[order[pos]]

    found_canonical_reps = {}
    total_solutions = 0
    explored_nodes = 0
    truncated_by_max_solutions = False
    truncated_by_time_limit = False
    start = time.monotonic()
    selected: list[int] = []

    def should_stop() -> bool:
        nonlocal truncated_by_time_limit
        if time_limit_sec > 0 and (time.monotonic() - start) >= time_limit_sec:
            truncated_by_time_limit = True
            return True
        return False

    def dfs(pos: int, chosen: int, covered: int) -> None:
        nonlocal total_solutions, explored_nodes, truncated_by_max_solutions
        if truncated_by_max_solutions or truncated_by_time_limit:
            return
        if should_stop():
            return
        explored_nodes += 1
        if chosen == target_k:
            if covered == full_cover_mask:
                total_solutions += 1
                rows = witness_rows_from_indices(witnesses, sign_field, selected)
                canon, _ = canonicalize_via_orbit(rows)
                found_canonical_reps[canon] = found_canonical_reps.get(canon, 0) + 1
                if max_exact_solutions > 0 and total_solutions >= max_exact_solutions:
                    truncated_by_max_solutions = True
            return
        if pos == n:
            return
        if chosen + (n - pos) < target_k:
            return
        if (covered | suffix_union[pos]) != full_cover_mask:
            return

        wi = order[pos]
        selected.append(wi)
        dfs(pos + 1, chosen + 1, covered | reject_masks_by_witness[wi])
        selected.pop()
        dfs(pos + 1, chosen, covered)

    dfs(0, 0, 0)
    return {
        "found_canonical_reps": found_canonical_reps,
        "exact_solutions_count": int(total_solutions),
        "search_nodes_explored": int(explored_nodes),
        "truncated_by_max_solutions": bool(truncated_by_max_solutions),
        "truncated_by_time_limit": bool(truncated_by_time_limit),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--in-json", type=Path, required=True)
    p.add_argument(
        "--candidate-space", type=str, choices=("hessian", "agl"), default="hessian"
    )
    p.add_argument("--mode", type=str, choices=("sample", "exact"), default="sample")
    p.add_argument("--max-samples", type=int, default=2000)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--max-exact-solutions", type=int, default=0)
    p.add_argument("--time-limit-sec", type=float, default=0.0)
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

    if args.mode == "exact":
        exact = exact_min_enumeration(
            lines,
            sign_field,
            mats,
            k,
            max_exact_solutions=int(args.max_exact_solutions),
            time_limit_sec=float(args.time_limit_sec),
        )
        reps = exact["found_canonical_reps"]
        samples_tried = None
    else:
        reps = randomized_greedy_enumeration(
            lines, sign_field, mats, k, args.max_samples, args.seed
        )
        exact = None
        samples_tried = int(args.max_samples)

    rep_rows = []
    for canon, count in sorted(reps.items(), key=lambda kv: (-kv[1], kv[0])):
        rep_rows.append(
            {
                "hit_count": int(count),
                "canonical_repr": canonical_tuple_to_json(canon),
            }
        )

    out = {
        "status": "ok",
        "mode": args.mode,
        "candidate_space": args.candidate_space,
        "k_min": k,
        "samples_tried": samples_tried,
        "distinct_canonical_representatives_found": len(reps),
        "representatives": rep_rows,
        "counts": {"repr_count": {str(c): int(v) for c, v in reps.items()}},
    }
    if exact is not None:
        out["exact_solutions_count"] = exact["exact_solutions_count"]
        out["search_nodes_explored"] = exact["search_nodes_explored"]
        out["truncated_by_max_solutions"] = exact["truncated_by_max_solutions"]
        out["truncated_by_time_limit"] = exact["truncated_by_time_limit"]
        out["limits"] = {
            "max_exact_solutions": int(args.max_exact_solutions),
            "time_limit_sec": float(args.time_limit_sec),
        }
    else:
        out["seed"] = int(args.seed)

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(
        "Wrote {} (mode={}, found {} distinct canonical reps)".format(
            args.out_json, args.mode, len(reps)
        )
    )


if __name__ == "__main__":
    main()
