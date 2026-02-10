#!/usr/bin/env python3
"""Enumerate (or sample) minimal full-sign obstruction certificates and report AGL-orbit canonical reps.

Usage:
  py -3 tools/enumerate_minimal_certificates.py --in-json artifacts/e6_f3_trilinear_map.json --candidate-space hessian --max-samples 200 --out-json artifacts/e6_f3_trilinear_min_cert_enumeration.json

Notes:
 - Uses a randomized greedy sampler to find minimal-size certificates and canonicalize them under AGL(2,3) x z-affine.
 - This is a heuristic enumerator (not exhaustive) but suitable for discovering distinct orbit types.
 - New CLI options: `--workers N` (parallel sampling), `--batch-size N`, `--patience N` (rounds with no new reps to stop), `--checkpoint-interval N` (samples between checkpoint saves), `--stop-if-found N` (stop when N distinct canonical reps found), and `--progress` (print progress). Checkpointing writes intermediate results to `--out-json` so long runs can be resumed from saved artifacts.

# Examples:
#  py -3 tools/enumerate_minimal_certificates.py --in-json artifacts/e6_f3_trilinear_map.json --candidate-space hessian --max-samples 20000 --seed 42 --workers 4 --batch-size 1000 --checkpoint-interval 2000 --out-json artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_20k.json --progress
#  py -3 tools/enumerate_minimal_certificates.py --in-json artifacts/e6_f3_trilinear_map.json --candidate-space agl --max-samples 20000 --seed 43 --workers 4 --batch-size 1000 --checkpoint-interval 2000 --out-json artifacts/e6_f3_trilinear_min_cert_enumeration_agl_20k.json --progress
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


def sample_batch(
    witnesses,
    reject_masks_by_witness,
    full_cover_mask,
    sign_field,
    mats,
    target_k,
    iterations,
    seed=0,
):
    """Run a batch of randomized greedy enumerations and return a dict canonical->count and iterations run."""
    rnd = random.Random(seed)
    n = len(witnesses)
    found = {}
    ran = 0
    for _ in range(iterations):
        ran += 1
        order = list(range(n))
        rnd.shuffle(order)
        covered = 0
        selected = []
        for i in order:
            mask = reject_masks_by_witness[i]
            if (covered | mask) != covered:
                covered |= mask
                selected.append(i)
            if covered == full_cover_mask:
                break
        if covered != full_cover_mask:
            continue
        # minimize selection
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
        if len(selected) == target_k:
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
            canon, _rep_info = canonicalize_via_orbit(rows)
            found[canon] = found.get(canon, 0) + 1
    return found, ran


def randomized_greedy_enumeration(
    lines,
    sign_field,
    mats,
    target_k,
    max_samples,
    seed=0,
    workers=1,
    batch_size=100,
    patience=10,
    checkpoint_interval=1000,
    stop_if_found=0,
    out_json_path=None,
    progress=False,
):
    """Run the randomized greedy enumeration with optional parallelism and early stopping.

    Args:
        lines, sign_field, mats, target_k: as before
        max_samples: total number of randomized samples to attempt
        seed: base seed for RNG
        workers: number of parallel workers (ProcessPoolExecutor)
        batch_size: number of samples per worker task
        patience: number of consecutive rounds with no new canonical reps before stopping
        checkpoint_interval: save intermediate results every N samples
        stop_if_found: stop when this many distinct canonical reps have been found (0 means no stop)
        out_json_path: optional Path to write checkpoints to
        progress: if True, print progress lines
    Returns:
        found_canonical_reps: dict canonical->count
    """
    witnesses, reject_masks_by_witness, full_cover_mask = build_reject_masks(
        lines, sign_field, mats
    )

    found_canonical_reps: dict = {}
    samples_done = 0
    rounds_without_new = 0
    next_checkpoint_at = checkpoint_interval
    base_seed = int(seed)

    # Calculate total rounds (each round consists of workers * batch_size samples, except possibly last)
    import math

    if max_samples <= 0:
        return found_canonical_reps

    # Simple single-worker fast path
    if workers <= 1:
        rnd = random.Random(base_seed)
        n = len(witnesses)
        # run single-threaded
        for it in range(max_samples):
            order = list(range(n))
            rnd.shuffle(order)
            covered = 0
            selected = []
            for i in order:
                mask = reject_masks_by_witness[i]
                if (covered | mask) != covered:
                    covered |= mask
                    selected.append(i)
                if covered == full_cover_mask:
                    break
            if covered != full_cover_mask:
                samples_done += 1
                continue
            # minimize
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
            if len(selected) == target_k:
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
                canon, _rep_info = canonicalize_via_orbit(rows)
                if canon not in found_canonical_reps:
                    rounds_without_new = 0
                else:
                    rounds_without_new += 1
                found_canonical_reps[canon] = found_canonical_reps.get(canon, 0) + 1
            samples_done += 1
            # checkpointing
            if out_json_path and samples_done >= next_checkpoint_at:
                _write_checkpoint(
                    out_json_path, found_canonical_reps, samples_done, target_k
                )
                next_checkpoint_at += checkpoint_interval
            if stop_if_found and len(found_canonical_reps) >= stop_if_found:
                break
            if rounds_without_new >= patience:
                if progress:
                    print(
                        f"Stopping early after {samples_done} samples (no new reps for {patience} samples)"
                    )
                break
        return found_canonical_reps

    # Multi-worker path
    from concurrent.futures import ProcessPoolExecutor, as_completed

    # Number of full tasks we'll submit in total
    samples_remaining = max_samples
    round_idx = 0
    while samples_remaining > 0:
        tasks = []
        iters_for_tasks = []
        with ProcessPoolExecutor(max_workers=workers) as ex:
            for w in range(workers):
                iters = min(batch_size, samples_remaining)
                if iters <= 0:
                    break
                seed_w = base_seed + (round_idx * workers + w)
                tasks.append(
                    ex.submit(
                        sample_batch,
                        witnesses,
                        reject_masks_by_witness,
                        full_cover_mask,
                        sign_field,
                        mats,
                        target_k,
                        iters,
                        seed_w,
                    )
                )
                iters_for_tasks.append(iters)
                samples_remaining -= iters
            round_idx += 1
            # collect
            batch_found_total = {}
            total_iters_run = 0
            for fut in as_completed(tasks):
                res_found, ran = fut.result()
                total_iters_run += ran
                for canon, cnt in res_found.items():
                    batch_found_total[canon] = batch_found_total.get(canon, 0) + cnt
        # Merge batch results
        new_found_in_batch = False
        for canon, cnt in batch_found_total.items():
            if canon not in found_canonical_reps:
                new_found_in_batch = True
                found_canonical_reps[canon] = cnt
            else:
                found_canonical_reps[canon] += cnt
        samples_done += total_iters_run
        if new_found_in_batch:
            rounds_without_new = 0
        else:
            rounds_without_new += 1
        # checkpoint
        if out_json_path and samples_done >= next_checkpoint_at:
            _write_checkpoint(
                out_json_path, found_canonical_reps, samples_done, target_k
            )
            next_checkpoint_at += checkpoint_interval
        # progress
        if progress:
            print(
                f"Round {round_idx}: samples_done={samples_done}, distinct_reps={len(found_canonical_reps)}"
            )
        # stopping criteria
        if stop_if_found and len(found_canonical_reps) >= stop_if_found:
            break
        if rounds_without_new >= patience:
            if progress:
                print(
                    f"Stopping early after {samples_done} samples (no new reps for {patience} rounds)"
                )
            break
    return found_canonical_reps


def _write_checkpoint(out_json_path, found_canonical_reps, samples_done, k):
    out = {
        "status": "ok",
        "k_min": k,
        "samples_tried": samples_done,
        "distinct_canonical_representatives_found": len(found_canonical_reps),
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
            for canon in found_canonical_reps.keys()
        ],
        "counts": {
            "repr_count": {str(c): int(v) for c, v in found_canonical_reps.items()}
        },
    }
    out_json_path.parent.mkdir(parents=True, exist_ok=True)
    out_json_path.write_text(json.dumps(out, indent=2), encoding="utf-8")


def exhaustive_enumeration(
    lines,
    sign_field,
    mats,
    target_k,
    workers=1,
    checkpoint_interval=10000,
    out_json_path=None,
    progress=False,
):
    """Exhaustively enumerate all witness subsets of size `target_k` and canonicalize those that cover the full non-stabilizer candidate universe.

    Returns:
        (found_dict, combinations_checked)
    """
    from concurrent.futures import ProcessPoolExecutor, as_completed
    from itertools import combinations

    witnesses, reject_masks_by_witness, full_cover_mask = build_reject_masks(
        lines, sign_field, mats
    )
    n = len(witnesses)

    print(f"exhaustive_enumeration: n={n}, k={target_k}")

    # Precompute suffix ORs for pruning
    suffix_or = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        suffix_or[i] = suffix_or[i + 1] | reject_masks_by_witness[i]


def _exhaustive_worker_first_index(
    i, witnesses, reject_masks_by_witness, full_cover_mask, sign_field, target_k
):
    from itertools import combinations

    found = {}
    iter_count = 0
    n = len(witnesses)
    for tail in combinations(range(i + 1, n), target_k - 1):
        iter_count += 1
        sel = (i,) + tail
        cov = 0
        for idx in sel:
            cov |= reject_masks_by_witness[idx]
            if cov == full_cover_mask:
                break
        if cov != full_cover_mask:
            continue
        rows = []
        for idx in sel:
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
        canon, _rep_info = canonicalize_via_orbit(rows)
        found[canon] = found.get(canon, 0) + 1
    return found, iter_count

    def worker_first_index(i):
        found = {}
        iter_count = 0
        for tail in combinations(range(i + 1, n), target_k - 1):
            iter_count += 1
            sel = (i,) + tail
            cov = 0
            for idx in sel:
                cov |= reject_masks_by_witness[idx]
                if cov == full_cover_mask:
                    break
            if cov != full_cover_mask:
                continue
            rows = []
            for idx in sel:
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
            canon, _rep_info = canonicalize_via_orbit(rows)
            found[canon] = found.get(canon, 0) + 1
        return found, iter_count

    total_iters = 0
    found_total = {}
    # Single worker path: iterate over starting indices
    if workers <= 1:
        counts_tried = 0
        counts_skipped = 0
        for i in range(0, n - target_k + 1):
            if suffix_or[i] != full_cover_mask:
                counts_skipped += 1
                if progress:
                    print(f"i={i}: skipped (suffix_or cannot cover)")
                continue
            counts_tried += 1
            found_i, ran = _exhaustive_worker_first_index(
                i,
                witnesses,
                reject_masks_by_witness,
                full_cover_mask,
                sign_field,
                target_k,
            )
            total_iters += ran
            for c, cnt in found_i.items():
                found_total[c] = found_total.get(c, 0) + cnt
            if out_json_path and total_iters % checkpoint_interval == 0:
                _write_checkpoint(out_json_path, found_total, total_iters, target_k)
            if progress:
                print(f"i={i}: ran={ran}, distinct_found={len(found_total)}")
        if progress:
            print(
                f"exhaustive done: tried={counts_tried}, skipped={counts_skipped}, total_iters={total_iters}, distinct_found={len(found_total)}"
            )
        return found_total, total_iters

    # Parallel path: submit each i as a separate task
    futures = {}
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for i in range(0, n - target_k + 1):
            if suffix_or[i] != full_cover_mask:
                continue
            futures[
                ex.submit(
                    _exhaustive_worker_first_index,
                    i,
                    witnesses,
                    reject_masks_by_witness,
                    full_cover_mask,
                    sign_field,
                    target_k,
                )
            ] = i
        for fut in as_completed(futures):
            found_i, ran = fut.result()
            total_iters += ran
            for c, cnt in found_i.items():
                found_total[c] = found_total.get(c, 0) + cnt
            if out_json_path and total_iters % checkpoint_interval < 1000:
                _write_checkpoint(out_json_path, found_total, total_iters, target_k)
            if progress:
                print(
                    f"finished i={futures[fut]}: ran={ran}, distinct_total={len(found_total)}"
                )
    return found_total, total_iters


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--in-json", type=Path, required=True)
    p.add_argument(
        "--candidate-space", type=str, choices=("hessian", "agl"), default="hessian"
    )
    p.add_argument("--max-samples", type=int, default=2000)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--workers", type=int, default=1)
    p.add_argument("--batch-size", type=int, default=200)
    p.add_argument("--patience", type=int, default=10)
    p.add_argument("--checkpoint-interval", type=int, default=1000)
    p.add_argument("--stop-if-found", type=int, default=0)
    p.add_argument(
        "--exhaustive",
        action="store_true",
        help="Run exhaustive enumeration of size k (exact)",
    )
    p.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "e6_f3_trilinear_min_cert_enumeration.json",
    )
    p.add_argument("--progress", action="store_true")
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

    if args.exhaustive:
        samples, tried = exhaustive_enumeration(
            lines,
            sign_field,
            mats,
            k,
            workers=args.workers,
            checkpoint_interval=args.checkpoint_interval,
            out_json_path=args.out_json,
            progress=args.progress,
        )
    else:
        samples = randomized_greedy_enumeration(
            lines,
            sign_field,
            mats,
            k,
            args.max_samples,
            seed=args.seed,
            workers=args.workers,
            batch_size=args.batch_size,
            patience=args.patience,
            checkpoint_interval=args.checkpoint_interval,
            stop_if_found=args.stop_if_found,
            out_json_path=args.out_json,
            progress=args.progress,
        )
        tried = args.max_samples

    out = {
        "status": "ok",
        "candidate_space": args.candidate_space,
        "k_min": k,
        "samples_tried": tried,
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
