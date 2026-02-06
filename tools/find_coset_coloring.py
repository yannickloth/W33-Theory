#!/usr/bin/env python3
"""
Find a 3-coloring of the 27 coset nodes so that every coset triad contains
exactly one node of each color. Write result to artifacts/coset_coloring.json
"""
import json
from collections import defaultdict
from itertools import combinations, product
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

G_matrix = np.array(
    [
        [1, 0, 0, 0, 0, 0, 1, 1, 2, 2, 1, 2],
        [0, 1, 0, 0, 0, 0, 1, 2, 1, 2, 2, 1],
        [0, 0, 1, 0, 0, 0, 2, 1, 1, 1, 2, 2],
        [0, 0, 0, 1, 0, 0, 2, 2, 1, 1, 1, 2],
        [0, 0, 0, 0, 1, 0, 1, 2, 2, 1, 1, 2],
        [0, 0, 0, 0, 0, 1, 2, 1, 2, 2, 1, 1],
    ]
)
M = np.array([[2, 2, 1, 2, 1, 2], [0, 2, 2, 0, 2, 1]], dtype=int)
messages = list(tuple(m) for m in product(range(3), repeat=6))

kernel = [m for m in messages if (M @ np.array(m) % 3 == 0).all()]

# find kernel basis
basis = []
for m in kernel:
    if all(x == 0 for x in m):
        continue
    if not basis:
        basis.append(m)
        continue

    def in_span(m, basis):
        if len(basis) == 1:
            for a in range(3):
                if tuple((a * basis[0][i]) % 3 for i in range(6)) == m:
                    return True
            return False
        if len(basis) == 2:
            for a in range(3):
                for b in range(3):
                    if (
                        tuple(
                            ((a * basis[0][i] + b * basis[1][i]) % 3) for i in range(6)
                        )
                        == m
                    ):
                        return True
            return False
        if len(basis) == 3:
            for a in range(3):
                for b in range(3):
                    for c in range(3):
                        if (
                            tuple(
                                (
                                    (
                                        a * basis[0][i]
                                        + b * basis[1][i]
                                        + c * basis[2][i]
                                    )
                                    % 3
                                )
                                for i in range(6)
                            )
                            == m
                        ):
                            return True
            return False
        return False

    if not in_span(m, basis):
        basis.append(m)
    if len(basis) == 4:
        break
W_basis = basis[:3]

# cosets
W = set()
for a, b, c in product(range(3), repeat=3):
    W.add(
        tuple(
            (a * W_basis[0][i] + b * W_basis[1][i] + c * W_basis[2][i]) % 3
            for i in range(6)
        )
    )
used = set()
cosets = []
for m in messages:
    if m in used:
        continue
    cosets.append(m)
    for w in W:
        used.add(tuple((m[i] + w[i]) % 3 for i in range(6)))

# cw
cw27 = [tuple((np.array(m) @ G_matrix % 3).tolist()) for m in cosets]
# triads
coset_triads = []
for i, j, k in combinations(range(27), 3):
    if (
        sum(x != y for x, y in zip(cw27[i], cw27[j])) == 6
        and sum(x != y for x, y in zip(cw27[i], cw27[k])) == 6
        and sum(x != y for x, y in zip(cw27[j], cw27[k])) == 6
    ):
        coset_triads.append((i, j, k))

# adjacency
adj_triads_by_node = [[] for _ in range(27)]
for t in coset_triads:
    for v in t:
        adj_triads_by_node[v].append(t)

# backtracking for 3-coloring
N = 27
colors = [-1] * N
nodes = list(range(N))
# sort nodes by degree
nodes.sort(key=lambda x: len(adj_triads_by_node[x]), reverse=True)

sol = None
steps = 0


def valid_assign(node, color):
    # check triads containing node
    for tri in adj_triads_by_node[node]:
        used_colors = set()
        for v in tri:
            if v == node:
                used_colors.add(color)
            elif colors[v] != -1:
                if colors[v] == color:
                    return False
                used_colors.add(colors[v])
        # if all three assigned, they must be {0,1,2}
        if all(colors[v] != -1 or v == node for v in tri):
            if used_colors != {0, 1, 2}:
                return False
    return True


def backtrack(idx):
    global steps, sol
    steps += 1
    if steps % 100000 == 0:
        print("steps", steps)
    if idx == len(nodes):
        sol = colors.copy()
        return True
    node = nodes[idx]
    if colors[node] != -1:
        return backtrack(idx + 1)
    for ccol in range(3):
        if not valid_assign(node, ccol):
            continue
        colors[node] = ccol
        if backtrack(idx + 1):
            return True
        colors[node] = -1
    return False


ok = backtrack(0)
print("coloring found", ok)
if not ok:
    raise RuntimeError("No 3-coloring found")

out = ROOT / "artifacts" / "coset_coloring.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps({"colors": colors}, indent=2), encoding="utf-8")
print("Wrote", out)
