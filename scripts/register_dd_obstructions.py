#!/usr/bin/env python3
"""Collect unique dd_shrink results, verify via global CP-SAT, and record obstruction artifacts.

Usage:
  python scripts/register_dd_obstructions.py --k 40 --time-limit 30 --seed 212 --commit

"""
from __future__ import annotations

import glob
import json
import subprocess
import time
from collections import defaultdict
from pathlib import Path

BASE = Path.cwd()
CHECKS = BASE / "checks"
ART = BASE / "committed_artifacts"

import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--commit", action="store_true", help="Commit artifact changes to git"
)
parser.add_argument(
    "--push",
    action="store_true",
    help="Push commits to origin after commit (only staged artifacts will be pushed)",
)
parser.add_argument(
    "--git-remote", type=str, default="origin", help="Git remote to push to"
)
parser.add_argument(
    "--git-branch",
    type=str,
    default=None,
    help="Optional git branch to push to (default: current branch)",
)
args = parser.parse_args()


# helpers
def load_json(p):
    return json.loads(open(p, encoding="utf-8").read())


# bookkeeping for optional commit/push
commit_files = []
commit_sets = []

# collect dd_shrink outputs
outs = glob.glob(str(CHECKS / "PART_CVII_dd_shrink_result_*.json"))
by_result = defaultdict(list)
for p in outs:
    try:
        j = load_json(p)
    except Exception as e:
        print("Skipping malformed dd_shrink_result (cannot parse JSON):", p, "->", e)
        continue
    res = tuple(sorted(j.get("result", [])))
    by_result[res].append({"path": p, "json": j})

print("Found", len(by_result), "unique dd_shrink results")

# load bij
bij = load_json(str(ART / "PART_CVII_e8_bijection_intermediate_1770491863.json"))[
    "bijection"
]
bij = {int(k): int(v) for k, v in bij.items()}


# helper to write seed
def write_seed_for_edges(edges, outpath):
    seed_edges = []
    for e in edges:
        if e in bij:
            seed_edges.append({"edge_index": int(e), "root_index": int(bij[e])})
    out = {"seed_edges": seed_edges, "rotation": None}
    open(outpath, "w", encoding="utf-8").write(json.dumps(out, indent=2))
    return outpath


# helper to write seed from an explicit seed_map (edge->root)
def write_seed_for_map(seed_map, edges, outpath):
    seed_edges = []
    for e in edges:
        if e in seed_map:
            seed_edges.append({"edge_index": int(e), "root_index": int(seed_map[e])})
    out = {"seed_edges": seed_edges, "rotation": None}
    open(outpath, "w", encoding="utf-8").write(json.dumps(out, indent=2))
    return outpath


# helper to get edge endpoints from adjacency
def edge_endpoints(edge_idx):
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


# load e8 roots (make import robust when run via runpy)
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from e8_embedding_group_theoretic import (
    generate_e8_roots,
    vec_add,
    vec_dot,
    vec_neg,
    vec_sub,
)

roots = generate_e8_roots()

