#!/usr/bin/env python3
"""
Extract a symmetric E6 cubic tensor d_{ijk} using the SU3 color gauge fixed from singleton ladders.

Steps:
  1) Load phase_bits[c][i] from artifacts/su3_color_gauge_from_singletons.json.
     These phases canonically identify the three color copies of the 27 as a single SU(3) fundamental.
  2) Enumerate the 270 ordered mixed triples (i,j,k) across the three color 27-orbits and their raw signs:
       raw(i,j,k) = signbit( ε(β_A, β_B) )  (since |N|=1 on these triples)
  3) Normalize by the SU3 gauge:
       s_norm = raw ⊕ phase0(i) ⊕ phase1(j) ⊕ phase2(k)
  4) Verify s_norm is constant across the 6 assignments per unordered triad {i,j,k}.
     If so, define d_{ {i,j,k} } = s_norm for that triad.

Outputs:
  artifacts/e6_cubic_from_su3_gauge.json
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


cds = _load_module(ROOT / "tools" / "compute_double_sixes.py", "compute_double_sixes")
cocycle = _load_module(ROOT / "tools" / "e8_lattice_cocycle.py", "e8_lattice_cocycle")

SU3_ALPHA = np.array([1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
SU3_BETA = np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0])


def k2(r: np.ndarray) -> Tuple[int, ...]:
    return tuple(int(round(2 * float(x))) for x in r.tolist())


def sign_to_bit(s: int) -> int:
    return 1 if s == -1 else 0


def bit_to_sign(b: int) -> int:
    return -1 if b else 1


def su3_weight(r: np.ndarray) -> Tuple[int, int]:
    return (
        int(round(float(np.dot(r, SU3_ALPHA)))),
        int(round(float(np.dot(r, SU3_BETA)))),
    )


def proj_to_su3(r: np.ndarray) -> np.ndarray:
    A = np.stack([SU3_ALPHA, SU3_BETA], axis=1)
    G = A.T @ A
    coeffs = np.linalg.solve(G, A.T @ r)
    return A @ coeffs


def e6_key(r: np.ndarray) -> Tuple[int, ...]:
    re6 = r - proj_to_su3(r)
    return tuple(int(round(2 * float(x))) for x in re6.tolist())


def load_phases() -> List[List[int]]:
    data = json.loads(
        (ROOT / "artifacts" / "su3_color_gauge_from_singletons.json").read_text(
            encoding="utf-8"
        )
    )
    if not data["solve"]["solvable"]:
        raise RuntimeError("SU3 gauge artifact is not solvable")
    return data["solution"]["phase_bits"]


def main() -> None:
    phase_bits = load_phases()

    roots = cds.construct_e8_roots()
    orbits = cds.compute_we6_orbits(roots)
    orbit_sizes = [len(o) for o in orbits]
    assert sorted(orbit_sizes) == [1, 1, 1, 1, 1, 1, 27, 27, 27, 27, 27, 27, 72]

    idx_orb: Dict[int, int] = {}
    for oi, orb in enumerate(orbits):
        for v in orb:
            idx_orb[v] = oi

    root_index = {k2(roots[i]): i for i in range(len(roots))}

    # Color orbits in the same order as the SU3 gauge solver.
    mix_orbs = [oi for oi, sz in enumerate(orbit_sizes) if sz == 27]
    weights = {oi: su3_weight(roots[orbits[oi][0]]) for oi in mix_orbs}
    weights_3 = {(1, 0), (-1, 1), (0, -1)}
    color_orbs = sorted(
        [oi for oi in mix_orbs if weights[oi] in weights_3], key=lambda x: weights[x]
    )
    assert len(color_orbs) == 3
    oa, ob, oc = color_orbs

    # E6 ids by projection across three color orbits.
    e6_groups: Dict[Tuple[int, ...], int] = {}
    root_to_e6id: Dict[int, int] = {}
    for oi in color_orbs:
        for ridx in orbits[oi]:
            k = e6_key(roots[ridx])
            if k not in e6_groups:
                e6_groups[k] = len(e6_groups)
            root_to_e6id[ridx] = e6_groups[k]
    assert len(e6_groups) == 27

    # Enumerate couplings and normalize.
    triad_vals: Dict[Tuple[int, int, int], List[int]] = defaultdict(list)
    for a_root in orbits[oa]:
        ka = k2(roots[a_root])
        i = root_to_e6id[a_root]
        for b_root in orbits[ob]:
            kb = k2(roots[b_root])
            j = root_to_e6id[b_root]
            need = tuple(-(ka[t] + kb[t]) for t in range(8))
            c_root = root_index.get(need)
            if c_root is None or idx_orb[c_root] != oc:
                continue
            k = root_to_e6id[c_root]
            raw = sign_to_bit(int(cocycle.epsilon_e8(ka, kb)))
            s_norm = raw ^ phase_bits[0][i] ^ phase_bits[1][j] ^ phase_bits[2][k]
            triad = tuple(sorted((i, j, k)))
            triad_vals[triad].append(s_norm)

    if len(triad_vals) != 45:
        raise RuntimeError(f"Expected 45 triads, got {len(triad_vals)}")

    mult = Counter(len(v) for v in triad_vals.values())
    if mult != {6: 45}:
        raise RuntimeError(f"Expected multiplicity 6 per triad, got {mult}")

    inconsistent = []
    d_bits: Dict[Tuple[int, int, int], int] = {}
    for t, vals in triad_vals.items():
        if len(set(vals)) != 1:
            inconsistent.append((t, vals))
        else:
            d_bits[t] = vals[0]

    out: Dict[str, object] = {
        "status": "ok",
        "counts": {
            "triads": 45,
            "couplings": 270,
            "inconsistent_triads": int(len(inconsistent)),
        },
    }
    if inconsistent:
        out["inconsistent_examples"] = [
            {"triad": list(t), "vals": v} for t, v in inconsistent[:5]
        ]
    else:
        d_signs = [bit_to_sign(d_bits[t]) for t in sorted(d_bits.keys())]
        out["d_triples"] = [
            {"triple": list(t), "sign": int(bit_to_sign(d_bits[t]))}
            for t in sorted(d_bits.keys())
        ]
        out["d_sign_distribution"] = dict(Counter(d_signs))

    out_path = ROOT / "artifacts" / "e6_cubic_from_su3_gauge.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(
        "PASS" if not inconsistent else "FAIL",
        "Extracted E6 cubic tensor from SU3 gauge.",
    )
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
