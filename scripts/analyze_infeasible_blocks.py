#!/usr/bin/env python3
"""Analyze local INFEASIBLE blocks and find minimal conflicting subsets via forced-seed checks.

Usage:
  python scripts/analyze_infeasible_blocks.py --bij committed_artifacts/PART_CVII_e8_bijection_intermediate_1770491863.json --time-limit 60 --k 40 --seed 212 --auto-commit

Outputs: checks/PART_CVII_infeasible_block_analysis_<ts>.json
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List


def load_bijection(bij_path: Path) -> Dict[int, int]:
    j = json.loads(bij_path.read_text(encoding="utf-8"))
    bij = j.get("bijection") or {}
    return {int(k): int(v) for k, v in bij.items()}


def write_seed_for_edges(bij: Dict[int, int], edges: List[int], outpath: Path):
    seed_edges = []
    for e in edges:
        if e in bij:
            seed_edges.append({"edge_index": int(e), "root_index": int(bij[e])})
    out = {"seed_edges": seed_edges, "rotation": None}
    from utils.json_safe import dump_json

    dump_json(out, outpath, indent=2)


def run_forced_seed(
    seed_json: Path, k: int, time_limit: float, seed: int
) -> Dict[str, Any]:
    cmd = [
        "py",
        "-3",
        "-X",
        "utf8",
        "scripts/solve_e8_embedding_cpsat.py",
        "--seed-json",
        str(seed_json),
        "--k",
        str(k),
        "--time-limit",
        str(time_limit),
        "--seed",
        str(seed),
        "--force-seed",
    ]
    try:
        # enforce an external timeout slightly larger than the solver's internal time_limit
        timeout = max(10, int(time_limit) + 5)
        proc = subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
        # read output JSON if present
        out_json = None
        checks_path = Path.cwd() / "checks" / "PART_CVII_e8_embedding_cpsat.json"
        if checks_path.exists():
            out_json = json.loads(checks_path.read_text(encoding="utf-8"))
        return {
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "json": out_json,
        }
    except subprocess.TimeoutExpired as e:
        return {
            "timeout": True,
            "error": f"Timeout after {timeout}s",
            "stdout": getattr(e, "stdout", ""),
            "stderr": getattr(e, "stderr", ""),
        }
    except Exception as e:
        return {"error": str(e)}


def shrink_unsat(
    bij: Dict[int, int],
    edges: List[int],
    k: int,
    time_limit: float,
    seed: int,
    max_checks: int | None = None,
) -> List[int]:
    # Greedy shrink: remove edges that are not necessary for infeasibility
    U = list(edges)
    checks_done = 0
    changed = True
    while changed:
        changed = False
        for e in list(U):
            # Respect a maximum number of forced-seed checks for quick diagnostics
            if max_checks is not None and checks_done >= max_checks:
                return U

            cand = [x for x in U if x != e]
            tmp = Path.cwd() / "checks" / f"_tmp_seed_shrink_{int(time.time())}.json"
            write_seed_for_edges(bij, cand, tmp)
            res = run_forced_seed(
                tmp, k=k, time_limit=max(5, time_limit / 6), seed=seed
            )
            checks_done += 1

            # if still infeasible, we can drop e
            j = res.get("json")
            if j and j.get("status") == "INFEASIBLE":
                U = cand
                changed = True
                break
            # cleanup
            try:
                tmp.unlink()
            except Exception:
                pass
        # end for
    return U


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bij", required=True)
    parser.add_argument("--time-limit", type=float, default=60.0)
    parser.add_argument("--k", type=int, default=40)
    parser.add_argument("--seed", type=int, default=212)
    parser.add_argument("--auto-commit", action="store_true")
    parser.add_argument(
        "--shrink-max-checks",
        type=int,
        default=50,
        help="Maximum forced-seed checks during greedy shrink per block (set 0 for none, or a positive integer)",
    )
    args = parser.parse_args()

    bij_path = Path(args.bij)
    if not bij_path.exists():
        raise SystemExit("Bijection file not found")
    bij = load_bijection(bij_path)

    local_files = sorted(glob.glob("checks/PART_CVII_e8_bijection_local_seed_*.json"))
    infeasible_files = []
    for f in local_files:
        j = json.loads(open(f, encoding="utf-8").read())
        if j.get("status") == "INFEASIBLE":
            infeasible_files.append((f, j))

    results = {
        "checked": [],
        "timestamp": int(time.time()),
        "bij_source": str(bij_path),
    }

    for f, j in infeasible_files:
        block_edges = j.get("block_edges") or []
        if not block_edges:
            # skip
            results["checked"].append({"file": f, "status": "no_block_edges"})
            continue

        tmp_seed = Path.cwd() / "checks" / f"_tmp_seed_block_{Path(f).stem}.json"
        write_seed_for_edges(bij, block_edges, tmp_seed)

        res = run_forced_seed(
            tmp_seed, k=args.k, time_limit=args.time_limit, seed=args.seed
        )
        status = res.get("json", {}).get("status") if res.get("json") else None
        entry = {
            "file": f,
            "start_vertex": j.get("start_vertex"),
            "block_size": len(block_edges),
            "forced_status": status,
        }

        if status == "INFEASIBLE":
            # attempt shrink to minimal conflict (bounded by --shrink-max-checks for quick diagnostics)
            max_checks = (
                None
                if args.shrink_max_checks is None or args.shrink_max_checks <= 0
                else int(args.shrink_max_checks)
            )
            min_conflict = shrink_unsat(
                bij,
                block_edges,
                k=args.k,
                time_limit=args.time_limit,
                seed=args.seed,
                max_checks=max_checks,
            )
            entry["minimal_conflict"] = min_conflict
            entry["minimal_conflict_size"] = len(min_conflict)
        results["checked"].append(entry)
        try:
            tmp_seed.unlink()
        except Exception:
            pass

    stamp = int(time.time())
    outp = Path.cwd() / "checks" / f"PART_CVII_infeasible_block_analysis_{stamp}.json"
    from utils.json_safe import dump_json

    dump_json(results, outp, indent=2)
    print("Wrote", outp)

    if getattr(args, "auto_commit", False):
        try:
            from scripts import git_auto_keep

            artifact = Path.cwd() / "committed_artifacts" / outp.name
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_text(outp.read_text(encoding="utf-8"), encoding="utf-8")
            ok, msg = git_auto_keep.git_add_commit(
                [str(artifact)], f"Infeasible block analysis: {outp.name}"
            )
            print("Auto-commit result:", ok, msg)
        except Exception as e:
            print("Auto-commit failed:", e)


if __name__ == "__main__":
    main()
