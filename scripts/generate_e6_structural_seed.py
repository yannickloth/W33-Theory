#!/usr/bin/env python3
"""Generate a decomposition-guided seed mapping W33 edges -> E8 roots.

Heuristic algorithm:
 - Use WE6 true action artifact (artifacts/we6_true_action.json) to compute exact W(E6) orbits
 - Partition E8 roots into pools: e6_adj (72), 6 x 27-orbits (162), 6 singletons (6)
 - Decompose W33 edges into (incident, h12_internal, h27_internal, cross)
 - Greedily assign roots from preferred pools to each edge class (ensure bijection)
 - Optionally run local_repair and backtrack on the produced seed

Outputs:
 - checks/PART_CVII_e8_seed_e6_structural.json (seed_edges list) and
 - checks/seed_e6_struct.json (matching result from check_bipartite_matching)
"""
from __future__ import annotations

import argparse
import json
import random
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[1]
ART_WE6 = ROOT / "artifacts" / "we6_true_action.json"
OUT_SEED = ROOT / "checks" / "PART_CVII_e8_seed_e6_structural.json"
OUT_MATCH = ROOT / "checks" / "match_e6_struct.json"
OUT_SEED_FROM_MATCH = ROOT / "checks" / "seed_e6_struct.json"

# import W33 builder
from e8_embedding_group_theoretic import build_w33, generate_e8_roots

Edge = Tuple[int, int]


def load_we6_artifact(path: Path):
    j = json.loads(path.read_text(encoding="utf-8"))
    roots_int2 = j["roots_int2"]
    gen_perms = j["we6_generators"]
    # convert perms to 0-based lists
    perms = [[p - 1 for p in perm] for perm in gen_perms]
    return roots_int2, perms


def compute_orbits_from_perms(n, perms):
    seen = [False] * n
    orbits = []
    for i in range(n):
        if seen[i]:
            continue
        orb = {i}
        stack = [i]
        while stack:
            x = stack.pop()
            for perm in perms:
                y = perm[x]
                if y not in orb:
                    orb.add(y)
                    stack.append(y)
                # also consider inverse by scanning perm indices is expensive; rely on closure of group generated
        for v in orb:
            seen[v] = True
        orbits.append(sorted(list(orb)))
    orbits_sorted = sorted(orbits, key=lambda o: len(o), reverse=True)
    return orbits_sorted


def decompose_edges(n, adj):
    neigh0 = set(adj[0])
    h27 = set(range(n)) - neigh0 - {0}
    incident = []
    h12_internal = []
    h27_internal = []
    cross = []
    edges_list = []
    for i in range(n):
        for j in adj[i]:
            if j <= i:
                continue
            edges_list.append((i, j))
            if i == 0:
                incident.append((i, j))
            elif i in neigh0 and j in neigh0:
                h12_internal.append((i, j))
            elif i in h27 and j in h27:
                h27_internal.append((i, j))
            else:
                cross.append((i, j))
    return {
        "incident": incident,
        "h12_internal": h12_internal,
        "h27_internal": h27_internal,
        "cross": cross,
        "edges": edges_list,
    }


def pick_and_assign(pool: List[int], count: int, rng: random.Random, used: set):
    """Pick `count` unused items from pool (shuffled) and mark them used."""
    avail = [p for p in pool if p not in used]
    if len(avail) < count:
        # pool exhausted; allow fallback to any unused
        avail = [p for p in range(240) if p not in used]
    rng.shuffle(avail)
    picks = avail[:count]
    for p in picks:
        used.add(p)
    return picks


