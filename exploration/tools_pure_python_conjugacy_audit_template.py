#!/usr/bin/env python3
"""Template for auditing conjugacy of two permutation actions (degree 120).

Load generator lists from JSON, compute full permutation groups by closure,
then extract invariants (order spectrum, fixed-point counts, orbit
structure).  Write results to JSON and optionally compare the two sets of
invariants to locate obstructions to conjugacy in S_n.

This script is intentionally simple and relies only on networkx for closure
and numpy for basic arithmetic.  It does *not* require Sage or GAP.

Usage example:
    python tools_pure_python_conjugacy_audit_template.py \
        --gen1 artifacts/sp43_edgepair_generators.json \
        --gen2 SP43_TO_WE6_TRUE_FIXED_BUNDLE_v01_2026-02-25/sp43_line_perms_fixed.json

"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict

import numpy as np
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]


def load_generators(path: Path) -> List[List[int]]:
    with open(path) as f:
        data = json.load(f)
    # expect a list of length-120 permutations
    return [list(map(int, perm)) for perm in data]


def group_closure(gens: List[List[int]]) -> List[List[int]]:
    n = len(gens[0])
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    perms = set(tuple(g) for g in gens)
    changed = True
    while changed:
        changed = False
        for p in list(perms):
            for q in gens:
                comp = tuple(p[q[i]] for i in range(n))
                if comp not in perms:
                    perms.add(comp)
                    changed = True
    return [list(p) for p in perms]


def order_of_perm(p: List[int]) -> int:
    visited = [False]*len(p)
    ord = 1
    for i in range(len(p)):
        if not visited[i]:
            length = 0
            j=i
            while not visited[j]:
                visited[j]=True
                j=p[j]
                length+=1
            if length>0:
                ord = np.lcm(ord, length)
    return ord


def fixed_point_count(p: List[int]) -> int:
    return sum(1 for i,v in enumerate(p) if v==i)


def analyze_group(perms: List[List[int]]) -> Dict:
    spectrum = {}
    fixed = {}
    for p in perms:
        o = order_of_perm(p)
        spectrum[o] = spectrum.get(o,0)+1
        fx = fixed_point_count(p)
        fixed.setdefault(o, []).append(fx)
    # compute orbits of action
    n = len(perms[0])
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    for p in perms:
        for i,j in enumerate(p):
            G.add_edge(i,j)
    orbits = list(nx.algorithms.components.strongly_connected_components(G))
    return {"group_order": len(perms),
            "order_spectrum": spectrum,
            "fixed_counts_by_order": fixed,
            "orbit_sizes": sorted(len(o) for o in orbits)}


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--gen1", required=True)
    parser.add_argument("--gen2", required=True)
    parser.add_argument("--output", default="action_conjugacy_obstruction.json")
    args = parser.parse_args()
    g1 = load_generators(Path(args.gen1))
    g2 = load_generators(Path(args.gen2))
    print(f"loading {len(g1)} and {len(g2)} gens")
    G1 = group_closure(g1)
    G2 = group_closure(g2)
    print(f"closure sizes {len(G1)} {len(G2)}")
    info1 = analyze_group(G1)
    info2 = analyze_group(G2)
    out = {"edgepair": info1, "line_fixed": info2}
    Path(args.output).write_text(json.dumps(out, indent=2))
    print("wrote", args.output)

if __name__ == "__main__":
    main()
