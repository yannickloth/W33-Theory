#!/usr/bin/env python3
"""
Test whether the Coxeter c^5 (order-6) "phase" acts on the mixed cubic triples.

Empirical target (suggested by counts):
  - Each of the two cubic hypergraphs has 270 unique triples.
  - 270/6 = 45, matching the classical count of tritangent planes on a cubic surface.

Here we:
  1) Build the c^5 action as a permutation of the 240 E8 roots.
  2) Mine the two mixed triple sets (9,3,4) and (5,0,6).
  3) Compute orbit structure of triples under simultaneous c^5 action on all 3 roots.
"""

from __future__ import annotations

import importlib.util
from collections import Counter
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
construct_e8_roots = _cds.construct_e8_roots
compute_coxeter_matrix = _cds.compute_coxeter_matrix
compute_we6_orbits = _cds.compute_we6_orbits


def k2(r: np.ndarray) -> Tuple[int, ...]:
    return tuple(int(round(2 * float(x))) for x in r.tolist())


def build_c5_permutation(roots: np.ndarray) -> List[int]:
    c = compute_coxeter_matrix()
    c5 = np.linalg.matrix_power(c, 5)
    perm = [-1] * len(roots)
    for i in range(len(roots)):
        v = c5 @ roots[i]
        d = np.linalg.norm(roots - v, axis=1)
        j = int(np.argmin(d))
        if d[j] > 1e-6:
            raise RuntimeError("Failed to match c5 image to a root")
        perm[i] = j
    if sorted(perm) != list(range(len(roots))):
        raise RuntimeError("c5 mapping is not a permutation")
    return perm


def mine_orbit_triple(
    roots: np.ndarray,
    orbits: List[List[int]],
    root_index: Dict[Tuple[int, ...], int],
    idx_orb: Dict[int, int],
    orbit_triple: Tuple[int, int, int],
) -> Set[Tuple[int, int, int]]:
    oa, ob, oc = orbit_triple
    triples: Set[Tuple[int, int, int]] = set()
    for a in orbits[oa]:
        ka = k2(roots[a])
        for b in orbits[ob]:
            kb = k2(roots[b])
            need = tuple(-(ka[t] + kb[t]) for t in range(8))
            c = root_index.get(need)
            if c is None or idx_orb[c] != oc:
                continue
            triples.add((a, b, c))
    return triples


def triple_orbits_unordered(
    triples: Set[Tuple[int, int, int]], perm: List[int]
) -> Counter[int]:
    """
    Compute orbit-size distribution on unordered triples (as frozensets of 3 root indices).
    """
    triples_u: Set[frozenset[int]] = {frozenset(t) for t in triples}
    unseen = set(triples_u)
    sizes = Counter()
    while unseen:
        t = next(iter(unseen))
        cur = t
        orbit = []
        while True:
            if cur in unseen:
                unseen.remove(cur)
            orbit.append(cur)
            nxt = frozenset({perm[i] for i in cur})
            if nxt == t:
                break
            cur = nxt
        sizes[len(orbit)] += 1
    return sizes


def main() -> None:
    roots = construct_e8_roots()
    orbits = compute_we6_orbits(roots)
    orbit_sizes = [len(o) for o in orbits]
    idx_orb = {}
    for oi, orb in enumerate(orbits):
        for v in orb:
            idx_orb[v] = oi

    keys = np.array(
        [[int(round(2 * float(x))) for x in roots[i]] for i in range(len(roots))],
        dtype=int,
    )
    root_index = {tuple(keys[i].tolist()): i for i in range(len(roots))}

    perm = build_c5_permutation(roots)
    # quick sanity: order 6
    x = 0
    for _ in range(6):
        x = perm[x]
    assert x == 0

    # The two cubic orbit-triples discovered earlier
    assert sorted(orbit_sizes) == [1, 1, 1, 1, 1, 1, 27, 27, 27, 27, 27, 27, 72]
    triples_three = mine_orbit_triple(roots, orbits, root_index, idx_orb, (9, 3, 4))
    triples_threebar = mine_orbit_triple(roots, orbits, root_index, idx_orb, (5, 0, 6))
    assert len(triples_three) == 270 and len(triples_threebar) == 270

    sizes_three = triple_orbits_unordered(triples_three, perm)
    sizes_threebar = triple_orbits_unordered(triples_threebar, perm)
    sizes_all = triple_orbits_unordered(triples_three | triples_threebar, perm)

    print("c^5 orbit-size distribution on unordered triples:")
    print("  three:   ", dict(sizes_three))
    print("  threebar:", dict(sizes_threebar))
    print("  total:   ", dict(sizes_all))


if __name__ == "__main__":
    main()