def build_seed(
    seed_out: Path,
    seed: int = 42,
    repair: bool = False,
    local_time: int = 120,
    run_check: bool = True,
):
    rng = random.Random(seed)
    n, vertices, adj, edges = build_w33()
    decomposition = decompose_edges(n, adj)

    roots_int2, perms = load_we6_artifact(ART_WE6)
    orbits = compute_orbits_from_perms(len(roots_int2), perms)
    # group orbits by size
    size2orbits = defaultdict(list)
    for orb in orbits:
        size2orbits[len(orb)].append(orb)

    # expected groups: 72 (1 orbit), 27 (6 orbits), 1 (6 orbits)
    e6_orbit = size2orbits.get(72, [])[0] if size2orbits.get(72) else []
    orbs27 = size2orbits.get(27, [])
    singletons = [o[0] for o in size2orbits.get(1, [])]

    # Flatten 27-orbit pools
    pool_27 = [i for orb in orbs27 for i in orb]

    # Build pools (heuristic)
    pool_e6 = list(e6_orbit)
    pool_27 = list(pool_27)
    pool_single = list(singletons)
    pool_all = set(range(240))

    used = set()
    edge_to_root = {}

    # Assign H27 internal edges -> prefer pool_27 (108 edges)
    h27_edges = decomposition["h27_internal"]
    picks = pick_and_assign(pool_27, len(h27_edges), rng, used)
    for e, r in zip(h27_edges, picks):
        idx = edges.index(e)
        edge_to_root[idx] = int(r)

    # Assign H12 internal edges (12) -> prefer e6 pool
    h12_edges = decomposition["h12_internal"]
    picks = pick_and_assign(pool_e6, len(h12_edges), rng, used)
    for e, r in zip(h12_edges, picks):
        idx = edges.index(e)
        edge_to_root[idx] = int(r)

    # Assign incident edges (12) -> prefer singletons + leftover e6
    inc_edges = decomposition["incident"]
    picks1 = pick_and_assign(
        pool_single, min(len(pool_single), len(inc_edges)), rng, used
    )
    remaining = len(inc_edges) - len(picks1)
    picks2 = pick_and_assign(pool_e6, remaining, rng, used)
    picks = picks1 + picks2
    for e, r in zip(inc_edges, picks):
        idx = edges.index(e)
        edge_to_root[idx] = int(r)

    # Assign cross edges (108) -> fill from remaining unused roots
    cross_edges = decomposition["cross"]
    picks = pick_and_assign(list(pool_all), len(cross_edges), rng, used)
    for e, r in zip(cross_edges, picks):
        idx = edges.index(e)
        edge_to_root[idx] = int(r)

    # Sanity: ensure all edges assigned
    assert len(edge_to_root) == 240

    seed_obj = {
        "seed_edges": [
            {"edge_index": int(k), "root_index": int(v)}
            for k, v in sorted(edge_to_root.items())
        ]
    }
    seed_out.parent.mkdir(parents=True, exist_ok=True)
    seed_out.write_text(json.dumps(seed_obj, indent=2), encoding="utf-8")
    print("Wrote", seed_out)

    # Run bipartite check & write match/seed
    if run_check:
        cmd = [
            "py",
            "-3",
            "scripts/check_bipartite_matching.py",
            "--mapping-json",
            str(seed_out),
            "--write-match",
            str(OUT_MATCH),
            "--write-seed",
            str(OUT_SEED_FROM_MATCH),
            "--check-triangles",
            "--verbose",
        ]
        print("Running:", " ".join(cmd))
        subprocess.run(" ".join(cmd), shell=True)

    if repair:
        # run local_repair on produced seed (from match output)
        cmd = [
            "py",
            "-3",
            "-m",
            "scripts.local_repair_matching",
            "--k",
            "60",
            "--time-limit",
            str(local_time),
            "--seed-json",
            str(OUT_SEED_FROM_MATCH),
            "--tries",
            "500000",
        ]
        print("Running local_repair:", " ".join(cmd))
        subprocess.run(" ".join(cmd), shell=True)

    return seed_out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=str, default=str(OUT_SEED))
    parser.add_argument("--repair", action="store_true")
    parser.add_argument("--local-time", type=int, default=120)
    parser.add_argument(
        "--no-check",
        action="store_true",
        help="Skip running check_bipartite_matching and local repair",
    )
    args = parser.parse_args()

    build_seed(
        Path(args.output),
        seed=args.seed,
        repair=args.repair,
        local_time=args.local_time,
        run_check=not args.no_check,
    )
