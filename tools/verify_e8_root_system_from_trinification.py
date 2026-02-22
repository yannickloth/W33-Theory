#!/usr/bin/env python3
"""
Verify the E8 root system from the Z3-graded trinification decomposition:

  E8  ≅  (e6 ⊕ a2)  ⊕  (27 ⊗ 3)  ⊕  (27* ⊗ 3*)

This is a *pure Cartan/weight* certificate (independent of matrix commutator numerics):

  - Uses the E6 Cartan matrix to generate all 72 E6 roots.
  - Uses the certified 27-rep Chevalley Cartan matrices (diagonal `h_i`) to get the 27 weights.
  - Uses the standard A2 weights of the 3: (1,0), (-1,1), (0,-1) (in simple-coroot coords).
  - Forms the 240 E8 roots as:
      (E6_root, 0)           72
      (0, A2_root)            6
      (E6_weight, A2_weight) 81
      (-E6_weight,-A2_weight) 81

Then it checks:
  - exactly 240 nonzero roots
  - rank 8 of Σ_{α} α α^T
  - all squared lengths equal under the induced form

Outputs:
  - artifacts/verify_e8_root_system_from_trinification.json
  - artifacts/verify_e8_root_system_from_trinification.md
"""

from __future__ import annotations

import json
from collections import deque
from itertools import combinations_with_replacement
from pathlib import Path
from typing import Dict, List, Sequence, Set, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


E6_CARTAN = np.array(
    [
        [2, -1, 0, 0, 0, 0],
        [-1, 2, -1, 0, 0, 0],
        [0, -1, 2, -1, -1, 0],
        [0, 0, -1, 2, 0, 0],
        [0, 0, -1, 0, 2, -1],
        [0, 0, 0, 0, -1, 2],
    ],
    dtype=int,
)


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _reflect_root_coeff(
    coeff: Tuple[int, ...], i: int, cartan: np.ndarray
) -> Tuple[int, ...]:
    c = np.array(coeff, dtype=int)
    m = int(cartan[i] @ c)  # beta(h_i)
    c2 = c.copy()
    c2[i] -= m
    return tuple(int(x) for x in c2.tolist())


def generate_roots_from_cartan(cartan: np.ndarray) -> Set[Tuple[int, ...]]:
    """
    Generate all roots as weight-values α(h) in Z^r by:
      - BFS in the simple-root coefficient lattice via reflections,
      - mapping coeffs -> α(h) = Cartan @ coeff.
    """
    r = cartan.shape[0]
    coeffs: Set[Tuple[int, ...]] = set()
    q: deque[Tuple[int, ...]] = deque()
    for i in range(r):
        v = [0] * r
        v[i] = 1
        for sgn in (1, -1):
            t = tuple(int(sgn * x) for x in v)
            coeffs.add(t)
            q.append(t)
    while q:
        c = q.popleft()
        for i in range(r):
            c2 = _reflect_root_coeff(c, i, cartan)
            if c2 not in coeffs:
                coeffs.add(c2)
                q.append(c2)
    roots = {
        tuple(int(x) for x in (cartan @ np.array(c, dtype=int)).tolist())
        for c in coeffs
    }
    roots.discard(tuple([0] * r))
    return roots


def load_e6_27_weights_from_chevalley() -> np.ndarray:
    """
    Load the 27 weights μ(h_i) from the certified Chevalley-exported 27-rep generators.
    """
    path = ROOT / "artifacts" / "e6_27rep_minuscule_generators.npy"
    if not path.exists():
        raise FileNotFoundError(
            "Missing artifacts/e6_27rep_minuscule_generators.npy. "
            "Run: python3 tools/build_e6_27rep_minuscule.py --export-basis78"
        )
    obj = np.load(path, allow_pickle=True).item()
    h = np.array(obj["h"], dtype=np.complex128)  # (6,27,27)
    if h.shape != (6, 27, 27):
        raise ValueError(f"Unexpected h shape {h.shape}")
    w = np.stack([np.diag(h[i]).real for i in range(6)], axis=1)
    wi = np.rint(w).astype(int)
    return wi


def a2_weights_fund3() -> np.ndarray:
    """
    Weights of the 3 of A2 in the simple-coroot basis:
      (1,0), (-1,1), (0,-1)
    """
    return np.array([[1, 0], [-1, 1], [0, -1]], dtype=int)


