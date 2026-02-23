#!/usr/bin/env python3
"""Randomly sample simple cycles in W33 and report CA rules.

This script does *not* attempt to enumerate all cycles.  Instead it generates
random closed walks of a given length and keeps only those that are simple
(no repeated vertices).  Each sampled cycle is tested with the same
mechanism as `w33_universal_search.py` to determine whether it corresponds to
an elementary CA rule.  This is a quick-and-dirty way to look for rare rules
like Rule 110 without exhausting the entire graph.

Usage:
    python scripts/random_cycle_search.py --length 12 --samples 5000

You can also specify `--rule R` to stop early when a cycle implementing rule
R is found.
"""

from __future__ import annotations

import argparse
import random
import json
from typing import List

import networkx as nx

from w33_universal_search import build_graph_and_l1, gf2_projector, is_circulant, rule_from_row


def sample_random_cycle(G: nx.Graph, length: int, rng: random.Random) -> List[int] | None:
    # simple random walk that returns to start after `length` steps, reject if
    # any vertex repeats except start==end
    if length < 3:
        return None
    start = rng.choice(list(G.nodes()))
    path = [start]
    current = start
    for _ in range(length - 1):
        nbrs = list(G[current])
        if not nbrs:
            return None
        current = rng.choice(nbrs)
        path.append(current)
    if current != start:
        return None
    # check simplicity
    if len(set(path[:-1])) != length - 1:
        return None
    return path[:-1]  # return cycle without duplicated last vertex


def test_cycle(indices: List[int]) -> int | None:
    edges, L1, edge_idx = build_graph_and_l1()
    U2 = gf2_projector(L1)
    try:
        M = U2[tuple(indices), :][:, tuple(indices)]
    except Exception:
        return None
    if not is_circulant(M):
        return None
    return rule_from_row(M[0])


def main():
    parser = argparse.ArgumentParser(description="Random cycle rule search")
    parser.add_argument("--length", type=int, default=10,
                        help="cycle length to sample")
    parser.add_argument("--samples", type=int, default=1000,
                        help="number of random trials")
    parser.add_argument("--rule", type=int, choices=range(0,256),
                        help="stop when this rule is found")
    parser.add_argument("--output", default=None,
                        help="optional JSON file to record all found cycles")
    args = parser.parse_args()

    edges, L1, edge_idx = build_graph_and_l1()
    # build vertex graph
    Gv = nx.Graph()
    npoints = max(max(u, v) for u, v in edges) + 1
    Gv.add_nodes_from(range(npoints))
    for u, v in edges:
        Gv.add_edge(u, v)

    rng = random.Random(42)
    found = []
    for i in range(args.samples):
        cyc = sample_random_cycle(Gv, args.length, rng)
        if cyc is None:
            continue
        rule = test_cycle(cyc)
        if rule is not None:
            found.append((cyc, rule))
            print(f"sample {i}: rule {rule} on cycle {cyc}")
            if args.rule is not None and rule == args.rule:
                break
    if args.output:
        json.dump(found, open(args.output, "w"))
    print(f"done, found {len(found)} circulant cycles")


if __name__ == "__main__":
    main()
