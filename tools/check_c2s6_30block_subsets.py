#!/usr/bin/env python3
"""Enumerate all 27-subsets of the 30-line C2xS6 block and test for Schlaefli SRG parameters.
Writes artifacts/c2s6_30block_27_candidates.json with any matching subsets.
"""
from __future__ import annotations

import json
from collections import Counter
from itertools import combinations
from pathlib import Path

import networkx as nx
import numpy as np

ROOT = Path(__file__).resolve().parent
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)

from tools.find_schlafli_embedding_in_w33 import (
    build_schlafli_adj,
    compute_w33_lines,
    compute_we6_orbits,
    construct_e8_roots,
    construct_w33_points,
)


def is_srg_27_16_10_8(adj):
    # adj: numpy array 27x27 with 0/1
    n = adj.shape[0]
    if n != 27:
        return False
    degs = adj.sum(axis=1)
    if not np.all(degs == 16):
        return False
    # compute lambda and mu from counts
    # pick a pair of adjacent vertices -> count common neighbors (lambda)
    # pick a pair of non-adjacent vertices -> count common neighbors (mu)
    lam = None
    mu = None
    for i in range(n):
        for j in range(i + 1, n):
            common = int((adj[i] & adj[j]).sum())
            if adj[i, j]:
                if lam is None:
                    lam = common
                elif lam != common:
                    return False
            else:
                if mu is None:
                    mu = common
                elif mu != common:
                    return False
    if lam != 10 or mu != 8:
        return False
    return True


def main():
    # load C2xS6 orbit
    orbits = json.loads(
        (ROOT / "artifacts" / "sage_c2s6_line_orbits.json").read_text(encoding="utf-8")
    )["orbits"]
    block30 = orbits[0]
    assert len(block30) == 30

    # build lines and disjointness graph
    pts = construct_w33_points()
    lines = compute_w33_lines(pts)
    n = len(lines)
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            if set(lines[i]).isdisjoint(set(lines[j])):
                G.add_edge(i, j)

    candidates = []
    total = 0
    for subset in combinations(block30, 27):
        total += 1
        S = list(subset)
        # build adjacency matrix
        adj = np.zeros((27, 27), dtype=int)
        idx = {v: i for i, v in enumerate(S)}
        for a in range(27):
            for b in range(a + 1, 27):
                if G.has_edge(S[a], S[b]):
                    adj[a, b] = adj[b, a] = 1
        if is_srg_27_16_10_8(adj):
            candidates.append({"subset": S})
    out = {
        "block30_size": len(block30),
        "n_checked": total,
        "n_candidates": len(candidates),
        "candidates": candidates,
    }
    (ART / "c2s6_30block_27_candidates.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )
    print("Done. checked", total, "subsets; candidates found:", len(candidates))


if __name__ == "__main__":
    main()
