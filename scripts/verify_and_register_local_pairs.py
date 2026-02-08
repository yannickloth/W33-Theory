#!/usr/bin/env python3
"""Verify local hotspot INFEASIBLE pairs with the global CP-SAT solver and register canonical forbids.

Usage:
  python scripts/verify_and_register_local_pairs.py --feasibility checks/PART_CVII_local_hotspot_feasibility_37_38_*.json --k 40 --time-limit 30

- Scans the given local-feasibility JSON files for pair tests with status=="INFEASIBLE".
- For each INFEASIBLE pair, builds a seed JSON forcing the two edge->root assignments and runs
  scripts/solve_e8_embedding_cpsat.py with --force-seed to verify global infeasibility.
- If the global solver returns INFEASIBLE, append a canonical obstruction entry to
  checks/PART_CVII_forbids.json and write an artifact checks/PART_CVII_pair_obstruction_<ts>.json
"""
from __future__ import annotations

import argparse
import glob
import json
import logging
import subprocess
import time
import traceback
from collections import defaultdict
from pathlib import Path

BASE = Path.cwd()
CHECKS = BASE / "checks"
ART = BASE / "committed_artifacts"
ART.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# helpers


def load_json(p: Path):
    return json.loads(open(p, encoding="utf-8").read())


def write_seed_for_pair(e1: int, r1: int, e2: int, r2: int, outpath: Path):
    seed_edges = [
        {"edge_index": int(e1), "root_index": int(r1)},
        {"edge_index": int(e2), "root_index": int(r2)},
    ]
    out = {"seed_edges": seed_edges, "rotation": None}
    outpath.write_text(json.dumps(out, indent=2), encoding="utf-8")
    return outpath


