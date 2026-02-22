#!/usr/bin/env python3
"""
Bridge: 45 S3-classes of mixed A2 triangles  <->  45 tritangent planes of a cubic surface.

Facts already established in this repo:
  - Each 27-orbit (of W(E6) acting on E8 roots) carries the Schläfli graph:
      edges = skew lines  ⇔  inner product = 1
    so the complement graph has:
      edges = meeting lines ⇔ inner product = 0
  - In the mixed roots, there are exactly 270 triples (a,b,c) across the 3 SU(3)-fundamental
    27-orbits with a+b+c=0, and W(A2)=S3 partitions them into 45 orbits of size 6.

What we do here:
  1) For the SU(3) "3" sector, take the three MIX27 orbits (9,3,4).
  2) Collapse SU(3) information by orthogonally projecting each mixed root r to its E6 part
     (since SU3 simples are orthogonal to the E6 subspace).
     Roots from different SU3 weights share the same E6 projection, giving 27 equivalence classes.
  3) Map each mixed triple (a,b,c) to an unordered triple of E6-classes; this yields 45 triples.
  4) Independently compute the 45 triangles in the complement of the Schläfli graph in one chosen
     27-orbit and map them to the same E6-class labels.
  5) Verify the two 45-sets coincide.

If this passes, we have a fully explicit combinatorial identification:
  mixed A2 triangles (E8 root-sum zero)  ==  tritangent-plane triples (3 meeting lines).
"""

from __future__ import annotations

import importlib.util
import json
from collections import Counter, defaultdict
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


SU3_ALPHA = np.array([1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
SU3_BETA = np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0])


def k2(r: np.ndarray) -> Tuple[int, ...]:
    return tuple(int(round(2 * float(x))) for x in r.tolist())


def su3_weight(r: np.ndarray) -> Tuple[int, int]:
    return (
        int(round(float(np.dot(r, SU3_ALPHA)))),
        int(round(float(np.dot(r, SU3_BETA)))),
    )


def proj_to_su3(r: np.ndarray) -> np.ndarray:
    """
    Orthogonal projection of r to span{alpha,beta} using Gram matrix.
    """
    A = np.stack([SU3_ALPHA, SU3_BETA], axis=1)  # 8x2
    G = A.T @ A  # 2x2
    coeffs = np.linalg.solve(G, A.T @ r)  # 2
    return A @ coeffs


def e6_key(r: np.ndarray) -> Tuple[int, ...]:
    """
    Key for E6-component of a mixed root: r_E6 = r - proj_SU3(r).
    We store 2*r_E6 rounded to int; should be integral in this embedding.
    """
    re6 = r - proj_to_su3(r)
    return tuple(int(round(2 * float(x))) for x in re6.tolist())


def build_root_indices(roots: np.ndarray) -> Dict[Tuple[int, ...], int]:
    keys = {k2(roots[i]): i for i in range(len(roots))}
    if len(keys) != len(roots):
        raise RuntimeError("Duplicate root keys")
    return keys


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


def find_triangles_in_complement(adj_meet: np.ndarray) -> Set[Tuple[int, int, int]]:
    """
    Find all triangles in an undirected graph given by boolean adjacency matrix.
    Returns triangles as sorted index triples (i<j<k).
    """
    n = adj_meet.shape[0]
    triangles: Set[Tuple[int, int, int]] = set()
    # O(n^3) is fine for n=27.
    for i in range(n):
        for j in range(i + 1, n):
            if not adj_meet[i, j]:
                continue
            for k in range(j + 1, n):
                if adj_meet[i, k] and adj_meet[j, k]:
                    triangles.add((i, j, k))
    return triangles


