#!/usr/bin/env python3
"""
Extract the 45 S3-orbits of mixed A2 triangles (α+β+γ=0) inside one (27,3) sector.

We proved computationally:
  - There are 270 unique mixed triples in the 3⊗3⊗3 sector (orbit triple 9,3,4).
  - The A2 Weyl group W(A2) ≅ S3 (order 6) partitions these 270 triples into 45 orbits of size 6.

These 45 orbit-classes are strong candidates for the "45 tritangent planes" object on the
E6 / cubic-surface side (the count matches exactly).

This tool writes a JSON artifact with 45 orbit representatives and basic invariants.
"""

from __future__ import annotations

import importlib.util
import json
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


def compose(p: List[int], q: List[int]) -> List[int]:
    return [p[q[i]] for i in range(len(p))]


def generate_group(gens: List[List[int]]) -> List[List[int]]:
    n = len(gens[0])
    idp = list(range(n))
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


def partition_into_orbits(
    triples: Set[frozenset[int]], group: List[List[int]]
) -> List[Set[frozenset[int]]]:
    unseen = set(triples)
    orbs = []
    while unseen:
        t = next(iter(unseen))
        orb = set()
        for g in group:
            orb.add(frozenset({g[i] for i in t}))
        for x in orb:
            unseen.discard(x)
        orbs.append(orb)
    return orbs


def main() -> None:
    roots = construct_e8_roots()
    orbits = compute_we6_orbits(roots)
    idx_orb: Dict[int, int] = {}
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
    assert len(group) == 6

    triples_3 = mine_orbit_triple(roots, orbits, root_index, idx_orb, (9, 3, 4))
    triples_3bar = mine_orbit_triple(roots, orbits, root_index, idx_orb, (5, 0, 6))
    assert len(triples_3) == 270 and len(triples_3bar) == 270

    orbs_3 = partition_into_orbits(triples_3, group)
    orbs_3bar = partition_into_orbits(triples_3bar, group)
    assert len(orbs_3) == 45 and all(len(o) == 6 for o in orbs_3)
    assert len(orbs_3bar) == 45 and all(len(o) == 6 for o in orbs_3bar)

    def rep(triple_set: Set[frozenset[int]]) -> List[int]:
        # canonical representative: lexicographically smallest sorted triple
        best = None
        for t in triple_set:
            s = sorted(t)
            if best is None or tuple(s) < tuple(best):
                best = s
        assert best is not None
        return best

    def invariant(t: List[int]) -> Dict[str, object]:
        ra, rb, rc = (roots[t[0]], roots[t[1]], roots[t[2]])
        ips = [
            float(np.dot(ra, rb)),
            float(np.dot(ra, rc)),
            float(np.dot(rb, rc)),
        ]
        return {
            "root_indices": t,
            "we6_orbits": [idx_orb[x] for x in t],
            "pairwise_inner_products": ips,
        }

    out = {
        "wa2_group_size": 6,
        "three": {
            "orbit_triple_seed": [9, 3, 4],
            "n_triples": 270,
            "n_orbits": 45,
            "orbit_size": 6,
            "orbit_representatives": [
                invariant(rep(o)) for o in sorted(orbs_3, key=lambda s: tuple(rep(s)))
            ],
        },
        "threebar": {
            "orbit_triple_seed": [5, 0, 6],
            "n_triples": 270,
            "n_orbits": 45,
            "orbit_size": 6,
            "orbit_representatives": [
                invariant(rep(o))
                for o in sorted(orbs_3bar, key=lambda s: tuple(rep(s)))
            ],
        },
        "notes": {
            "interpretation": "Each 6-element orbit is an S3-class of A2 triangles among mixed roots; 45 matches classical tritangent-plane count.",
        },
    }

    out_path = ROOT / "artifacts" / "tritangent_like_orbits.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
