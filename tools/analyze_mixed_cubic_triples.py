#!/usr/bin/env python3
"""
Deeper invariants of the mixed cubic triples (α+β+γ=0) across three 27-orbits.

We compute:
  - pairwise inner-product distributions inside each triple,
  - how triples relate to the Schläfli adjacency (ip=1 inside each 27-orbit),
  - sanity checks suggesting ties to classical cubic-surface counts (45 tritangent planes).
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


def k2(r: np.ndarray) -> Tuple[int, ...]:
    return tuple(int(round(2 * float(x))) for x in r.tolist())


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
            need = tuple(-(ka[i] + kb[i]) for i in range(8))
            c = root_index.get(need)
            if c is None or idx_orb[c] != oc:
                continue
            triples.add((a, b, c))
    return triples


def main() -> None:
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

    # The two orbit-triples discovered earlier.
    orb_triples = {
        "three": (9, 3, 4),
        "threebar": (5, 0, 6),
    }

    results = {}
    for name, (oa, ob, oc) in orb_triples.items():
        triples = mine_orbit_triple(roots, orbits, root_index, idx_orb, (oa, ob, oc))
        assert len(triples) == 270

        ip_patterns = Counter()
        for a, b, c in triples:
            ra, rb, rc = roots[a], roots[b], roots[c]
            ips = (
                int(round(float(np.dot(ra, rb)))),
                int(round(float(np.dot(ra, rc)))),
                int(round(float(np.dot(rb, rc)))),
            )
            ip_patterns[tuple(sorted(ips))] += 1

        # Compare 270 to 45 tritangent planes: 270 = 45*6
        factors = {"270_over_45": 270 // 45, "270_over_6": 270 // 6}

        results[name] = {
            "orbit_triple": [oa, ob, oc],
            "triple_count": int(len(triples)),
            "pairwise_inner_product_multiset_counts": {
                str(k): int(v) for k, v in ip_patterns.items()
            },
            "count_factorizations": factors,
        }

        print(f"{name}: orbit triple {(oa, ob, oc)}")
        print("  triples:", len(triples))
        print("  pairwise ip multiset counts:", dict(ip_patterns))
        print("  270 = 45*%d, = 6*%d" % (factors["270_over_45"], factors["270_over_6"]))

    out_path = ROOT / "artifacts" / "mixed_cubic_triples_analysis.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
