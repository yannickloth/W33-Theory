#!/usr/bin/env python3
"""
Check that the A2 (=SU3) Weyl group S3 explains the 270 = 45*6 cubic triple count.

We have two 3-partite hypergraphs of 270 unique triples (a+b+c=0) among mixed roots:
  - (9,3,4) of SU3 rep-type 3⊗3⊗3
  - (5,0,6) of SU3 rep-type 3bar⊗3bar⊗3bar

Hypothesis:
  The A2 Weyl group W(A2) ≅ S3 (order 6), acting on E8 roots by reflections in the
  two SU(3) simple roots, partitions each 270-triple set into 45 orbits of size 6.
"""

from __future__ import annotations

import importlib.util
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

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
construct_e8_roots = _cds.construct_e8_roots
compute_we6_orbits = _cds.compute_we6_orbits
weyl_reflect = _cds.weyl_reflect


SU3_ALPHA = np.array([1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
SU3_BETA = np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0])


def k2(r: np.ndarray) -> Tuple[int, ...]:
    return tuple(int(round(2 * float(x))) for x in r.tolist())


def build_reflection_perm(roots: np.ndarray, alpha: np.ndarray) -> List[int]:
    perm = [-1] * len(roots)
    for i in range(len(roots)):
        v = weyl_reflect(roots[i], alpha)
        d = np.linalg.norm(roots - v, axis=1)
        j = int(np.argmin(d))
        if d[j] > 1e-6:
            raise RuntimeError("Failed to match reflection image to a root")
        perm[i] = j
    if sorted(perm) != list(range(len(roots))):
        raise RuntimeError("Reflection mapping is not a permutation")
    return perm


def generate_group(perms: List[List[int]]) -> List[List[int]]:
    """Generate subgroup of Sym(n) from generators (naive BFS)."""
    n = len(perms[0])
    idp = list(range(n))
    gens = perms[:]

    def compose(p: List[int], q: List[int]) -> List[int]:
        return [p[q[i]] for i in range(n)]

    seen = {tuple(idp)}
    queue = [idp]
    group = [idp]
    while queue:
        g = queue.pop()
        for h in gens:
            gh = compose(h, g)
            t = tuple(gh)
            if t not in seen:
                seen.add(t)
                queue.append(gh)
                group.append(gh)
    return group


def mine_orbit_triple(
    roots: np.ndarray,
    orbits: List[List[int]],
    root_index: Dict[Tuple[int, ...], int],
    idx_orb: Dict[int, int],
    orbit_triple: Tuple[int, int, int],
) -> Set[frozenset[int]]:
    oa, ob, oc = orbit_triple
    triples: Set[frozenset[int]] = set()
    for a in orbits[oa]:
        ka = k2(roots[a])
        for b in orbits[ob]:
            kb = k2(roots[b])
            need = tuple(-(ka[t] + kb[t]) for t in range(8))
            c = root_index.get(need)
            if c is None or idx_orb[c] != oc:
                continue
            triples.add(frozenset((a, b, c)))
    return triples


def orbit_sizes_under_group(
    triples: Set[frozenset[int]], group: List[List[int]]
) -> Counter[int]:
    unseen = set(triples)
    sizes = Counter()
    while unseen:
        t = next(iter(unseen))
        orb = set()
        for g in group:
            img = frozenset({g[i] for i in t})
            orb.add(img)
        for x in orb:
            unseen.discard(x)
        sizes[len(orb)] += 1
    return sizes


def main() -> None:
    roots = construct_e8_roots()
    orbits = compute_we6_orbits(roots)
    idx_orb = {}
    for oi, orb in enumerate(orbits):
        for v in orb:
            idx_orb[v] = oi

    keys = np.array(
        [[int(round(2 * float(x))) for x in roots[i]] for i in range(len(roots))],
        dtype=int,
    )
    root_index = {tuple(keys[i].tolist()): i for i in range(len(roots))}

    s_alpha = build_reflection_perm(roots, SU3_ALPHA)
    s_beta = build_reflection_perm(roots, SU3_BETA)
    group = generate_group([s_alpha, s_beta])
    print("Generated W(A2) size:", len(group))
    assert len(group) == 6

    triples_3 = mine_orbit_triple(roots, orbits, root_index, idx_orb, (9, 3, 4))
    triples_3bar = mine_orbit_triple(roots, orbits, root_index, idx_orb, (5, 0, 6))
    assert len(triples_3) == 270 and len(triples_3bar) == 270

    sizes_3 = orbit_sizes_under_group(triples_3, group)
    sizes_3bar = orbit_sizes_under_group(triples_3bar, group)
    print("Orbit-size distribution on 3-triples under W(A2):", dict(sizes_3))
    print("Orbit-size distribution on 3bar-triples under W(A2):", dict(sizes_3bar))


if __name__ == "__main__":
    main()
