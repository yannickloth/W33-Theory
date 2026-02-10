#!/usr/bin/env python3
"""Run ddmin on z3 candidate NPZ basis vectors to find minimal supporting subsets.

The ddmin aims to find a (locally) minimal subset of eigen-basis columns (across
clusters) that still pass verification metrics (idempotency, orthogonality, ranks).

Usage: python scripts/ddmin_z3_candidate.py --artifact committed_artifacts/PART_CVII_z3_candidate_...json --time-limit 30 --max-checks 1000
"""
from __future__ import annotations

import argparse
import math
import time
import json
import glob
import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple

import numpy as np

try:
    from utils.json_safe import dump_json
except Exception:
    import sys as _sys
    from pathlib import Path as _Path

    _sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
    from utils.json_safe import dump_json


def ddmin(S: List[int], test_func, max_checks: int | None = None, time_limit: float | None = None):
    n = 2
    checks = 0
    start_time = time.time()

    def time_exceeded():
        return time_limit is not None and (time.time() - start_time) > float(time_limit)

    def test(subset: List[int]):
        nonlocal checks
        if time_exceeded():
            # if time is up, conservatively return False so ddmin stops shrinking further
            return False
        checks += 1
        return bool(test_func(subset))

    S = list(S)
    if not test(S):
        return [], {}

    test_log = {}

    while True:
        if max_checks is not None and checks >= max_checks:
            return S, test_log
        if time_exceeded():
            return S, test_log
        if len(S) == 1:
            return S, test_log
        subset_size = math.ceil(len(S) / n)
        some_progress = False
        for i in range(0, len(S), subset_size):
            if time_exceeded():
                return S, test_log
            part = S[i : i + subset_size]
            if not part:
                continue
            if test(part):
                S = part
                n = max(n - 1, 2)
                some_progress = True
                break
            others = [x for x in S if x not in part]
            if others and test(others):
                S = others
                n = max(n - 1, 2)
                some_progress = True
                break
            if max_checks is not None and checks >= max_checks:
                return S, test_log
        if not some_progress:
            if n >= len(S):
                return S, test_log
            n = min(len(S), n * 2)


def make_test_function(cluster_bases: List[np.ndarray], target_ranks: List[int], tol: float = 1e-8):
    # cluster_bases: list of arrays cluster_k with shape (m, c_k)
    # We flatten indices as [0..c0-1] U [c0..c0+c1-1] U [c0+c1..]
    counts = [int(b.shape[1]) for b in cluster_bases]

    def idx_to_cluster(idx: int) -> Tuple[int, int]:
        # returns (cluster_k, local_index)
        acc = 0
        for k, c in enumerate(counts):
            if idx < acc + c:
                return k, int(idx - acc)
            acc += c
        raise IndexError(idx)

    def test(subset: List[int]) -> bool:
        # assemble per-cluster selected columns
        per = {k: [] for k in range(len(cluster_bases))}
        for idx in subset:
            k, j = idx_to_cluster(idx)
            per[k].append(j)

        # build projection matrices from selected columns
        Pmats = []
        m = cluster_bases[0].shape[0]
        for k, cols in per.items():
            if not cols:
                return False
            V = cluster_bases[k][:, cols]
            # quick rank check
            rank = int(np.linalg.matrix_rank(V, tol))
            if rank < target_ranks[k]:
                return False
            # compute orthonormal basis via QR
            try:
                Q, _ = np.linalg.qr(V)
            except Exception:
                # fallback via SVD
                U, s, _ = np.linalg.svd(V, full_matrices=False)
                Q = U
            P = Q @ Q.conj().T
            # idempotency check
            iderr = float(np.linalg.norm(P @ P - P))
            if iderr > 1e-6:  # allow some slack
                return False
            Pmats.append(P)

        # cross orthogonality
        for i in range(len(Pmats)):
            for j in range(len(Pmats)):
                if i == j:
                    continue
                cn = float(np.linalg.norm(Pmats[i] @ Pmats[j]))
                if cn > 1e-6:
                    return False

        # sum to identity check
        S = sum(Pmats)
        if float(np.linalg.norm(S - np.eye(m))) > 1e-6:
            return False

        return True

    return test


