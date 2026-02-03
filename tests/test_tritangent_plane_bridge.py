from __future__ import annotations

import importlib.util
import sys
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


def test_tritangent_plane_bridge_mixed_triples_equal_schlafli_triangles():
    repo_root = Path(__file__).resolve().parents[1]
    cds = _load_module(
        repo_root / "tools" / "compute_double_sixes.py", "compute_double_sixes"
    )

    roots = cds.construct_e8_roots()
    orbits = cds.compute_we6_orbits(roots)
    orbit_sizes = [len(o) for o in orbits]
    assert sorted(orbit_sizes) == [1, 1, 1, 1, 1, 1, 27, 27, 27, 27, 27, 27, 72]

    su3_alpha = np.array([1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    su3_beta = np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0])

    def su3_weight(r: np.ndarray) -> tuple[int, int]:
        return (
            int(round(float(np.dot(r, su3_alpha)))),
            int(round(float(np.dot(r, su3_beta)))),
        )

    def proj_to_su3(r: np.ndarray) -> np.ndarray:
        A = np.stack([su3_alpha, su3_beta], axis=1)
        G = A.T @ A
        coeffs = np.linalg.solve(G, A.T @ r)
        return A @ coeffs

    def e6_key(r: np.ndarray) -> tuple[int, ...]:
        re6 = r - proj_to_su3(r)
        return tuple(int(round(2 * float(x))) for x in re6.tolist())

    def k2(r: np.ndarray) -> tuple[int, ...]:
        return tuple(int(round(2 * float(x))) for x in r.tolist())

    # Index maps
    idx_orb: Dict[int, int] = {}
    for oi, orb in enumerate(orbits):
        for v in orb:
            idx_orb[v] = oi

    root_index = {k2(roots[i]): i for i in range(len(roots))}
    assert len(root_index) == len(roots)

    # Identify SU3 "3" orbits
    weights_3 = {(1, 0), (-1, 1), (0, -1)}
    mix_orbs = [oi for oi, sz in enumerate(orbit_sizes) if sz == 27]
    weights = {oi: su3_weight(roots[orbits[oi][0]]) for oi in mix_orbs}
    orbs_3 = sorted(
        [oi for oi in mix_orbs if weights[oi] in weights_3], key=lambda x: weights[x]
    )
    assert len(orbs_3) == 3

    # Mine 270 mixed triples (a,b,c) across orbs_3 with a+b+c=0
    oa, ob, oc = orbs_3
    triples: Set[tuple[int, int, int]] = set()
    for a in orbits[oa]:
        ka = k2(roots[a])
        for b in orbits[ob]:
            kb = k2(roots[b])
            need = tuple(-(ka[t] + kb[t]) for t in range(8))
            c = root_index.get(need)
            if c is None or idx_orb[c] != oc:
                continue
            triples.add((a, b, c))
    assert len(triples) == 270

    # Collapse to 27 E6-classes (each appears once per SU3 weight).
    e6_groups: Dict[tuple[int, ...], int] = {}
    root_to_e6id: Dict[int, int] = {}
    for oi in orbs_3:
        for r_idx in orbits[oi]:
            k = e6_key(roots[r_idx])
            if k not in e6_groups:
                e6_groups[k] = len(e6_groups)
            root_to_e6id[r_idx] = e6_groups[k]
    assert len(e6_groups) == 27

    # The 45 mixed-triple classes (each appears 6 times in the 270).
    class_triples: Set[tuple[int, int, int]] = set()
    multiplicities: Dict[tuple[int, int, int], int] = {}
    for a, b, c in triples:
        t = tuple(sorted((root_to_e6id[a], root_to_e6id[b], root_to_e6id[c])))
        class_triples.add(t)
        multiplicities[t] = multiplicities.get(t, 0) + 1
    assert len(class_triples) == 45
    assert set(multiplicities.values()) == {6}

    # Triangles in the complement of Schläfli (meeting graph) inside base orbit
    base_orb = orbs_3[0]
    base_vertices = orbits[base_orb]
    base_roots = roots[base_vertices]
    gram = np.rint(base_roots @ base_roots.T).astype(int)
    meet = gram == 0
    np.fill_diagonal(meet, False)

    triangles: Set[tuple[int, int, int]] = set()
    for i in range(27):
        for j in range(i + 1, 27):
            if not meet[i, j]:
                continue
            for k in range(j + 1, 27):
                if meet[i, k] and meet[j, k]:
                    triangles.add((i, j, k))
    assert len(triangles) == 45

    base_to_e6id = {i: root_to_e6id[base_vertices[i]] for i in range(27)}
    tri_class: Set[tuple[int, int, int]] = set()
    for i, j, k in triangles:
        tri_class.add(
            tuple(sorted((base_to_e6id[i], base_to_e6id[j], base_to_e6id[k])))
        )

    assert tri_class == class_triples