# helper to get edge endpoints from adjacency (copied from register_dd_obstructions.py)
def edge_endpoints(edge_idx: int):
    adj = []
    with open(CHECKS.parent / "W33_adjacency_matrix.txt", encoding="utf-8") as f:
        for line in f:
            row = [int(x) for x in line.strip().split()]
            adj.append(row)
    n = len(adj)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i][j] == 1:
                edges.append((i, j))
    if edge_idx < 0 or edge_idx >= len(edges):
        return None
    return edges[edge_idx]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--feasibility",
        type=str,
        required=True,
        help="Glob or file path for local_hotspot_feasibility json outputs",
    )
    parser.add_argument("--k", type=int, default=40)
    parser.add_argument("--time-limit", type=float, default=30.0)
    parser.add_argument("--seed", type=int, default=212)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--auto-commit", action="store_true")
    parser.add_argument(
        "--forbid-json", type=str, default=str(CHECKS / "PART_CVII_forbids.json")
    )
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()

    files = (
        sorted(glob.glob(args.feasibility))
        if "*" in args.feasibility or "?" in args.feasibility
        else [args.feasibility]
    )
    if not files:
        raise SystemExit("No feasibility files found for pattern: " + args.feasibility)

    forb_path = Path(args.forbid_json)
    forb = {"obstruction_sets": []}
    if forb_path.exists():
        try:
            forb = load_json(forb_path)
        except Exception as e:
            logging.warning("Failed to parse existing forbids JSON: %s", e)

    # gather pairs to verify
    pairs_to_verify = []  # tuples (src_file, idx, e1,r1,e2,r2)
    for f in files:
        j = load_json(Path(f))
        tests = j.get("tests", [])
        for idx, t in enumerate(tests):
            # accept statuses that indicate local solver found infeasible
            if t.get("status") == "INFEASIBLE" and t.get("pair"):
                p = t["pair"]
                if len(p) == 4:
                    pairs_to_verify.append(
                        (f, idx, int(p[0]), int(p[1]), int(p[2]), int(p[3]))
                    )

    logging.info("Found %d local INFEASIBLE pairs to verify", len(pairs_to_verify))
    if not pairs_to_verify:
        return

    for i, (src, tidx, e1, r1, e2, r2) in enumerate(pairs_to_verify, start=1):
        logging.info(
            "Verifying %d/%d: file=%s testidx=%s pair=(%d,%d,%d,%d)",
            i,
            len(pairs_to_verify),
            src,
            tidx,
            e1,
            r1,
            e2,
            r2,
        )

        # skip if this pair is already in forbids
        already = False
        for entry in forb.get("obstruction_sets", []):
            if entry.get("set") == [e1, e2] or entry.get("set") == [e2, e1]:
                logging.info("Pair already present in forbids; skipping")
                already = True
                break
        if already:
            continue

        ts = int(time.time())
        seed_path = CHECKS / f"_tmp_seed_pair_verify_{i}_{ts}.json"
        write_seed_for_pair(e1, r1, e2, r2, seed_path)
        if args.dry_run:
            logging.info("Dry-run: would run global CP-SAT with seed %s", seed_path)
            continue

        cmd = [
            "py",
            "-3",
            "-X",
            "utf8",
            "scripts/solve_e8_embedding_cpsat.py",
            "--seed-json",
            str(seed_path),
            "--k",
            str(args.k),
            "--time-limit",
            str(args.time_limit),
            "--seed",
            str(args.seed),
            "--force-seed",
        ]
        logging.info("Running solver: %s", " ".join(cmd))
        try:
            proc = subprocess.run(
                cmd,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=max(10, int(args.time_limit) + 10),
            )
            logging.debug("Solver stdout: %s", proc.stdout)
            logging.debug("Solver stderr: %s", proc.stderr)
        except subprocess.TimeoutExpired as e:
            logging.error("Solver timeout for pair %s: %s", (e1, r1, e2, r2), e)
            continue
        except Exception as e:
            logging.exception("Solver subprocess failed: %s", e)
            continue

        # read solver JSON output
        sol_json_path = CHECKS / "PART_CVII_e8_embedding_cpsat.json"
        sol_json = None
        if sol_json_path.exists():
            try:
                sol_json = load_json(sol_json_path)
            except Exception:
                logging.exception("Failed to read solver json at %s", sol_json_path)

        art = {
            "source_file": str(src),
            "source_test_index": tidx,
            "set": [e1, e2],
            "edges": [e1, e2],
            "roots": [r1, r2],
            "seed_path": str(seed_path),
            "solver_check": str(sol_json_path) if sol_json_path.exists() else None,
            "solver_status": sol_json.get("status") if sol_json else None,
            "timestamp": ts,
        }

        # compute vector checks if possible (optional)
        try:
            from e8_embedding_group_theoretic import (
                generate_e8_roots,
                vec_add,
                vec_dot,
                vec_neg,
                vec_sub,
            )

            roots = generate_e8_roots()
            a = roots[int(r1)]
            b = roots[int(r2)]
            art["dot_products"] = vec_dot(a, b)
            art["sum_is_root"] = (vec_add(a, b) in roots) or (
                vec_neg(vec_add(a, b)) in roots
            )
            art["diff_is_root"] = (vec_sub(a, b) in roots) or (
                vec_neg(vec_sub(a, b)) in roots
            )
        except Exception:
            logging.debug(
                "Could not compute explicit root vector checks", exc_info=True
            )

        outp = CHECKS / f"PART_CVII_pair_obstruction_{ts}_{i}.json"
        outp.write_text(json.dumps(art, indent=2), encoding="utf-8")
        logging.info("Wrote pair artifact: %s", outp)
        (ART / outp.name).write_text(outp.read_text(encoding="utf-8"), encoding="utf-8")
        logging.info("Mirrored artifact to %s", ART / outp.name)

        # append to forbids if solver returned INFEASIBLE
        if sol_json and sol_json.get("status") == "INFEASIBLE":
            forb_entry = {
                "set": [e1, e2],
                "roots": [r1, r2],
                "timestamp": int(time.time()),
                "source_local": src,
            }
            forb.setdefault("obstruction_sets", []).append(forb_entry)
            forb_path.write_text(json.dumps(forb, indent=2), encoding="utf-8")
            logging.info("Appended forbids entry to %s", forb_path)
            (ART / forb_path.name).write_text(
                forb_path.read_text(encoding="utf-8"), encoding="utf-8"
            )
            logging.info("Mirrored forbids to committed_artifacts")

            if args.auto_commit:
                try:
                    from git_auto_keep import git_add_commit

                    artifact = ART / forb_path.name
                    ok, msg = git_add_commit(
                        [str(artifact)], f"Add pair forbid {e1}-{e2}"
                    )
                    logging.info("Auto-commit result: %s %s", ok, msg)
                except Exception as e:
                    logging.exception("Auto-commit failed: %s", e)

    logging.info("Done")


if __name__ == "__main__":
    main()
