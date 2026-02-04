from __future__ import annotations

import importlib.util
import sys
from collections import deque
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


def test_we6_simple_reflections_generate_51840_and_preserve_tritangents():
    repo_root = Path(__file__).resolve().parents[1]
    cds = _load_module(
        repo_root / "tools" / "compute_double_sixes.py", "compute_double_sixes"
    )

    roots = cds.construct_e8_roots()
    we6_orbits = cds.compute_we6_orbits(roots)
    orbit27 = [o for o in we6_orbits if len(o) == 27][0]

    local_roots = roots[orbit27]
    key_to_local: Dict[Tuple[float, ...], int] = {}
    for i in range(27):
        key_to_local[cds.snap_to_lattice(local_roots[i])] = i

    gram = np.rint(local_roots @ local_roots.T).astype(int)
    meet = gram == 0
    np.fill_diagonal(meet, False)

    # 45 tritangent planes = triangles in meet graph
    tris: Set[Tuple[int, int, int]] = set()
    for i in range(27):
        for j in range(i + 1, 27):
            if not meet[i, j]:
                continue
            for k in range(j + 1, 27):
                if meet[i, k] and meet[j, k]:
                    tris.add((i, j, k))
    assert len(tris) == 45

    gens: List[Tuple[int, ...]] = []
    for alpha in cds.E6_SIMPLE_ROOTS:
        perm = []
        for i in range(27):
            v = cds.weyl_reflect(local_roots[i], alpha)
            k = cds.snap_to_lattice(v)
            j = key_to_local.get(k)
            assert j is not None
            perm.append(j)
        p = tuple(perm)
        assert sorted(p) == list(range(27))
        gens.append(p)

    def compose(p: Tuple[int, ...], q: Tuple[int, ...]) -> Tuple[int, ...]:
        return tuple(p[i] for i in q)

    # group closure
    idp = tuple(range(27))
    seen = {idp}
    q = deque([idp])
    while q:
        g = q.popleft()
        for h in gens:
            gh = compose(h, g)
            if gh not in seen:
                seen.add(gh)
                q.append(gh)
    assert len(seen) == 51840

    # generator-level preservation of tritangent triangles
    for p in gens:
        for i, j, k in tris:
            img = tuple(sorted((p[i], p[j], p[k])))
            assert img in tris
