#!/usr/bin/env python3
"""
Verify the E6 cubic invariant tensor d_{ijk} from E8 mixed-root triples.

Representation-theory expectation for the maximal subalgebra E8 ⊃ E6 × SU(3):
  248 = (78,1) ⊕ (1,8) ⊕ (27,3) ⊕ (27̄,3̄)

Let ψ_i^a be fields in (27,3). An SU(3)-invariant cubic coupling must contract
the SU(3) indices with ε_{abc}, leaving an E6-invariant symmetric tensor d_{ijk}:

    ε_{abc} d_{ijk} ψ_i^a ψ_j^b ψ_k^c

In this repo we can see this directly on the E8 root system:
  - There are exactly 270 mixed root triples (α,β,γ) with α+β+γ=0 in the 3-sector,
    and they form 45 S3-orbits of size 6 (W(A2) action).
  - Collapsing SU(3) information yields exactly 45 unordered E6 triples (i,j,k).

This script constructs d_{ijk} as the 45 tritangent-plane triples of the 27-line configuration,
and verifies the multiplicity-6 lift back to the 270 mixed triples.

Outputs:
  artifacts/e6_cubic_tensor_from_e8.json
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
    A = np.stack([SU3_ALPHA, SU3_BETA], axis=1)  # 8x2
    G = A.T @ A  # 2x2
    coeffs = np.linalg.solve(G, A.T @ r)
    return A @ coeffs


def e6_key(r: np.ndarray) -> Tuple[int, ...]:
    re6 = r - proj_to_su3(r)
    return tuple(int(round(2 * float(x))) for x in re6.tolist())


def mine_mixed_triples_across_three_orbits(
    roots: np.ndarray,
    orbits: List[List[int]],
    root_index: Dict[Tuple[int, ...], int],
    idx_orb: Dict[int, int],
    orbit_triple: Tuple[int, int, int],
) -> List[Tuple[int, int, int]]:
    oa, ob, oc = orbit_triple
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
    return triples


def build_double_six_labeling(gram: np.ndarray) -> Dict[int, str]:
    """
    Use the first double-six in this 27-orbit to label vertices by a_i, b_i, c_ij.
    """
    skew = gram == 1
    meet = gram == 0
    np.fill_diagonal(skew, False)
    np.fill_diagonal(meet, False)
    k6 = [tuple(sorted(clq)) for clq in _cds.find_k_cliques(skew, 6)]
    ds = _cds.find_double_sixes(skew, k6)
    assert len(ds) == 36
    A, B, match = ds[0]
    a = list(A)
    b = [match[x] for x in a]

    remaining = [v for v in range(27) if v not in (set(A) | set(B))]
    assert len(remaining) == 15

    labels: Dict[int, str] = {}
    for i in range(6):
        labels[a[i]] = f"a{i}"
        labels[b[i]] = f"b{i}"

    for v in remaining:
        meets = [i for i in range(6) if meet[v, a[i]]]
        assert len(meets) == 2
        i, j = sorted(meets)
        labels[v] = f"c{i}{j}"

    assert len(labels) == 27
    return labels


def main() -> None:
    roots = _cds.construct_e8_roots()
    orbits = _cds.compute_we6_orbits(roots)
    orbit_sizes = [len(o) for o in orbits]
    assert sorted(orbit_sizes) == [1, 1, 1, 1, 1, 1, 27, 27, 27, 27, 27, 27, 72]

    idx_orb: Dict[int, int] = {}
    for oi, orb in enumerate(orbits):
        for v in orb:
            idx_orb[v] = oi

    root_index = {k2(roots[i]): i for i in range(len(roots))}

    # Identify the SU3 "3" orbit triple by weights.
    mix_orbs = [oi for oi, sz in enumerate(orbit_sizes) if sz == 27]
    weights = {oi: su3_weight(roots[orbits[oi][0]]) for oi in mix_orbs}
    weights_3 = {(1, 0), (-1, 1), (0, -1)}
    orbs_3 = sorted(
        [oi for oi in mix_orbs if weights[oi] in weights_3], key=lambda x: weights[x]
    )
    assert len(orbs_3) == 3
    oa, ob, oc = orbs_3

    triples = mine_mixed_triples_across_three_orbits(
        roots, orbits, root_index, idx_orb, (oa, ob, oc)
    )
    assert len(triples) == 270

    # Collapse to 27 E6-classes by E6 projection equality.
    e6_groups: Dict[Tuple[int, ...], int] = {}
    root_to_e6id: Dict[int, int] = {}
    for oi in orbs_3:
        for r_idx in orbits[oi]:
            k = e6_key(roots[r_idx])
            if k not in e6_groups:
                e6_groups[k] = len(e6_groups)
            root_to_e6id[r_idx] = e6_groups[k]
    assert len(e6_groups) == 27

    # Count E6 triples and multiplicities (should be 45, each with multiplicity 6).
    e6_triples: Set[Tuple[int, int, int]] = set()
    mult = Counter()
    for a, b, c in triples:
        t = tuple(sorted((root_to_e6id[a], root_to_e6id[b], root_to_e6id[c])))
        e6_triples.add(t)
        mult[t] += 1
    assert len(e6_triples) == 45
    assert set(mult.values()) == {6}

    # Independently compute the 45 tritangent planes as meet-graph triangles inside a base 27-orbit.
    base_orb = orbs_3[0]
    base_vertices = orbits[base_orb]
    base_roots = roots[base_vertices]
    gram = np.rint(base_roots @ base_roots.T).astype(int)
    meet = gram == 0
    np.fill_diagonal(meet, False)
    triangles = set()
    for i in range(27):
        for j in range(i + 1, 27):
            if not meet[i, j]:
                continue
            for k in range(j + 1, 27):
                if meet[i, k] and meet[j, k]:
                    triangles.add((i, j, k))
    assert len(triangles) == 45

    # Convert those triangles to E6 IDs and compare.
    base_to_e6id = {i: root_to_e6id[base_vertices[i]] for i in range(27)}
    e6_triangles = {
        tuple(sorted((base_to_e6id[i], base_to_e6id[j], base_to_e6id[k])))
        for (i, j, k) in triangles
    }
    assert e6_triangles == e6_triples

    # Provide a human-readable labeling via a double-six inside the same base 27-orbit.
    labels = build_double_six_labeling(gram)
    # Map E6 IDs -> a canonical representative vertex in base orbit and label.
    e6id_to_vertex: Dict[int, int] = {}
    for i in range(27):
        e6id = base_to_e6id[i]
        e6id_to_vertex.setdefault(e6id, i)

    labeled_terms = []
    for t in sorted(e6_triples):
        vs = [e6id_to_vertex[x] for x in t]
        labs = [labels[v] for v in vs]
        labeled_terms.append({"e6ids": list(t), "vertices": vs, "labels": labs})

    out = {
        "su3_three_orbits": [
            {"orbit": int(oi), "su3_weight": list(weights[oi])} for oi in orbs_3
        ],
        "mixed_triples_count": 270,
        "e6_cubic_nonzero_count": 45,
        "multiplicity_distribution": dict(Counter(mult.values())),
        "verified_equal_to_tritangent_planes": True,
        "cubic_terms": labeled_terms,
    }

    out_path = ROOT / "artifacts" / "e6_cubic_tensor_from_e8.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(
        "PASS: 270 mixed triples = ε_{abc} lift of 45 E6 cubic terms (tritangent planes)."
    )
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
