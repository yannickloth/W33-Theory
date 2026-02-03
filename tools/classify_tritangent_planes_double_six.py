#!/usr/bin/env python3
"""
Classify the 45 tritangent planes (triangles in the meet graph) relative to a reference double-six.

Classical cubic-surface labeling with a chosen double-six:
  - 6 skew lines:      a1..a6
  - 6 skew lines:      b1..b6
  - 15 remaining:      c_ij, 1<=i<j<=6

Known decomposition of the 45 tritangent planes:
  - 30 planes of type: a_i, b_j, c_ij  with i != j
  - 15 planes of type: c_ij, c_kl, c_mn  for a perfect matching (ij)(kl)(mn) of {1..6}

In our computational model inside a Schläfli 27-orbit:
  - Schläfli adjacency (skew) is ip=1
  - "meet" edges are ip=0 (complement graph)
  - tritangent planes correspond to triangles in the meet graph

This script:
  1) picks a reference double-six (first) in a 27-orbit,
  2) computes all meet-graph triangles (should be 45),
  3) labels the 15 remaining vertices by duads {i,j} via which two a-lines they meet,
  4) checks the 45 split as 30 (a,b,c_ij) + 15 (perfect matchings on c_ij),
  5) writes artifacts with the explicit triangle lists and labels.
"""

from __future__ import annotations

import importlib.util
import itertools
import json
from collections import Counter, defaultdict
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


def perfect_matchings_on_6() -> (
    Set[Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]]
):
    """
    Canonical perfect matchings of K6 on {0..5} as sorted tuple of 3 sorted pairs.
    """

    def rec(verts: Tuple[int, ...]) -> List[List[Tuple[int, int]]]:
        if not verts:
            return [[]]
        v0 = verts[0]
        out = []
        for i in range(1, len(verts)):
            v1 = verts[i]
            rest = verts[1:i] + verts[i + 1 :]
            for tail in rec(rest):
                out.append([(v0, v1)] + tail)
        return out

    seen = set()
    for m in rec(tuple(range(6))):
        pairs = tuple(sorted(tuple(sorted(p)) for p in m))
        seen.add(pairs)
    assert len(seen) == 15
    return seen


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
    A_list = list(A)
    B_list = [match[a] for a in A_list]

    all_12 = set(A) | set(B)
    remaining = sorted(v for v in range(27) if v not in all_12)
    assert len(remaining) == 15

    # duad label for each remaining vertex based on which two A lines it MEETS (not skew-adjacent).
    v_to_duad: Dict[int, Tuple[int, int]] = {}
    duad_to_v: Dict[Tuple[int, int], int] = {}
    for v in remaining:
        meets = [i for i, a in enumerate(A_list) if not skew[v, a]]
        assert len(meets) == 2
        i, j = sorted(meets)
        v_to_duad[v] = (i, j)
        duad_to_v[(i, j)] = v
    assert len(duad_to_v) == 15

    # 45 tritangent planes = triangles in meet graph.
    triangles = triangles_in_graph(meet)
    assert len(triangles) == 45

    # Classify by how many vertices lie in A, B, remaining.
    class_counts = Counter()
    classes: Dict[str, List[List[int]]] = defaultdict(list)
    for t in triangles:
        a = sum(1 for x in t if x in A)
        b = sum(1 for x in t if x in B)
        c = sum(1 for x in t if x in remaining)
        class_counts[(a, b, c)] += 1
        classes[f"{a}{b}{c}"].append(list(t))

    # Expect exactly (1,1,1)=30 and (0,0,3)=15
    assert class_counts[(1, 1, 1)] == 30
    assert class_counts[(0, 0, 3)] == 15
    assert sum(class_counts.values()) == 45

    # Check the 15 all-remaining triangles correspond exactly to perfect matchings.
    matchings = perfect_matchings_on_6()
    remaining_triangles_duads = set()
    for x, y, z in triangles:
        if x in remaining and y in remaining and z in remaining:
            duads = tuple(sorted((v_to_duad[x], v_to_duad[y], v_to_duad[z])))
            remaining_triangles_duads.add(duads)
    assert len(remaining_triangles_duads) == 15
    assert remaining_triangles_duads == matchings

    # Check the 30 mixed triangles are exactly a_i b_j c_ij with i != j.
    # Translate A index i and B index j back to their A positions.
    v_to_ai = {A_list[i]: i for i in range(6)}
    v_to_bj = {B_list[i]: i for i in range(6)}

    observed_pairs = set()
    for x, y, z in triangles:
        if sum(1 for u in (x, y, z) if u in remaining) != 1:
            continue
        a_v = next(u for u in (x, y, z) if u in A)
        b_v = next(u for u in (x, y, z) if u in B)
        c_v = next(u for u in (x, y, z) if u in remaining)
        i = v_to_ai[a_v]
        j = v_to_bj[b_v]
        ij = tuple(sorted((i, j)))
        assert i != j
        assert v_to_duad[c_v] == ij
        observed_pairs.add((i, j))
    assert len(observed_pairs) == 30
    assert observed_pairs == {(i, j) for i in range(6) for j in range(6) if i != j}

    out = {
        "reference_double_six": {
            "A": A_list,
            "B": B_list,
            "remaining15": remaining,
            "matching_A_to_B": {int(k): int(v) for k, v in match.items()},
        },
        "counts": {
            "tritangent_planes": 45,
            "class_distribution": {str(k): int(v) for k, v in class_counts.items()},
            "abc_111": 30,
            "abc_003": 15,
        },
        "remaining15_duads": [
            {"vertex": int(v), "duad": list(v_to_duad[v])} for v in remaining
        ],
        "remaining15_tritangent_planes_duads": [
            list(map(list, t)) for t in sorted(remaining_triangles_duads)
        ],
        "mixed_tritangent_planes_pairs": sorted([list(x) for x in observed_pairs]),
        "notes": {
            "abc_111": "Triangles with one vertex in A, one in B, one in remaining15: a_i b_j c_ij with i!=j (count 30).",
            "abc_003": "Triangles entirely in remaining15 correspond to perfect matchings of K6: c_ij c_kl c_mn (count 15).",
        },
    }

    out_path = ROOT / "artifacts" / "tritangent_planes_double_six_classification.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(
        "PASS: tritangent planes split as 30 (a_i b_j c_ij, i!=j) + 15 (perfect matchings)."
    )
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