def process_candidate(npz_path: Path, max_checks: int | None, time_limit: float) -> dict:
    # load clusters
    with np.load(str(npz_path)) as f:
        cluster_0 = f.get("cluster_0", None)
        cluster_1 = f.get("cluster_1", None)
        cluster_2 = f.get("cluster_2", None)

    if cluster_0 is None or cluster_1 is None or cluster_2 is None:
        raise ValueError("NPZ missing cluster_{0,1,2}")

    cluster_bases = [cluster_0, cluster_1, cluster_2]
    counts = [int(b.shape[1]) for b in cluster_bases]
    total = sum(counts)
    target_ranks = counts.copy()  # require the same ranks

    # build initial S
    S = list(range(total))

    test_func = make_test_function(cluster_bases, target_ranks)

    # run ddmin with internal time checks (no spawn) — ddmin will return early if time_limit exceeded
    result = {}
    subset, _log = ddmin(S, test_func, max_checks=max_checks, time_limit=time_limit)
    if not subset:
        result["subset"] = None
        result["timeout"] = False
        return result
    if time_limit is not None:
        # if ddmin returned a subset but may have terminated due to time, attempt to detect that
        # (ddmin will stop early if time exceeded and return current S)
        pass


    # map subset back to clusters
    per = {0: [], 1: [], 2: []}
    acc = 0
    for k, c in enumerate(counts):
        for local_idx in subset:
            pass
    # simpler mapping
    acc = 0
    for idx in subset:
        if idx < counts[0]:
            per[0].append(int(idx))
        elif idx < counts[0] + counts[1]:
            per[1].append(int(idx - counts[0]))
        else:
            per[2].append(int(idx - counts[0] - counts[1]))

    result.update(
        {
            "npz": str(npz_path),
            "initial_counts": counts,
            "final_total": len(subset),
            "final_counts": [len(per[0]), len(per[1]), len(per[2])],
            "subset_indices": subset,
            "subset_by_cluster": per,
            "timeout": result.get("timeout", False),
        }
    )

    # write reduced NPZ for subset
    outdir = Path("checks") / f"z3_ddmin_{int(time.time())}"
    outdir.mkdir(parents=True, exist_ok=True)
    subset_npz = outdir / (npz_path.stem + "_ddmin.npz")

    sel_bases = {}
    for k in range(3):
        cols = per[k]
        if cols:
            sel_bases[f"cluster_{k}"] = cluster_bases[k][:, cols]
        else:
            sel_bases[f"cluster_{k}"] = np.zeros((cluster_bases[k].shape[0], 0), dtype=complex)

    np.savez_compressed(subset_npz, **sel_bases)
    result["subset_npz"] = str(subset_npz)

    # write summary JSON
    ts = int(time.time())
    out_json = Path("checks") / f"PART_CVII_z3_candidate_ddmin_{ts}.json"
    dump_json(result, out_json, indent=2)
    result["summary_json"] = str(out_json)

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--artifact-json",
        help="Committed artifact JSON (committed_artifacts/PART_CVII_z3_candidate_*.json) or path to NPZ",
    )
    parser.add_argument("--n", type=int, default=5, help="Top N artifacts to process")
    parser.add_argument("--time-limit", type=float, default=30.0, help="Time limit per candidate (sec)")
    parser.add_argument("--max-checks", type=int, default=5000, help="Max ddmin checks per candidate")
    parser.add_argument("--commit", action="store_true", help="Commit any resultant artifacts")
    args = parser.parse_args()

    if args.artifact_json and Path(args.artifact_json).suffix == ".npz":
        # single NPZ provided
        res = process_candidate(Path(args.artifact_json), max_checks=args.max_checks, time_limit=args.time_limit)
        print("Result:", res)
        return

    # find top committed artifacts
    files = sorted(glob.glob("committed_artifacts/PART_CVII_z3_candidate_*.json"), key=os.path.getmtime)
    if not files:
        raise FileNotFoundError("No committed z3 candidate metadata found")

    targets = files[-args.n :]
    all_results = []

    for jf in targets:
        meta = json.loads(open(jf, encoding="utf-8").read())
        npzname = meta.get("artifact")
        if not npzname:
            print("No artifact entry in", jf, "skipping")
            continue
        npzpath = Path("committed_artifacts") / Path(npzname).name
        if not npzpath.exists():
            print("NPZ not found for", jf, npzpath)
            continue
        print("Processing", npzpath)
        res = process_candidate(npzpath, max_checks=args.max_checks, time_limit=args.time_limit)
        res["candidate_meta"] = meta
        all_results.append(res)

        # optionally commit subset_npz and summary
        if args.commit and res.get("subset_npz"):
            # only commit if a strictly smaller subset was found
            if res.get("final_total", 0) < sum(res.get("initial_counts", [])):
                subset_npz = Path(res["subset_npz"])
                summary_json = Path(res["summary_json"]) if res.get("summary_json") else None
                # copy NPZ into committed_artifacts and write a small metadata JSON
                ts = int(time.time())
                dest_npz = Path("committed_artifacts") / f"PART_CVII_z3_candidate_ddmin_{ts}_{subset_npz.stem}.npz"
                shutil.copy2(subset_npz, dest_npz)
                meta_json = Path("committed_artifacts") / f"PART_CVII_z3_candidate_ddmin_{ts}_{subset_npz.stem}.json"
                dump_json({"source_npz": str(npzpath), "subset_npz": str(dest_npz.name), "summary": str(summary_json)}, meta_json, indent=2)
                subprocess.run(["git", "add", str(dest_npz), str(meta_json)])
                cp = subprocess.run(["git", "commit", "-m", f"Add ddmin reduced NPZ for {npzpath.name}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if cp.returncode != 0:
                    print("git commit failed:", cp.stderr)
                else:
                    print("Committed ddmin artifacts for", npzpath)
            else:
                print("No smaller subset found for", npzpath, "; skipping commit.")
    print("All results written to checks/ and (optionally) committed")


if __name__ == "__main__":
    main()
