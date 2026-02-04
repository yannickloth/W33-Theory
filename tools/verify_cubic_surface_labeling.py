#!/usr/bin/env python3
"""
Recover the classical (a_i, b_i, c_ij) labeling of the 27 lines from a computed double-six.

We work inside one Schläfli 27-orbit:
  - skew adjacency: inner product = 1
  - meet adjacency: inner product = 0

Given a double-six (A,B,match) with |A|=|B|=6:
  - label A as a_0..a_5
  - label B as b_0..b_5 via the perfect matching (a_i -> b_i)
  - label remaining15 as c_ij for 0<=i<j<=5 by the duad {i,j} determined from
    which two a-lines it meets.

Then verify the standard incidence rules (e.g. as summarized in classic references):
  - a_i meets b_j  iff i != j
  - c_ij meets a_i, a_j, b_i, b_j
  - c_ij meets c_kl iff {i,j} and {k,l} are disjoint
  - a_i meets no a_j (i!=j); b_i meets no b_j (i!=j); a_i meets no b_i

Also verify the 45 tritangent planes split as:
  - 30 of type (a_i, b_j, c_ij) with i!=j
  - 15 of type (c_ij, c_kl, c_mn) for perfect matchings.
"""

from __future__ import annotations

import importlib.util
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load_compute_double_sixes():
    path = ROOT / "tools" / "compute_double_sixes.py"
    spec = importlib.util.spec_from_file_location("compute_double_sixes", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_cds = _load_compute_double_sixes()


def triangles_in_graph(adj: np.ndarray) -> Set[Tuple[int, int, int]]:
    n = adj.shape[0]
    out: Set[Tuple[int, int, int]] = set()
    for i in range(n):
        for j in range(i + 1, n):
            if not adj[i, j]:
                continue
            for k in range(j + 1, n):
                if adj[i, k] and adj[j, k]:
                    out.add((i, j, k))
    return out


def main() -> None:
    roots = _cds.construct_e8_roots()
    orbits = _cds.compute_we6_orbits(roots)
    orb27 = [o for o in orbits if len(o) == 27][0]
    r = roots[orb27]
    gram = np.rint(r @ r.T).astype(int)
    skew = gram == 1
    meet = gram == 0
    np.fill_diagonal(skew, False)
    np.fill_diagonal(meet, False)

    k6 = [tuple(sorted(clq)) for clq in _cds.find_k_cliques(skew, 6)]
    ds = _cds.find_double_sixes(skew, k6)
    assert len(ds) == 36
    A, B, match = ds[0]
    a = list(A)
    b = [match[x] for x in a]

    all_12 = set(A) | set(B)
    remaining = sorted(v for v in range(27) if v not in all_12)
    assert len(remaining) == 15

    # Map remaining vertex -> duad (i,j) from which a_i,a_j it meets.
    v_to_duad: Dict[int, Tuple[int, int]] = {}
    duad_to_v: Dict[Tuple[int, int], int] = {}
    for v in remaining:
        meets = [i for i in range(6) if meet[v, a[i]]]
        assert len(meets) == 2
        i, j = sorted(meets)
        v_to_duad[v] = (i, j)
        duad_to_v[(i, j)] = v
    assert len(duad_to_v) == 15

    # Basic incidence checks
    # a_i meets b_j iff i != j; in particular a_i does not meet b_i.
    for i in range(6):
        assert not meet[a[i], b[i]]
        for j in range(6):
            if i == j:
                continue
            assert meet[a[i], b[j]]

    # a_i does not meet a_j for i!=j; b_i does not meet b_j for i!=j
    for i in range(6):
        for j in range(i + 1, 6):
            assert not meet[a[i], a[j]]
            assert not meet[b[i], b[j]]

    # c_ij meets a_i,a_j,b_i,b_j and meets no other a_k/b_k
    for (i, j), v in duad_to_v.items():
        for k in range(6):
            if k in (i, j):
                assert meet[v, a[k]]
                assert meet[v, b[k]]
            else:
                assert not meet[v, a[k]]
                assert not meet[v, b[k]]

    # c_ij meets c_kl iff {i,j} and {k,l} are disjoint
    for (i, j), v in duad_to_v.items():
        for (k, l), w in duad_to_v.items():
            if (i, j) >= (k, l):
                continue
            disjoint = len({i, j} & {k, l}) == 0
            assert meet[v, w] == disjoint

    # Intersection degrees: each line meets exactly 10 others (in general position).
    degs = meet.sum(axis=1).tolist()
    assert set(degs) == {10}

    # Tritangent planes = triangles in meet graph, and split 30+15 in the standard way.
    tris = triangles_in_graph(meet)
    assert len(tris) == 45
    class_counts = Counter()
    for t in tris:
        aa = sum(1 for x in t if x in A)
        bb = sum(1 for x in t if x in B)
        cc = sum(1 for x in t if x in remaining)
        class_counts[(aa, bb, cc)] += 1
    assert class_counts == Counter({(1, 1, 1): 30, (0, 0, 3): 15})

    out = {
        "double_six": {"a": a, "b": b},
        "c_ij": [
            {"ij": [i, j], "vertex": int(v)} for (i, j), v in sorted(duad_to_v.items())
        ],
        "meet_degree_distribution": dict(Counter(degs)),
        "tritangent_plane_class_counts": {
            str(k): int(v) for k, v in class_counts.items()
        },
    }
    out_path = ROOT / "artifacts" / "cubic_surface_labeling_from_double_six.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(
        "PASS: recovered (a_i,b_i,c_ij) labeling and verified incidence + tritangent split."
    )
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
