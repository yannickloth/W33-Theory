#!/usr/bin/env python3
"""Check triangle consistency of a seed JSON file deterministically.

Checks for:
- any triangle where two edges are seeded and the implied third root is inconsistent with a seeded value
- any implied root from two seeded edges that is not a valid E8 root

Prints summary and exits with non-zero code if contradictions found.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Tuple

# Local copies of functions to avoid importing OR-Tools during checks
import numpy as np


def generate_scaled_e8_roots():
    roots = set()
    # Type 1
    for i in range(8):
        for j in range(i + 1, 8):
            for si in (-2, 2):
                for sj in (-2, 2):
                    v = [0] * 8
                    v[i] = si
                    v[j] = sj
                    roots.add(tuple(v))
    # Type 2
    from itertools import product

    for signs in product((-1, 1), repeat=8):
        if sum(1 for s in signs if s < 0) % 2 == 0:
            roots.add(tuple(int(s) for s in signs))
    roots_list = sorted(list(roots))
    assert len(roots_list) == 240, f"expected 240 roots, got {len(roots_list)}"
    return roots_list


def build_w33_graph():
    F = 3
    all_vectors = [
        (a, b, c, d)
        for a in range(F)
        for b in range(F)
        for c in range(F)
        for d in range(F)
        if (a, b, c, d) != (0, 0, 0, 0)
    ]

    def canonical_rep(v):
        for i in range(4):
            if v[i] % F != 0:
                a = v[i] % F
                inv = 1 if a == 1 else 2
                return tuple(((x * inv) % F) for x in v)
        return None

    reps = set(canonical_rep(v) for v in all_vectors if canonical_rep(v))
    vertices = sorted(list(reps))

    def symp(x, y):
        return (x[0] * y[1] - x[1] * y[0] + x[2] * y[3] - x[3] * y[2]) % F

    n = len(vertices)
    adj = [[] for _ in range(n)]
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if symp(vertices[i], vertices[j]) == 0:
                adj[i].append(j)
                adj[j].append(i)
                edges.append((i, j))
    return n, vertices, adj, edges


def compute_embedding_matrix():
    n, vertices, adj, edges = build_w33_graph()
    A = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in adj[i]:
            A[i, j] = 1.0
    vals, vecs = np.linalg.eigh(A)
    idx = np.argsort(vals)[::-1]
    vals = vals[idx]
    vecs = vecs[:, idx]
    # find eigenvalue-2 indices
    idxs_2 = [i for i, v in enumerate(vals) if abs(v - 2.0) < 1e-6]
    if len(idxs_2) >= 8:
        chosen = idxs_2[:8]
    else:
        chosen = list(range(1, 9))
    X = vecs[:, chosen]
    X = X - X.mean(axis=0)
    X = X / (X.std(axis=0) + 1e-12)
    return X, edges


def main():
    p = argparse.ArgumentParser()
    p.add_argument('seed_json')
    args = p.parse_args()

    seed_path = Path(args.seed_json)
    if not seed_path.exists():
        print('Seed file not found:', seed_path)
        sys.exit(2)

    seed = json.loads(open(seed_path, encoding='utf-8').read())
    seeded: Dict[int, int] = {int(s['edge_index']): int(s['root_index']) for s in seed.get('seed_edges', [])}

    # load roots and edges
    X, edges = compute_embedding_matrix()
    roots = generate_scaled_e8_roots()
    roots_map = {tuple(r): i for i, r in enumerate(roots)}

    # triangles
    n = max(max(a, b) for e in edges for (a, b) in [e]) + 1  # rough
    # build adjacency
    adj = [[] for _ in range(n)]
    for (i, j) in edges:
        adj[i].append(j)
        adj[j].append(i)

    triangles = []
    for a in range(n):
        for b in adj[a]:
            if b <= a:
                continue
            for c in adj[b]:
                if c <= b:
                    continue
                if a in adj[c]:
                    tri = tuple(sorted((a, b, c)))
                    if tri not in triangles:
                        triangles.append(tri)

    # map edge to index as in the solver
    edge_index = {edges[i]: i for i in range(len(edges))}

    contradictions = []
    missing_roots = []

    # 1) direct triangle checks where two seeded edges imply the third
    for (a, b, c) in triangles:
        # oriented edges e_ab, e_bc, e_ac as in solver
        e_ab = edge_index.get((a, b)) if (a, b) in edge_index else edge_index.get((b, a))
        e_bc = edge_index.get((b, c)) if (b, c) in edge_index else edge_index.get((c, b))
        e_ac = edge_index.get((a, c)) if (a, c) in edge_index else edge_index.get((c, a))
        if e_ab is None or e_bc is None or e_ac is None:
            continue
        # if e_ab and e_bc both seeded, we can compute implied r_ac
        if e_ab in seeded and e_bc in seeded:
            r_ab = roots[seeded[e_ab]]
            r_bc = roots[seeded[e_bc]]
            # implied r_ac = r_ab + r_bc coordinate-wise
            implied = tuple(int(x + y) for x, y in zip(r_ab, r_bc))
            if implied not in roots_map:
                missing_roots.append({'triangle': (a, b, c), 'implied': implied, 'e_ab': e_ab, 'e_bc': e_bc})
            else:
                implied_idx = roots_map[implied]
                # if e_ac seeded, check equality
                if e_ac in seeded:
                    if seeded[e_ac] != implied_idx:
                        contradictions.append({'triangle': (a, b, c), 'e_ab': e_ab, 'r_ab': seeded[e_ab], 'e_bc': e_bc, 'r_bc': seeded[e_bc], 'e_ac': e_ac, 'r_ac': seeded[e_ac], 'implied': implied_idx})

    # 2) iterative propagation: start with seeded assignments and deduce further edges
    propagated = dict(seeded)
    prop_contradictions = []
    prop_missing = []
    changed = True
    while changed:
        changed = False
        for (a, b, c) in triangles:
            e_ab = edge_index.get((a, b)) if (a, b) in edge_index else edge_index.get((b, a))
            e_bc = edge_index.get((b, c)) if (b, c) in edge_index else edge_index.get((c, b))
            e_ac = edge_index.get((a, c)) if (a, c) in edge_index else edge_index.get((c, a))
            if e_ab is None or e_bc is None or e_ac is None:
                continue
            # if two are known, deduce third
            # case: e_ab and e_bc known -> e_ac
            if e_ab in propagated and e_bc in propagated and e_ac not in propagated:
                r_ab = roots[propagated[e_ab]]
                r_bc = roots[propagated[e_bc]]
                implied = tuple(int(x + y) for x, y in zip(r_ab, r_bc))
                if implied not in roots_map:
                    prop_missing.append({'triangle': (a, b, c), 'implied': implied, 'e_ab': e_ab, 'e_bc': e_bc})
                    continue
                propagated[e_ac] = roots_map[implied]
                changed = True
            # other cases: e_ab and e_ac known -> e_bc (r_bc = r_ac - r_ab)
            if e_ab in propagated and e_ac in propagated and e_bc not in propagated:
                r_ab = roots[propagated[e_ab]]
                r_ac = roots[propagated[e_ac]]
                implied = tuple(int(c - a) for a, c in zip(r_ab, r_ac))
                if implied not in roots_map:
                    prop_missing.append({'triangle': (a, b, c), 'implied': implied, 'e_ab': e_ab, 'e_ac': e_ac})
                    continue
                propagated[e_bc] = roots_map[implied]
                changed = True
            # e_bc and e_ac known -> e_ab (r_ab = r_ac - r_bc)
            if e_bc in propagated and e_ac in propagated and e_ab not in propagated:
                r_bc = roots[propagated[e_bc]]
                r_ac = roots[propagated[e_ac]]
                implied = tuple(int(c - b) for b, c in zip(r_bc, r_ac))
                if implied not in roots_map:
                    prop_missing.append({'triangle': (a, b, c), 'implied': implied, 'e_bc': e_bc, 'e_ac': e_ac})
                    continue
                propagated[e_ab] = roots_map[implied]
                changed = True
        # check for contradictions with seeded values
        for ei, ridx in list(propagated.items()):
            if ei in seeded and seeded[ei] != ridx:
                prop_contradictions.append({'edge': ei, 'seeded': seeded[ei], 'propagated': ridx})
                # stop early
                changed = False
                break
    res = {
        'seed_file': str(seed_path),
        'num_seeded_edges': len(seeded),
        'triangles_checked': len(triangles),
        'contradictions': contradictions,
        'missing_roots': missing_roots,
        'propagated_count': len(propagated),
        'prop_contradictions': prop_contradictions,
        'prop_missing': prop_missing,
    }
    outp = Path('checks') / f"PART_CVII_z3_seed_consistency_{seed_path.stem}.json"
    outp.parent.mkdir(parents=True, exist_ok=True)
    with open(outp, 'w', encoding='utf-8') as f:
        json.dump(res, f, indent=2)
    print('Wrote', outp)

    if contradictions or missing_roots:
        sys.exit(1)


if __name__ == '__main__':
    main()