def a2_roots_from_weights(w3: np.ndarray) -> Set[Tuple[int, int]]:
    roots: Set[Tuple[int, int]] = set()
    for i in range(3):
        for j in range(3):
            if i == j:
                continue
            roots.add(tuple(int(x) for x in (w3[i] - w3[j]).tolist()))
    roots.discard((0, 0))
    return roots


def main() -> None:
    # E6 roots and 27 weights in coroot-coordinates (h_i).
    e6_roots = generate_roots_from_cartan(E6_CARTAN)
    w27 = load_e6_27_weights_from_chevalley()

    # A2 weights and roots.
    w3 = a2_weights_fund3()
    a2_roots = a2_roots_from_weights(w3)

    # Build E8 roots in Z^8 = Z^6 ⊕ Z^2.
    roots8: Set[Tuple[int, ...]] = set()

    for r in e6_roots:
        roots8.add(tuple(list(r) + [0, 0]))
    for r in a2_roots:
        roots8.add(tuple([0] * 6 + list(r)))

    for mu in w27:
        for nu in w3:
            roots8.add(tuple(list(mu.tolist()) + list(nu.tolist())))
            roots8.add(tuple(list((-mu).tolist()) + list((-nu).tolist())))

    roots8.discard(tuple([0] * 8))

    # Induced form from the adjoint trace on Cartan:
    #   B(H,H') = Tr(ad(H) ad(H')) = Σ_{α∈Φ} α(H) α(H')
    R = np.array(sorted(roots8), dtype=float)
    B = R.T @ R
    rank = int(np.linalg.matrix_rank(B))
    Binv = np.linalg.inv(B)
    sq_lengths = np.sum(R * (R @ Binv), axis=1)
    sq_min = float(np.min(sq_lengths))
    sq_max = float(np.max(sq_lengths))

    # Sanity: check no duplicates up to sign beyond expected.
    neg_missing = sum(1 for r in roots8 if tuple((-np.array(r)).tolist()) not in roots8)

    status = "ok"
    if len(roots8) != 240:
        status = "fail"
    if rank != 8:
        status = "fail"
    if sq_max - sq_min > 1e-12:
        status = "fail"
    if neg_missing != 0:
        status = "fail"

    out = {
        "status": status,
        "counts": {
            "e6_roots": int(len(e6_roots)),
            "a2_roots": int(len(a2_roots)),
            "w27": int(w27.shape[0]),
            "w3": int(w3.shape[0]),
            "e8_roots_total": int(len(roots8)),
            "negation_missing": int(neg_missing),
        },
        "form": {
            "rank": int(rank),
            "sq_length_min": float(sq_min),
            "sq_length_max": float(sq_max),
            "sq_length_spread": float(sq_max - sq_min),
        },
        "paths": {
            "e6_27rep_minuscule_generators": str(
                ROOT / "artifacts" / "e6_27rep_minuscule_generators.npy"
            ),
        },
        "notes": {
            "interpretation": "A rank-8 simply-laced root system with 240 roots is uniquely E8.",
            "construction": "Roots are in coroot-eigenvalue coordinates: first 6 for E6, last 2 for A2.",
        },
    }

    out_json = ROOT / "artifacts" / "verify_e8_root_system_from_trinification.json"
    out_md = ROOT / "artifacts" / "verify_e8_root_system_from_trinification.md"
    _write_json(out_json, out)

    md: List[str] = []
    md.append("# Verify E8 root system from trinification weights\n")
    md.append(f"- status: `{status}`")
    md.append(f"- roots: `{out['counts']['e8_roots_total']}` (expected 240)")
    md.append(f"- form rank: `{rank}` (expected 8)")
    md.append(
        f"- squared length spread: `{out['form']['sq_length_spread']}` (expected ~0)\n"
    )
    md.append("## Breakdown")
    md.append(f"- E6 roots: `{out['counts']['e6_roots']}`")
    md.append(f"- A2 roots: `{out['counts']['a2_roots']}`")
    md.append(f"- (27,3) weights: `{out['counts']['w27']}×{out['counts']['w3']} = 81`")
    md.append("- (27*,3*) weights: `81`\n")
    md.append(f"- JSON: `{out_json}`")
    _write_md(out_md, md)

    print(f"status={status} roots={len(roots8)} rank={rank} sq_spread={sq_max-sq_min}")
    if status != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
