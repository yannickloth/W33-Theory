#!/usr/bin/env python3
"""
Mine the sparse cubic-coupling hypergraphs inside the mixed roots (27,3) ⊕ (27bar,3bar).

From E8 → E6 ⊕ A2, the 240 roots split as:
  - 72 roots in E6
  - 6 roots in A2
  - 162 mixed roots = 6 × 27  (these are the (27,3) ⊕ (27bar,3bar) root spaces)

Among the mixed roots, our earlier root-addition scan shows that α+β+γ=0 triples exist only in:
  - one orbit-triple of type 3 ⊗ 3 ⊗ 3,
  - one orbit-triple of type 3bar ⊗ 3bar ⊗ 3bar,
and (crucially) each triple uses one element from each of the three 27-orbits involved.

This script constructs those two 3-partite 3-uniform hypergraphs and reports:
  - number of triples,
  - per-vertex degrees (should be uniform),
  - pair-incidence multiplicities,
  - basic connectivity.

It writes a JSON artifact that can be used to try to align these triples with W33 "blocks"/bipartitions,
Schläfli double-sixes, or other structures.
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


def rep_of_weight(w: Tuple[int, int]) -> str:
    weights_3 = {(1, 0), (-1, 1), (0, -1)}
    weights_3bar = {(0, 1), (1, -1), (-1, 0)}
    if w in weights_3:
        return "3"
    if w in weights_3bar:
        return "3bar"
    return "?"


def build_indices() -> (
    Tuple[np.ndarray, List[List[int]], Dict[Tuple[int, ...], int], Dict[int, int]]
):
    roots = construct_e8_roots()
    orbits = compute_we6_orbits(roots)
    keys = np.array(
        [[int(round(2 * float(x))) for x in roots[i]] for i in range(len(roots))],
        dtype=int,
    )
    root_index = {tuple(keys[i].tolist()): i for i in range(len(roots))}
    idx_orb: Dict[int, int] = {}
    for oi, orb in enumerate(orbits):
        for v in orb:
            idx_orb[v] = oi
    return roots, orbits, root_index, idx_orb


def mine_orbit_triple(
    roots: np.ndarray,
    orbits: List[List[int]],
    root_index: Dict[Tuple[int, ...], int],
    idx_orb: Dict[int, int],
    orbit_triple: Tuple[int, int, int],
) -> Set[Tuple[int, int, int]]:
    """
    Return unique triples (a,b,c) with a in orbA, b in orbB, c in orbC and root_a+root_b+root_c=0.
    We count each triple exactly once by iterating ordered pairs (a,b) and computing c.
    """
    oa, ob, oc = orbit_triple
    triples: Set[Tuple[int, int, int]] = set()
    for a in orbits[oa]:
        ka = k2(roots[a])
        for b in orbits[ob]:
            kb = k2(roots[b])
            need = tuple(-(ka[i] + kb[i]) for i in range(8))
            c = root_index.get(need)
            if c is None or idx_orb[c] != oc:
                continue
            triples.add((a, b, c))
    return triples


def analyze_hypergraph(
    triples: Set[Tuple[int, int, int]],
    parts: Tuple[List[int], List[int], List[int]],
) -> Dict[str, object]:
    A, B, C = parts
    degA = Counter()
    degB = Counter()
    degC = Counter()
    pairAB = Counter()
    pairAC = Counter()
    pairBC = Counter()

    for a, b, c in triples:
        degA[a] += 1
        degB[b] += 1
        degC[c] += 1
        pairAB[(a, b)] += 1
        pairAC[(a, c)] += 1
        pairBC[(b, c)] += 1

    # Connectivity in the 3-partite incidence graph (triples as hyperedges):
    # Build adjacency among vertices if they appear together in a triple.
    neighbors: Dict[int, Set[int]] = defaultdict(set)
    for a, b, c in triples:
        neighbors[a].update([b, c])
        neighbors[b].update([a, c])
        neighbors[c].update([a, b])

    seen = set()
    comps = []
    for v in A + B + C:
        if v in seen:
            continue
        stack = [v]
        comp = []
        seen.add(v)
        while stack:
            x = stack.pop()
            comp.append(x)
            for y in neighbors.get(x, set()):
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        comps.append(comp)

    return {
        "triple_count": int(len(triples)),
        "degree_distributions": {
            "A": dict(Counter(degA.values())),
            "B": dict(Counter(degB.values())),
            "C": dict(Counter(degC.values())),
        },
        "pair_multiplicity_distributions": {
            "AB": dict(Counter(pairAB.values())),
            "AC": dict(Counter(pairAC.values())),
            "BC": dict(Counter(pairBC.values())),
        },
        "component_sizes": sorted((len(c) for c in comps), reverse=True),
    }


def main() -> None:
    roots, orbits, root_index, idx_orb = build_indices()
    orbit_sizes = [len(o) for o in orbits]

    mix_orbs = [oi for oi, sz in enumerate(orbit_sizes) if sz == 27]
    mix_weights = {oi: su3_weight(roots[orbits[oi][0]]) for oi in mix_orbs}
    mix_rep = {oi: rep_of_weight(mix_weights[oi]) for oi in mix_orbs}

    # Identify which 3 MIX27 orbits are "3" and which 3 are "3bar".
    orbs_3 = sorted(
        [oi for oi in mix_orbs if mix_rep[oi] == "3"], key=lambda x: mix_weights[x]
    )
    orbs_3bar = sorted(
        [oi for oi in mix_orbs if mix_rep[oi] == "3bar"], key=lambda x: mix_weights[x]
    )

    print("MIX27 orbits (3):", [(oi, mix_weights[oi]) for oi in orbs_3])
    print("MIX27 orbits (3bar):", [(oi, mix_weights[oi]) for oi in orbs_3bar])

    # Mine the two 3-partite hypergraphs.
    tri_3 = mine_orbit_triple(roots, orbits, root_index, idx_orb, tuple(orbs_3))  # type: ignore[arg-type]
    tri_3bar = mine_orbit_triple(roots, orbits, root_index, idx_orb, tuple(orbs_3bar))  # type: ignore[arg-type]

    print("\nCubic hypergraphs (unique triples a+b+c=0):")
    print("  3    orbit triple:", tuple(orbs_3), "triples:", len(tri_3))
    print("  3bar orbit triple:", tuple(orbs_3bar), "triples:", len(tri_3bar))

    analysis_3 = analyze_hypergraph(
        tri_3, (orbits[orbs_3[0]], orbits[orbs_3[1]], orbits[orbs_3[2]])
    )
    analysis_3bar = analyze_hypergraph(
        tri_3bar, (orbits[orbs_3bar[0]], orbits[orbs_3bar[1]], orbits[orbs_3bar[2]])
    )

    print("\n3 hypergraph degree distributions:", analysis_3["degree_distributions"])
    print(
        "3 hypergraph pair multiplicities:",
        analysis_3["pair_multiplicity_distributions"],
    )
    print("3 hypergraph component sizes:", analysis_3["component_sizes"][:8])

    print(
        "\n3bar hypergraph degree distributions:", analysis_3bar["degree_distributions"]
    )
    print(
        "3bar hypergraph pair multiplicities:",
        analysis_3bar["pair_multiplicity_distributions"],
    )
    print("3bar hypergraph component sizes:", analysis_3bar["component_sizes"][:8])

    out = {
        "mix_orbits": {
            "three": [{"orbit": oi, "weight": list(mix_weights[oi])} for oi in orbs_3],
            "threebar": [
                {"orbit": oi, "weight": list(mix_weights[oi])} for oi in orbs_3bar
            ],
        },
        "hypergraphs": {
            "three": {
                "orbit_triple": list(orbs_3),
                "triple_count": analysis_3["triple_count"],
                "analysis": analysis_3,
            },
            "threebar": {
                "orbit_triple": list(orbs_3bar),
                "triple_count": analysis_3bar["triple_count"],
                "analysis": analysis_3bar,
            },
        },
        "notes": {
            "triple_definition": "Unique triples (a,b,c) with a in orbitA, b in orbitB, c in orbitC and root_a+root_b+root_c=0.",
            "expected_rep_rule": "Only 3⊗3⊗3 and 3bar⊗3bar⊗3bar appear (matches A2 epsilon selection).",
        },
    }

    out_path = ROOT / "artifacts" / "mixed_cubic_hypergraphs.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
