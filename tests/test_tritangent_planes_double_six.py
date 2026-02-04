from __future__ import annotations

import importlib.util
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple

import numpy as np


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_tritangent_planes_split_30_plus_15_relative_to_double_six():
    repo_root = Path(__file__).resolve().parents[1]
    cds = _load_module(
        repo_root / "tools" / "compute_double_sixes.py", "compute_double_sixes"
    )

    roots = cds.construct_e8_roots()
    orbits = cds.compute_we6_orbits(roots)
    orb27 = [o for o in orbits if len(o) == 27][0]
    r = roots[orb27]
    gram = np.rint(r @ r.T).astype(int)
    skew = gram == 1
    meet = gram == 0
    np.fill_diagonal(skew, False)
    np.fill_diagonal(meet, False)

    def triangles(adj: np.ndarray) -> Set[Tuple[int, int, int]]:
        out = set()
        for i in range(27):
            for j in range(i + 1, 27):
                if not adj[i, j]:
                    continue
                for k in range(j + 1, 27):
                    if adj[i, k] and adj[j, k]:
                        out.add((i, j, k))
        return out

    tri = triangles(meet)
    assert len(tri) == 45

    k6 = [tuple(sorted(clq)) for clq in cds.find_k_cliques(skew, 6)]
    ds = cds.find_double_sixes(skew, k6)
    assert len(ds) == 36
    A, B, match = ds[0]
    all_12 = set(A) | set(B)
    remaining = set(i for i in range(27) if i not in all_12)
    assert len(remaining) == 15

    counts = Counter()
    for t in tri:
        a = sum(1 for x in t if x in A)
        b = sum(1 for x in t if x in B)
        c = sum(1 for x in t if x in remaining)
        counts[(a, b, c)] += 1

    assert counts == Counter({(1, 1, 1): 30, (0, 0, 3): 15})
