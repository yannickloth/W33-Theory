#!/usr/bin/env python3
"""
Verify: the 'remaining15' vertices outside a double-six form PG(3,2) in the K6-edge model.

From the Schläfli / 27-line model:
  - Pick a reference double-six: A (6 skew lines), B (6 skew lines) with perfect matching.
  - The 15 remaining vertices each meets exactly 2 lines in A and 2 lines in B.
  - Using A as the reference, each remaining vertex gets a label {i,j} (a duad) from which
    two A-lines it meets. This gives a bijection:
        remaining15  <->  C(6,2)  (edges of K6 on letters 0..5)

Classical finite-geometry fact:
  PG(3,2) has 15 points and 35 lines (each line has 3 points, each point on 7 lines).
  One convenient model uses the K6 edges as points and splits lines into:
    - 20 triangle-lines: {ij, jk, ki} for each 3-subset {i,j,k}
    - 15 matching-lines: {ab, cd, ef} for each perfect matching of K6

This script reproduces that structure purely from the computed double-six inside a 27-orbit.
Outputs:
  - artifacts/pg32_points_from_remaining15.json
  - artifacts/pg32_lines_from_remaining15.json
"""

from __future__ import annotations

import importlib.util
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

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


def perfect_matchings_on_6() -> List[List[Tuple[int, int]]]:
    """
    Return the 15 perfect matchings of K6 on vertices 0..5.
    Each matching is a list of 3 disjoint pairs.
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

    matchings = rec(tuple(range(6)))
    # canonicalize each matching by sorting pairs and sorting the list
    canon = []
    seen = set()
    for m in matchings:
        pairs = tuple(sorted(tuple(sorted(p)) for p in m))
        if pairs in seen:
            continue
        seen.add(pairs)
        canon.append([tuple(p) for p in pairs])
    assert len(canon) == 15
    return canon


def build_pg32_lines_duads() -> List[Dict]:
    """
    Build the 35 PG(3,2) lines as sets of 3 duads on {0..5}.
    """
    lines = []
    # 20 triangle lines from 3-subsets
    for a, b, c in itertools.combinations(range(6), 3):
        duads = sorted([sorted([a, b]), sorted([b, c]), sorted([a, c])])
        lines.append({"type": "triangle", "letters": [a, b, c], "duads": duads})
    # 15 matching lines from perfect matchings
    for pairs in perfect_matchings_on_6():
        duads = sorted([sorted([i, j]) for (i, j) in pairs])
        lines.append(
            {"type": "matching", "pairs": [list(p) for p in pairs], "duads": duads}
        )
    assert len(lines) == 35
    return lines


def main() -> None:
    roots = _cds.construct_e8_roots()
    orbits = _cds.compute_we6_orbits(roots)

    # take first 27-orbit (same convention as compute_double_sixes)
    orbits_27 = [o for o in orbits if len(o) == 27]
    base = orbits_27[0]
    base_roots = roots[base]
    gram = np.rint(base_roots @ base_roots.T).astype(int)
    # Schläfli adjacency = ip=1 (skew), meet = ip=0
    adj = gram == 1
    np.fill_diagonal(adj, False)

    k6_raw = _cds.find_k_cliques(adj, 6)
    k6 = [tuple(int(x) for x in sorted(list(clq))) for clq in k6_raw]
    ds = _cds.find_double_sixes(adj, k6)
    assert len(ds) == 36
    A, B, match = ds[0]
    A_list = list(A)
    B_list = [match[a] for a in A_list]
    all_12 = set(A) | set(B)
    remaining = sorted(v for v in range(27) if v not in all_12)
    assert len(remaining) == 15

    # Label each remaining vertex by the pair of A-lines it MEETS (i.e., not adjacent in skew graph).
    vertex_to_duad: Dict[int, List[int]] = {}
    duad_to_vertex: Dict[Tuple[int, int], int] = {}
    for v in remaining:
        meets = [i for i, a in enumerate(A_list) if not adj[v, a]]
        assert len(meets) == 2
        i, j = sorted(meets)
        vertex_to_duad[v] = [i, j]
        duad_to_vertex[(i, j)] = v

    assert len(duad_to_vertex) == 15

    # Build PG(3,2) lines (in duad language) and translate to vertex IDs.
    lines = []
    for line in build_pg32_lines_duads():
        pts = []
        for x, y in (tuple(d) for d in line["duads"]):
            pts.append(duad_to_vertex[(x, y)])
        lines.append({**line, "points": pts})

    # Incidence checks
    point_to_lines = defaultdict(list)
    for li, line in enumerate(lines):
        for p in line["points"]:
            point_to_lines[p].append(li)

    n_points = 15
    n_lines = len(lines)
    incidences = sum(len(line["points"]) for line in lines)

    assert n_lines == 35
    assert incidences == 105
    assert all(len(line["points"]) == 3 for line in lines)
    assert set(len(point_to_lines[p]) for p in remaining) == {7}

    # Pair multiplicities: each unordered pair of points should be in exactly 1 line or 0 lines.
    pair_mult = Counter()
    for line in lines:
        pts = sorted(line["points"])
        for a, b in itertools.combinations(pts, 2):
            pair_mult[(a, b)] += 1
    assert set(pair_mult.values()).issubset({1})

    points_out = {
        "summary": {
            "reference_double_six": {
                "L": A_list,
                "M": B_list,
                "remaining15": remaining,
                "matching_L_to_M": {int(k): int(v) for k, v in match.items()},
            },
            "n_points": n_points,
        },
        "points": [{"vertex": v, "duad": vertex_to_duad[v]} for v in remaining],
    }

    lines_out = {
        "summary": {
            "n_lines": n_lines,
            "line_size": 3,
            "incidences": incidences,
            "each_point_on_7_lines": True,
        },
        "lines": lines,
    }

    (ROOT / "artifacts").mkdir(parents=True, exist_ok=True)
    (ROOT / "artifacts" / "pg32_points_from_remaining15.json").write_text(
        json.dumps(points_out, indent=2), encoding="utf-8"
    )
    (ROOT / "artifacts" / "pg32_lines_from_remaining15.json").write_text(
        json.dumps(lines_out, indent=2), encoding="utf-8"
    )

    print("PASS: remaining15 forms PG(3,2) with 15 points and 35 lines.")


if __name__ == "__main__":
    main()