# Result artifacts will be written to checks/PART_CVII_dd_pair_obstruction_<ts>.json
for res, entries in by_result.items():
    if not res:
        continue
    ts = int(time.time())
    print("\nProcessing result", res, "from", len(entries), "dd outputs")

    # Prefer seed artifact or seed_map from dd_shrink results when available
    seed_json_path = None
    seed_source_used = None
    for e in entries:
        j = e.get("json")
        if j is None:
            try:
                j = load_json(e["path"])
            except Exception:
                j = None
        if not j:
            continue
        # prefer explicit seed_artifact
        sa = j.get("seed_artifact")
        if sa:
            sp = Path(sa)
            if not sp.exists():
                sp = Path.cwd() / sp if not sp.is_absolute() else sp
                if not sp.exists():
                    sp = Path.cwd() / "committed_artifacts" / Path(sa).name
            if sp.exists():
                seed_json_path = sp
                seed_source_used = f"dd_shrink_result_seed_artifact:{sp}"
                break
        # else try seed_map
        smap = j.get("seed_map")
        if smap:
            try:
                smap_int = {int(k): int(v) for k, v in smap.items()}
                tmp_seed = CHECKS / f"_tmp_seed_dd_verify_{ts}_from_map.json"
                write_seed_for_map(smap_int, res, tmp_seed)
                seed_json_path = tmp_seed
                seed_source_used = "dd_shrink_result_seed_map"
                break
            except Exception:
                pass

    # fallback to bijection mapping
    if seed_json_path is None:
        seed_path = CHECKS / f"_tmp_seed_dd_verify_{ts}.json"
        write_seed_for_edges(res, seed_path)
        seed_json_path = seed_path
        seed_source_used = "bijection_map"

    # run global CP-SAT check with the chosen seed JSON
    cmd = [
        "py",
        "-3",
        "scripts/solve_e8_embedding_cpsat.py",
        "--seed-json",
        str(seed_json_path),
        "--k",
        "40",
        "--time-limit",
        "30",
        "--seed",
        "212",
        "--force-seed",
    ]
    print("Running solver with seed source", seed_source_used, ":", " ".join(cmd))
    proc = subprocess.run(
        cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    # read solver JSON output
    sol_json_path = CHECKS / "PART_CVII_e8_embedding_cpsat.json"
    sol_json = None
    if sol_json_path.exists():
        sol_json = load_json(sol_json_path)

    # try to extract verified roots from the seed JSON used for verification
    verified_roots = None
    try:
        if seed_json_path and Path(seed_json_path).exists():
            sj = load_json(str(seed_json_path))
            seed_edges = sj.get("seed_edges", [])
            seed_map = {
                int(s["edge_index"]): int(s["root_index"])
                for s in seed_edges
                if "edge_index" in s and "root_index" in s
            }
            verified_roots = [seed_map.get(int(e), None) for e in res]
    except Exception:
        verified_roots = None

    # decide which roots to record: prefer verified roots from the seed used to verify, otherwise fall back to bijection mapping
    roots_for_artifact = None
    if verified_roots and all(r is not None for r in verified_roots):
        roots_for_artifact = verified_roots
    else:
        roots_for_artifact = [bij[e] for e in res]

    # build artifact
    art = {
        "dd_shrink_results": [e["path"] for e in entries],
        "set": list(res),
        "edges": list(res),
        "vertices": [list(edge_endpoints(e)) for e in res],
        "roots": roots_for_artifact,
        "root_vectors": {str(r): roots[r] for r in roots_for_artifact if r is not None},
        "dot_products": None,
        "sum_is_root": None,
        "diff_is_root": None,
        "solver_check": str(sol_json_path) if sol_json_path.exists() else None,
        "solver_status": sol_json.get("status") if sol_json else None,
        "seed_source_used": seed_source_used,
        "used_seed_json": str(seed_json_path),
        "verified_roots": verified_roots,
        "notes": "Auto-verified by register_dd_obstructions.py",
    }
    if len(res) == 2:
        a, b = res
        if (
            roots_for_artifact
            and roots_for_artifact[0] is not None
            and roots_for_artifact[1] is not None
        ):
            ra = roots[roots_for_artifact[0]]
            rb = roots[roots_for_artifact[1]]
            art["dot_products"] = vec_dot(ra, rb)
            # Use vec_neg to check negations properly
            art["sum_is_root"] = (vec_add(ra, rb) in roots) or (
                vec_neg(vec_add(ra, rb)) in roots
            )
            art["diff_is_root"] = (vec_sub(ra, rb) in roots) or (
                vec_neg(vec_sub(ra, rb)) in roots
            )
    stamp = int(time.time())
    outp = CHECKS / f"PART_CVII_dd_pair_obstruction_{stamp}.json"
    open(outp, "w", encoding="utf-8").write(json.dumps(art, indent=2))
    print("Wrote", outp)
    # mirror to committed_artifacts
    art_out = ART / outp.name
    art_out.write_text(open(outp, encoding="utf-8").read(), encoding="utf-8")
    print("Mirrored to", art_out)
    # record artifact for eventual commit/push
    try:
        commit_files.append(str(art_out))
        commit_sets.append(list(res))
    except Exception:
        pass

    # append to forbids list if solver returned INFEASIBLE
    if sol_json and sol_json.get("status") == "INFEASIBLE":
        forb_path = CHECKS / "PART_CVII_forbids.json"
        forb = {"obstruction_sets": []}
        if forb_path.exists():
            forb = load_json(forb_path)
        entry = {
            "set": list(res),
            "roots": [bij[e] for e in res],
            "timestamp": int(time.time()),
            "source_dd": [e["path"] for e in entries],
            "seed_source_used": seed_source_used,
        }
        forb.setdefault("obstruction_sets", []).append(entry)
        open(forb_path, "w", encoding="utf-8").write(json.dumps(forb, indent=2))
        print("Appended to forbids:", forb_path)
        # mirror forbids too
        (ART / forb_path.name).write_text(
            open(forb_path, encoding="utf-8").read(), encoding="utf-8"
        )
        print(
            "Mirrored forbids to committed_artifacts"
        )  # record forbids file for commit/push
        try:
            commit_files.append(str(ART / forb_path.name))
        except Exception:
            pass
# optionally commit and push the artifacts we created
if args.commit:
    commit_files = sorted(set(commit_files))
    if commit_files:
        print("Staging files for commit:", commit_files)
        add_proc = subprocess.run(
            ["git", "add"] + commit_files,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if add_proc.returncode != 0:
            print("git add failed:", add_proc.stderr)
        else:
            commit_msg = (
                f"Auto-registered {len(commit_sets)} dd_pair_obstruction(s): "
                + ", ".join(["[" + ",".join(map(str, s)) + "]" for s in commit_sets])
            )
            cp = subprocess.run(
                ["git", "commit", "-m", commit_msg],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if cp.returncode != 0:
                print("git commit failed:", cp.stderr)
            else:
                print("Committed:", cp.stdout)
                if args.push:
                    # don't push if README.md or memory.md show up in worktree
                    st = subprocess.run(
                        ["git", "status", "--porcelain"],
                        stdout=subprocess.PIPE,
                        text=True,
                    ).stdout
                    if "README.md" in st or "memory.md" in st:
                        print(
                            "Detected modifications to README.md or memory.md in working tree; skipping push for safety."
                        )
                    else:
                        branch = args.git_branch
                        if not branch:
                            brp = subprocess.run(
                                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                                stdout=subprocess.PIPE,
                                text=True,
                            )
                            branch = brp.stdout.strip()
                        p = subprocess.run(
                            (
                                ["git", args.git_remote, "push", branch]
                                if False
                                else ["git", "push", args.git_remote, branch]
                            ),
                            check=False,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                        )
                        if p.returncode != 0:
                            print("git push failed:", p.stderr)
                        else:
                            print("Pushed to remote:", p.stdout)

print("\nDone")
