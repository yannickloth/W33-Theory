from __future__ import annotations

import importlib.util
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, Tuple

import numpy as np


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_mixed_270_triples_collapse_to_45_tritangent_planes_with_mult_6():
    repo_root = Path(__file__).resolve().parents[1]
    cds = _load_module(
        repo_root / "tools" / "compute_double_sixes.py", "compute_double_sixes"
    )

    su3_alpha = np.array([1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    su3_beta = np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0])

    roots = cds.construct_e8_roots()
    orbits = cds.compute_we6_orbits(roots)
    orbit_sizes = [len(o) for o in orbits]
    assert sorted(orbit_sizes) == [1, 1, 1, 1, 1, 1, 27, 27, 27, 27, 27, 27, 72]

    idx_orb: Dict[int, int] = {}
    for oi, orb in enumerate(orbits):
        for v in orb:
            idx_orb[v] = oi

    def su3_weight(r) -> Tuple[int, int]:
        return (
            int(round(float(np.dot(r, su3_alpha)))),
            int(round(float(np.dot(r, su3_beta)))),
        )

    def proj_to_su3(r):
        A = np.stack([su3_alpha, su3_beta], axis=1)
        G = A.T @ A
        coeffs = np.linalg.solve(G, A.T @ r)
        return A @ coeffs

    def e6_key(r):
        re6 = r - proj_to_su3(r)
        return tuple(int(round(2 * float(x))) for x in re6.tolist())

    def k2(r):
        return tuple(int(round(2 * float(x))) for x in r.tolist())

    root_index = {k2(roots[i]): i for i in range(len(roots))}

    mix_orbs = [oi for oi, sz in enumerate(orbit_sizes) if sz == 27]
    weights = {oi: su3_weight(roots[orbits[oi][0]]) for oi in mix_orbs}
    weights_3 = {(1, 0), (-1, 1), (0, -1)}
    orbs_3 = sorted(
        [oi for oi in mix_orbs if weights[oi] in weights_3], key=lambda x: weights[x]
    )
    assert len(orbs_3) == 3
    oa, ob, oc = orbs_3

    triples = []
    for a in orbits[oa]:
        ka = k2(roots[a])
        for b in orbits[ob]:
            kb = k2(roots[b])
            need = tuple(-(ka[t] + kb[t]) for t in range(8))
            c = root_index.get(need)
            if c is None or idx_orb[c] != oc:
                continue
            triples.append((a, b, c))
    assert len(triples) == 270

    # Build 27 E6-classes across the three 27-orbits.
    e6_groups = {}
    root_to_e6id = {}
    for oi in orbs_3:
        for r_idx in orbits[oi]:
            k = e6_key(roots[r_idx])
            if k not in e6_groups:
                e6_groups[k] = len(e6_groups)
            root_to_e6id[r_idx] = e6_groups[k]
    assert len(e6_groups) == 27

    mult = Counter()
    e6_triples = set()
    for a, b, c in triples:
        t = tuple(sorted((root_to_e6id[a], root_to_e6id[b], root_to_e6id[c])))
        e6_triples.add(t)
        mult[t] += 1

    assert len(e6_triples) == 45
    assert dict(Counter(mult.values())) == {6: 45}
