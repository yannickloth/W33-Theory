from __future__ import annotations

import importlib.util
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, Set, Tuple

import numpy as np


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_double_six_induces_standard_27_line_incidence_rules():
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

    k6 = [tuple(sorted(clq)) for clq in cds.find_k_cliques(skew, 6)]
    ds = cds.find_double_sixes(skew, k6)
    assert len(ds) == 36
    A, B, match = ds[0]
    a = list(A)
    b = [match[x] for x in a]

    remaining = [v for v in range(27) if v not in (set(A) | set(B))]
    assert len(remaining) == 15

    duad_to_v: Dict[Tuple[int, int], int] = {}
    for v in remaining:
        meets = [i for i in range(6) if meet[v, a[i]]]
        assert len(meets) == 2
        i, j = sorted(meets)
        duad_to_v[(i, j)] = v
    assert len(duad_to_v) == 15

    # a_i meets b_j iff i != j
    for i in range(6):
        assert not meet[a[i], b[i]]
        for j in range(6):
            if i != j:
                assert meet[a[i], b[j]]

    # c_ij meets exactly a_i,a_j,b_i,b_j
    for (i, j), v in duad_to_v.items():
        for k in range(6):
            if k in (i, j):
                assert meet[v, a[k]] and meet[v, b[k]]
            else:
                assert (not meet[v, a[k]]) and (not meet[v, b[k]])

    # c_ij meets c_kl iff disjoint
    for (i, j), v in duad_to_v.items():
        for (k, l), w in duad_to_v.items():
            if (i, j) >= (k, l):
                continue
            disjoint = len({i, j} & {k, l}) == 0
            assert meet[v, w] == disjoint

    # Every line meets 10 others
    degs = meet.sum(axis=1).tolist()
    assert dict(Counter(degs)) == {10: 27}
