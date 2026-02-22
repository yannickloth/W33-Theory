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


def test_a2_weyl_group_partitions_cubic_triples_into_45_orbits():
    repo_root = Path(__file__).resolve().parents[1]
    cds = _load_module(
        repo_root / "tools" / "compute_double_sixes.py", "compute_double_sixes"
    )

    roots = cds.construct_e8_roots()
    orbits = cds.compute_we6_orbits(roots)

    idx_orb: Dict[int, int] = {}
    for oi, orb in enumerate(orbits):
        for v in orb:
            idx_orb[v] = oi

    keys = np.array(
        [[int(round(2 * float(x))) for x in roots[i]] for i in range(len(roots))],
        dtype=int,
    )
    root_index = {tuple(keys[i].tolist()): i for i in range(len(roots))}

    su3_alpha = np.array([1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    su3_beta = np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0])

    def build_reflection_perm(alpha: np.ndarray) -> List[int]:
        perm = [-1] * len(roots)
        for i in range(len(roots)):
            v = cds.weyl_reflect(roots[i], alpha)
            d = np.linalg.norm(roots - v, axis=1)
            j = int(np.argmin(d))
            assert d[j] <= 1e-6
            perm[i] = j
        assert sorted(perm) == list(range(len(roots)))
        return perm

    def compose(p: List[int], q: List[int]) -> List[int]:
        return [p[q[i]] for i in range(len(p))]

    s_alpha = build_reflection_perm(su3_alpha)
    s_beta = build_reflection_perm(su3_beta)

    # Generate W(A2) = <s_alpha, s_beta> (should be size 6).
    idp = list(range(len(roots)))
    seen = {tuple(idp)}
    queue = [idp]
    group = [idp]
    while queue:
        g = queue.pop()
        for h in (s_alpha, s_beta):
            gh = compose(h, g)
            t = tuple(gh)
            if t not in seen:
                seen.add(t)
                queue.append(gh)
                group.append(gh)
    assert len(group) == 6

    def mine_orbit_triple(oa: int, ob: int, oc: int) -> Set[frozenset[int]]:
        triples: Set[frozenset[int]] = set()
        for a in orbits[oa]:
            ka = tuple(keys[a].tolist())
            for b in orbits[ob]:
                kb = tuple(keys[b].tolist())
                need = tuple(-(ka[t] + kb[t]) for t in range(8))
                c = root_index.get(need)
                if c is None or idx_orb[c] != oc:
                    continue
                triples.add(frozenset((a, b, c)))
        return triples

    triples_3 = mine_orbit_triple(9, 3, 4)
    triples_3bar = mine_orbit_triple(5, 0, 6)
    assert len(triples_3) == 270 and len(triples_3bar) == 270

    def orbit_sizes(triples: Set[frozenset[int]]) -> Counter[int]:
        unseen = set(triples)
        sizes = Counter()
        while unseen:
            t = next(iter(unseen))
            orb = set()
            for g in group:
                orb.add(frozenset({g[i] for i in t}))
            for x in orb:
                unseen.discard(x)
            sizes[len(orb)] += 1
        return sizes

    assert orbit_sizes(triples_3) == Counter({6: 45})
    assert orbit_sizes(triples_3bar) == Counter({6: 45})
