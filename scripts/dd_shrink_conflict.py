#!/usr/bin/env python3
"""Delta-debugging shrink (divide-and-conquer) for infeasible conflict sets.

Usage:
  python scripts/dd_shrink_conflict.py --bij committed_artifacts/PART_CVII_e8_bijection_intermediate_1770491863.json --conf checks/PART_CVII_infeasible_block_analysis_quick_merged_1770498926.json --index 0 --max-checks 500 --k 40 --time-limit 30 --seed 212

Writes: checks/PART_CVII_dd_shrink_result_<ts>.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import time
from pathlib import Path
from typing import Iterable, List

print("dd_shrink_conflict module loaded")


# create a simple run log so we can detect that the script started
Path("checks/PART_CVII_dd_shrink_run_log.txt").write_text(
    "dd_shrink_conflict started at " + str(time.time()) + "\n"
)


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


def write_seed_for_edges(bij: dict, edges: Iterable[int], outpath: Path):
    seed_edges = []
    for e in edges:
        if e in bij:
            seed_edges.append({"edge_index": int(e), "root_index": int(bij[e])})
    out = {"seed_edges": seed_edges, "rotation": None}
    outpath.write_text(json.dumps(out, indent=2), encoding="utf-8")
    return outpath


def write_seed_for_map(seed_map: dict, edges: Iterable[int], outpath: Path):
    """Write a seed JSON using an explicit mapping edge->root (seed_map).
    Only includes edges present in the provided edges iterable and in seed_map.
    """
    seed_edges = []
    for e in edges:
        if e in seed_map:
            seed_edges.append({"edge_index": int(e), "root_index": int(seed_map[e])})
    out = {"seed_edges": seed_edges, "rotation": None}
    outpath.write_text(json.dumps(out, indent=2), encoding="utf-8")
    return outpath


def load_seed_map_from_json(seed_json_path: Path):
    try:
        j = json.loads(open(seed_json_path, encoding="utf-8").read())
        se = j.get("seed_edges", [])
        return {
            int(s["edge_index"]): int(s["root_index"])
            for s in se
            if "edge_index" in s and "root_index" in s
        }
    except Exception:
        return {}


def ddmin(
    bij: dict,
    S: List[int],
    k: int,
    time_limit: float,
    seed: int,
    max_checks: int,
    seed_map: dict = None,
):
    """Delta debugging to minimize failing set S.
    Returns a minimal failing subset (not guaranteed minimal w.r.t. checks bound).
    """
    n = 2
    checks = 0

    def test(subset: List[int]):
        nonlocal checks
        checks += 1
        tmp = Path.cwd() / "checks" / f"_tmp_seed_dd_{int(time.time()*1000)}.json"
        if seed_map:
            # Use explicit seed assignments when available (preferred)
            write_seed_for_map(seed_map, subset, tmp)
        else:
            write_seed_for_edges(bij, subset, tmp)
        res = run_forced_seed(tmp, k=k, time_limit=time_limit, seed=seed)
        try:
            tmp.unlink()
        except Exception:
            pass
        j = res.get("json")
        return j and j.get("status") == "INFEASIBLE"

    S = list(S)
    if not test(S):
        return []

    while True:
        if max_checks is not None and checks >= max_checks:
            return S
        if len(S) == 1:
            return S
        subset_size = math.ceil(len(S) / n)
        some_progress = False
        for i in range(0, len(S), subset_size):
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
                return S
        if not some_progress:
            if n >= len(S):
                return S
            n = min(len(S), n * 2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bij", required=True)
    parser.add_argument(
        "--conf", required=True, help="Conflict source JSON (e.g., quick merged)"
    )
    parser.add_argument(
        "--index", type=int, default=0, help="Which conflict entry index to shrink"
    )
    parser.add_argument("--max-checks", type=int, default=1000)
    parser.add_argument("--k", type=int, default=40)
    parser.add_argument("--time-limit", type=float, default=60.0)
    parser.add_argument("--seed", type=int, default=212)
    parser.add_argument(
        "--seed-json",
        type=str,
        default=None,
        help="Optional seed JSON to use for initial and subset checks",
    )
    args = parser.parse_args()

    bij = json.loads(open(args.bij, encoding="utf-8").read())["bijection"]
    bij = {int(k): int(v) for k, v in bij.items()}

    conf_json = json.loads(open(args.conf, encoding="utf-8").read())
    entries = conf_json.get("checked", [])
    if args.index >= len(entries):
        raise SystemExit("Index out of range")
    entry = entries[args.index]
    if "minimal_conflict" not in entry:
        raise SystemExit("No minimal_conflict found in selected entry")

    S = entry["minimal_conflict"]
    print(f"Starting ddmin on conflict of size {len(S)}")

    # Derive a seed map that will be used to build seeds for the initial check and
    # for subset tests. Preference order:
    # 1) CLI --seed-json
    # 2) source pair artifact's explicit seed_path or roots
    # 3) fallback to bijection mapping (for edges in S)
    seed_map = {}
    seed_source = None
    # user-supplied seed JSON takes precedence
    if args.seed_json:
        sjp = Path(args.seed_json)
        if sjp.exists():
            seed_map = load_seed_map_from_json(sjp)
            seed_source = f"seed_json:{sjp}"
    if not seed_map:
        src = entry.get("source")
        if src:
            srcp = Path(src)
            if not srcp.exists():
                srcp = Path.cwd() / src
            if not srcp.exists():
                # try committed_artifacts by name
                srcp = Path.cwd() / "committed_artifacts" / Path(src).name
            if srcp.exists():
                try:
                    print(f"Loaded pair artifact candidate at: {srcp}")
                    pa = json.loads(open(srcp, encoding="utf-8").read())
                    sp = pa.get("seed_path")
                    if sp:
                        spath = Path(sp) if Path(sp).is_absolute() else Path.cwd() / sp
                        if not spath.exists():
                            # try committed_artifacts location
                            spath = Path.cwd() / "committed_artifacts" / Path(sp).name
                        if spath.exists():
                            seed_map = load_seed_map_from_json(spath)
                            seed_source = f"pair_seed_path:{spath}"
                    if (
                        not seed_map
                        and "roots" in pa
                        and ("edges" in pa or "set" in pa)
                    ):
                        edges_list = pa.get("edges") or pa.get("set")
                        roots_list = pa.get("roots")
                        if (
                            edges_list
                            and roots_list
                            and len(edges_list) == len(roots_list)
                        ):
                            seed_map = {
                                int(e): int(r) for e, r in zip(edges_list, roots_list)
                            }
                            seed_source = "pair_artifact_roots"
                except Exception:
                    pass
    if not seed_map:
        seed_map = {int(e): int(bij[int(e)]) for e in S if int(e) in bij}
        seed_source = "bijection_map"

    # write an initial seed JSON (and persist it to committed_artifacts) and test reproducibilty
    tmp_init = (
        Path.cwd() / "checks" / f"_tmp_seed_dd_initial_{int(time.time()*1000)}.json"
    )
    write_seed_for_map(seed_map, S, tmp_init)
    ART = Path.cwd() / "committed_artifacts"
    ART.mkdir(parents=True, exist_ok=True)
    init_seed_art = ART / f"PART_CVII_dd_seed_initial_{int(time.time())}.json"
    init_seed_art.write_text(tmp_init.read_text(encoding="utf-8"), encoding="utf-8")

    init_res = run_forced_seed(
        tmp_init, k=args.k, time_limit=args.time_limit, seed=args.seed
    )
    try:
        tmp_init.unlink()
    except Exception:
        pass
    init_json = init_res.get("json")
    initial_reproducible = bool(init_json and init_json.get("status") == "INFEASIBLE")

    start = time.time()
    result = ddmin(
        bij,
        S,
        k=args.k,
        time_limit=args.time_limit,
        seed=args.seed,
        max_checks=args.max_checks,
        seed_map=seed_map,
    )
    elapsed = time.time() - start

    if not initial_reproducible:
        shrink_status = "not_reproducible"
        notes = "Initial check indicates the conflict is not currently infeasible under the provided bijection/seed."
    else:
        if len(result) == 0:
            shrink_status = "reproducible_but_no_shrink_found"
            notes = (
                "Initial check passed but ddmin did not find a smaller failing subset."
            )
        elif len(result) == len(S):
            shrink_status = "already_minimal"
            notes = "Conflict appears minimal (no strict subset found infeasible)."
        else:
            shrink_status = "shrunk"
            notes = "ddmin found a smaller failing subset."

    out = {
        "source_conf_entry": entry,
        "initial_size": len(S),
        "initial_reproducible": initial_reproducible,
        "shrink_status": shrink_status,
        "result": result,
        "result_size": len(result),
        "checks_limit": int(args.max_checks),
        "time_seconds": elapsed,
        "timestamp": int(time.time()),
        "notes": notes,
        "seed_source": seed_source,
        "seed_artifact": str(init_seed_art) if "init_seed_art" in locals() else None,
        "seed_map": seed_map,
    }

    stamp = int(time.time())
    outpath = Path.cwd() / "checks" / f"PART_CVII_dd_shrink_result_{stamp}.json"
    outpath.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote", outpath)

    # mirror to committed_artifacts
    art = Path.cwd() / "committed_artifacts" / outpath.name
    art.write_text(outpath.read_text(encoding="utf-8"), encoding="utf-8")
    print("Also wrote", art)


if __name__ == "__main__":
    main()