def main() -> None:
    roots = construct_e8_roots()
    orbits = compute_we6_orbits(roots)
    orbit_sizes = [len(o) for o in orbits]
    assert sorted(orbit_sizes) == [1, 1, 1, 1, 1, 1, 27, 27, 27, 27, 27, 27, 72]

    idx_orb: Dict[int, int] = {}
    for oi, orb in enumerate(orbits):
        for v in orb:
            idx_orb[v] = oi

    root_index = build_root_indices(roots)

    # Determine the three SU3 "3" orbits by their SU3 weights.
    mix_orbs = [oi for oi, sz in enumerate(orbit_sizes) if sz == 27]
    weights = {oi: su3_weight(roots[orbits[oi][0]]) for oi in mix_orbs}
    weights_3 = {(1, 0), (-1, 1), (0, -1)}
    orbs_3 = sorted(
        [oi for oi in mix_orbs if weights[oi] in weights_3], key=lambda x: weights[x]
    )
    assert len(orbs_3) == 3

    # Mine 270 mixed zero-sum triples across these three orbits.
    triples = mine_orbit_triple(roots, orbits, root_index, idx_orb, tuple(orbs_3))  # type: ignore[arg-type]
    assert len(triples) == 270

    # Collapse each root to an E6-class id (0..26) by grouping equal E6 projections.
    e6_groups: Dict[Tuple[int, ...], int] = {}
    root_to_e6id: Dict[int, int] = {}
    for oi in orbs_3:
        for r_idx in orbits[oi]:
            k = e6_key(roots[r_idx])
            if k not in e6_groups:
                e6_groups[k] = len(e6_groups)
            root_to_e6id[r_idx] = e6_groups[k]

    assert len(e6_groups) == 27
    counts_per_e6id = Counter(root_to_e6id.values())
    assert set(counts_per_e6id.values()) == {3}  # one per SU3 weight/orbit

    # Convert 270 mixed triples to unordered E6-id triples.
    tritangent_from_mixed: Set[Tuple[int, int, int]] = set()
    multiplicities = Counter()
    for a, b, c in triples:
        t = tuple(sorted((root_to_e6id[a], root_to_e6id[b], root_to_e6id[c])))
        tritangent_from_mixed.add(t)
        multiplicities[t] += 1

    assert len(tritangent_from_mixed) == 45
    # Each E6 triple appears 6 times (S3 permutations of SU3 indices).
    assert set(multiplicities.values()) == {6}

    # Now compute Schläfli complement triangles in one chosen orbit (pick first SU3-weight orbit as base).
    base_orb = orbs_3[0]
    base_vertices = orbits[base_orb]
    base_roots = roots[base_vertices]
    gram = np.rint(base_roots @ base_roots.T).astype(int)
    # In this repo convention for a 27-orbit:
    #   ip=1 -> skew (Schläfli edge)
    #   ip=0 -> meet (complement edge)
    meet = gram == 0
    np.fill_diagonal(meet, False)
    triangles = find_triangles_in_complement(meet)
    assert len(triangles) == 45

    # Map base orbit vertices to E6 ids and convert those triangles to E6-id triples.
    base_to_e6id = {i: root_to_e6id[base_vertices[i]] for i in range(27)}
    tritangent_from_schlafli: Set[Tuple[int, int, int]] = set()
    for i, j, k in triangles:
        tritangent_from_schlafli.add(
            tuple(sorted((base_to_e6id[i], base_to_e6id[j], base_to_e6id[k])))
        )

    assert tritangent_from_schlafli == tritangent_from_mixed

    out = {
        "su3_orbits_three": [
            {"orbit": oi, "su3_weight": list(weights[oi])} for oi in orbs_3
        ],
        "e6_class_count": 27,
        "mixed_triples_count": 270,
        "tritangent_planes_count": 45,
        "each_plane_multiplicity_in_mixed": 6,
        "verified_equal_sets": True,
        "tritangent_planes_e6ids": [list(t) for t in sorted(tritangent_from_mixed)],
    }

    out_path = ROOT / "artifacts" / "tritangent_plane_bridge.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"PASS: 45 mixed-triple classes == 45 Schläfli-complement triangles")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
