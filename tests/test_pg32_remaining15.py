from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_remaining15_is_pg32_in_k6_edge_model():
    repo_root = Path(__file__).resolve().parents[1]
    cds = _load_module(
        repo_root / "tools" / "compute_double_sixes.py", "compute_double_sixes"
    )

    roots = cds.construct_e8_roots()
    orbits = cds.compute_we6_orbits(roots)
    base = [o for o in orbits if len(o) == 27][0]
    base_roots = roots[base]
    gram = np.rint(base_roots @ base_roots.T).astype(int)
    adj = gram == 1
    np.fill_diagonal(adj, False)

    k6 = [tuple(sorted(clq)) for clq in cds.find_k_cliques(adj, 6)]
    ds = cds.find_double_sixes(adj, k6)
    assert len(ds) == 36
    A, B, match = ds[0]
    A_list = list(A)
    all_12 = set(A) | set(B)
    remaining = sorted(v for v in range(27) if v not in all_12)
    assert len(remaining) == 15

    duad_to_vertex = {}
    for v in remaining:
        meets = [i for i, a in enumerate(A_list) if not adj[v, a]]
        assert len(meets) == 2
        i, j = sorted(meets)
        duad_to_vertex[(i, j)] = v
    assert len(duad_to_vertex) == 15

    # PG(3,2) line model gives 35 lines of size 3.
    # Triangles: {ij,jk,ki} over 3-subsets of {0..5} = 20
    tri_lines = []
    for a in range(6):
        for b in range(a + 1, 6):
            for c in range(b + 1, 6):
                tri_lines.append([(a, b), (b, c), (a, c)])
    assert len(tri_lines) == 20

    # Matchings: 15 perfect matchings of K6.
    def matchings(verts):
        if not verts:
            return [[]]
        v0 = verts[0]
        out = []
        for i in range(1, len(verts)):
            v1 = verts[i]
            rest = verts[1:i] + verts[i + 1 :]
            for tail in matchings(rest):
                out.append([(v0, v1)] + tail)
        return out

    raw = matchings(list(range(6)))
    canon = set()
    for m in raw:
        canon.add(tuple(sorted(tuple(sorted(p)) for p in m)))
    assert len(canon) == 15

    lines = []
    for duads in tri_lines:
        pts = [duad_to_vertex[tuple(sorted(d))] for d in duads]
        lines.append(sorted(pts))
    for m in canon:
        pts = [duad_to_vertex[p] for p in m]
        lines.append(sorted(pts))
    assert len(lines) == 35

    # Each point is on 7 lines; total incidences 105.
    incidences = 0
    deg = {v: 0 for v in remaining}
    for ln in lines:
        assert len(ln) == 3
        incidences += 3
        for v in ln:
            deg[v] += 1
    assert incidences == 105
    assert set(deg.values()) == {7}
