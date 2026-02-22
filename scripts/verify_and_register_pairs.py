#!/usr/bin/env python3
"""Verify INFEASIBLE local hotspot pairs with a global CP-SAT forced-seed check and
append canonical forbids when the global solver reports INFEASIBLE.

Usage:
  python scripts/verify_and_register_pairs.py --input checks/PART_CVII_local_hotspot_feasibility_*.json --time-limit 30 --k 40
"""
from __future__ import annotations

import argparse
import glob
import json
import subprocess
import time
from pathlib import Path
from typing import List, Tuple


def run_forced_seed(seed_json: Path, k: int, time_limit: float, seed: int):
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
        timeout = max(10, int(time_limit) + 5)
        proc = subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
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


def write_seed_for_pair(e1: int, r1: int, e2: int, r2: int, outpath: Path):
    out = {
        "seed_edges": [
            {"edge_index": int(e1), "root_index": int(r1)},
            {"edge_index": int(e2), "root_index": int(r2)},
        ],
        "rotation": None,
    }
    outpath.write_text(json.dumps(out, indent=2), encoding="utf-8")
    return outpath


def append_forbid(forbid_path: Path, e_set: List[int], roots: List[int], src: str):
    forb = {"obstruction_sets": []}
    if forbid_path.exists():
        forb = json.loads(forbid_path.read_text(encoding="utf-8"))
    # check duplicates
    for entry in forb.get("obstruction_sets", []):
        if entry.get("set") == e_set and entry.get("roots") == roots:
            return False
    entry = {"set": e_set, "roots": roots, "timestamp": int(time.time()), "source": src}
    forb.setdefault("obstruction_sets", []).append(entry)
    forbid_path.write_text(json.dumps(forb, indent=2), encoding="utf-8")
    return True


def collect_pairs_from_files(
    patterns: List[str],
) -> List[Tuple[Tuple[int, int, int, int], str]]:
    pairs = []
    for p in patterns:
        for fname in sorted(glob.glob(p)):
            j = json.loads(open(fname, encoding="utf-8").read())
            tests = j.get("tests", [])
            for t in tests:
                pair = t.get("pair")
                status = t.get("status", "")
                if not pair or not isinstance(pair, list) or len(pair) != 4:
                    continue
                if str(status).upper().startswith("INFEASIBLE"):
                    pairs.append(
                        (
                            (int(pair[0]), int(pair[1]), int(pair[2]), int(pair[3])),
                            fname,
                        )
                    )
    return pairs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=str,
        nargs="+",
        required=True,
        help="Glob pattern(s) for local_hotspot result files",
    )
    parser.add_argument("--k", type=int, default=40)
    parser.add_argument("--time-limit", type=float, default=30.0)
    parser.add_argument("--seed", type=int, default=212)
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Run forced checks sequentially by default; >1 runs in parallel (riskier)",
    )
    parser.add_argument(
        "--forbid-json", type=str, default="checks/PART_CVII_forbids.json"
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Mirror forbids to committed_artifacts and attempt git commit",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="List pairs but do not run solver"
    )
    parser.add_argument(
        "--max",
        type=int,
        default=0,
        help="Limit number of pairs to verify; 0 means no limit",
    )
    parser.add_argument(
        "--checks-dir",
        type=str,
        default="checks",
        help="Directory to read/write solver check files",
    )
    args = parser.parse_args()

    checks_dir = Path(args.checks_dir)
    forbid_path = Path(args.forbid_json)
    pairs = collect_pairs_from_files(args.input)
    if args.max and len(pairs) > args.max:
        pairs = pairs[: args.max]

    if not pairs:
        print("No INFEASIBLE pairs found in inputs", args.input)
        return

    print(f"Found {len(pairs)} INFEASIBLE pairs to verify")
    verified = []
    skipped = []

    for (e1, r1, e2, r2), src in pairs:
        ts = int(time.time())
        seed_path = checks_dir / f"_tmp_seed_pair_verify_{e1}_{r1}_{e2}_{r2}_{ts}.json"
        write_seed_for_pair(e1, r1, e2, r2, seed_path)
        outp = checks_dir / f"PART_CVII_pair_verification_{e1}_{r1}_{e2}_{r2}_{ts}.json"
        if args.dry_run:
            print("Dry run: would verify pair", (e1, r1, e2, r2))
            skipped.append(((e1, r1, e2, r2), "DRY_RUN"))
            continue
        res = run_forced_seed(
            seed_path, k=args.k, time_limit=args.time_limit, seed=args.seed
        )
        sol_json_path = Path.cwd() / checks_dir / "PART_CVII_e8_embedding_cpsat.json"
        sol_json = None
        if sol_json_path.exists():
            sol_json = json.loads(sol_json_path.read_text(encoding="utf-8"))
        entry = {
            "pair": [e1, r1, e2, r2],
            "local_source": src,
            "solver_process": {
                "returncode": res.get("returncode"),
                "stdout": res.get("stdout"),
                "stderr": res.get("stderr"),
            },
            "solver_json": sol_json,
            "timestamp": ts,
        }
        outp.write_text(json.dumps(entry, indent=2), encoding="utf-8")
        print("Wrote verification artifact", outp)
        # check solver status
        status = sol_json.get("status") if sol_json else None
        if status == "INFEASIBLE":
            appended = append_forbid(
                forbid_path, [int(e1), int(e2)], [int(r1), int(r2)], src
            )
            if appended:
                print("Appended forbids entry for pair", (e1, e2), "-> roots", (r1, r2))
            else:
                print(
                    "Forbid entry already present for pair",
                    (e1, e2),
                    "-> roots",
                    (r1, r2),
                )
            verified.append(((e1, r1, e2, r2), str(outp)))
            if args.commit:
                # mirror and attempt auto-commit
                art = Path.cwd() / "committed_artifacts" / forbid_path.name
                art.parent.mkdir(parents=True, exist_ok=True)
                art.write_text(
                    forbid_path.read_text(encoding="utf-8"), encoding="utf-8"
                )
                try:
                    from git_auto_keep import git_add_commit

                    ok, msg = git_add_commit(
                        [str(art)], f"Auto-register verified pair forbid: {e1}-{e2}"
                    )
                    print("Auto-commit result:", ok, msg)
                except Exception as e:
                    print("Auto-commit failed:", e)
        else:
            print(
                "Solver did not return INFEASIBLE for pair",
                (e1, r1, e2, r2),
                "status=",
                status,
            )

    print("\nSummary:")
    print("Verified (appended to forbids):", len(verified))
    print("Skipped (dry-run or other):", len(skipped))


if __name__ == "__main__":
    main()
