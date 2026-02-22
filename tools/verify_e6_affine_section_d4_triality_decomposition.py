#!/usr/bin/env python3
"""
Certificate: an affine firewall section induces a D4⊕u(1)^2 split of the E6-27 into 8+8+8+1+1+1.

From `tools/verify_e6_affine_section_stabilizer_d4_u1u1.py` we know:
  Stabilizer_e6(section) has dim 30 with derived dim 28, matching D4 ⊕ u(1)^2.

Here we go one layer deeper and recover the *representation decomposition* of the 27
under that stabilizer:

  27  =  8 ⊕ 8 ⊕ 8  ⊕  1 ⊕ 1 ⊕ 1

Mechanism:
  - Use the exported diagonal Cartan basis `Cartan_mats.npy` (6 commuting diagonals).
  - Find the 2-dimensional center directions in Cartan that commute with the stabilizer's derived algebra
    by solving linear constraints on weight differences across stabilizer support edges.
  - The resulting U(1)^2 charges split the 27 basis vectors into 6 charge-clusters:
      three clusters of size 8 (the D4 triality 8_v, 8_s, 8_c),
      and three singlets.

Inputs:
  - artifacts/e6_27rep_basis_export/E6_basis_78.npy
  - artifacts/e6_27rep_basis_export/Cartan_mats.npy
  - artifacts/e6_cubic_affine_heisenberg_model.json

Outputs:
  - artifacts/e6_affine_section_d4_triality_decomposition.json
  - artifacts/e6_affine_section_d4_triality_decomposition.md
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

IN_E6_BASIS = ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
IN_CARTAN = ROOT / "artifacts" / "e6_27rep_basis_export" / "Cartan_mats.npy"
IN_HEIS = ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json"

OUT_JSON = ROOT / "artifacts" / "e6_affine_section_d4_triality_decomposition.json"
OUT_MD = ROOT / "artifacts" / "e6_affine_section_d4_triality_decomposition.md"


def _u_values() -> List[Tuple[int, int]]:
    return [(x, y) for x in range(3) for y in range(3)]


def _affine_section_rows(
    hz_to_e6: Dict[Tuple[Tuple[int, int], int], int], *, a: int, b: int, c: int
) -> List[int]:
    rows: List[int] = []
    for x, y in _u_values():
        z = int((a * x + b * y + c) % 3)
        rows.append(int(hz_to_e6[((x, y), z)]))
    return sorted(rows)


def _nullspace(A: np.ndarray, *, rel_tol: float) -> Tuple[np.ndarray, float, int]:
    _U, s, Vh = np.linalg.svd(A, full_matrices=False)
    tol = float(s[0] * rel_tol) if s.size else 1e-12
    rank = int(np.sum(s > tol))
    N = Vh[rank:].conj().T
    return N, tol, rank


def main() -> None:
    B = np.load(IN_E6_BASIS).astype(np.complex128)  # (78,27,27)
    H = np.load(IN_CARTAN).astype(np.complex128)  # (6,27,27), diagonal
    if B.shape != (78, 27, 27) or H.shape != (6, 27, 27):
        raise RuntimeError(f"Unexpected shapes: basis {B.shape}, cartan {H.shape}")

    # weights of the 27 under the diagonal Cartan
    weights = np.stack([np.diag(H[i]).real for i in range(6)], axis=1)  # (27,6)

    heis = json.loads(IN_HEIS.read_text(encoding="utf-8"))
    e6_to_hz = {
        int(k): (tuple(v["u"]), int(v["z"]))
        for k, v in heis["e6id_to_heisenberg"].items()
    }
    hz_to_e6 = {(u, z): e6id for e6id, (u, z) in e6_to_hz.items()}

    # Use a canonical affine section (a,b,c)=(0,0,0). (All affine sections are conjugate.)
    a = b = c = 0
    rows = _affine_section_rows(hz_to_e6, a=a, b=b, c=c)
    inside = set(rows)
    outside = [i for i in range(27) if i not in inside]

    inside_arr = np.array(rows, dtype=int)
    outside_arr = np.array(outside, dtype=int)

    # Stabilizer nullspace in the 78D E6 span.
    block = B[:, outside_arr[:, None], inside_arr[None, :]]  # (78,18,9)
    A = block.transpose(1, 2, 0).reshape(
        len(outside_arr) * len(inside_arr), 78
    )  # (162,78)
    N, tol, rank = _nullspace(A, rel_tol=1e-10)
    stab_dim = int(N.shape[1])
    if stab_dim != 30:
        raise RuntimeError(
            f"Unexpected stabilizer dim {stab_dim} (rank {rank}, tol {tol})"
        )

    # Stabilizer basis matrices in End(27)
    M = np.tensordot(N.T, B, axes=(1, 0))  # (30,27,27)

    # Find the 2D center directions in Cartan that commute with the stabilizer derived algebra.
    # Because Cartan is diagonal, commuting constraints are linear in the weight differences across support edges.
    th = 1e-9
    diffs: List[np.ndarray] = []
    for X in M:
        idx = np.argwhere(np.abs(X) > th)
        for p, q in idx:
            if p == q:
                continue
            diffs.append(weights[p] - weights[q])
    D = np.array(diffs, dtype=float)
    _U2, s2, Vh2 = np.linalg.svd(D, full_matrices=False)
    tol2 = float(s2[0] * 1e-10) if s2.size else 1e-12
    r2 = int(np.sum(s2 > tol2))
    center_dim = int(6 - r2)
    if center_dim != 2:
        raise RuntimeError(f"Expected center dim 2, got {center_dim} (rank {r2})")
    T = Vh2[r2:].T  # (6,2) basis for center directions (in Cartan coefficient space)

    # Compute U(1)^2 charges and cluster the 27 basis vectors.
    charges = weights @ T  # (27,2)
    charges_r = np.round(charges, 6)
    clusters = defaultdict(list)
    for i, ch in enumerate(charges_r):
        clusters[tuple(ch)].append(int(i))

    size_hist = Counter(len(v) for v in clusters.values())
    expected = Counter({8: 3, 1: 3})
    ok = size_hist == expected

    report = {
        "status": "ok" if ok else "unexpected_cluster_sizes",
        "section": {"affine_params": {"a": a, "b": b, "c": c}, "rows": rows},
        "stabilizer": {"dim": stab_dim, "derived_dim_expected": 28, "center_dim": 2},
        "center_covar": {
            "diff_constraint_rank": int(r2),
            "center_basis_T": np.round(T, 6).tolist(),
        },
        "clusters": {
            "num_clusters": int(len(clusters)),
            "size_hist": dict(size_hist),
            "clusters_by_charge": {str(k): v for k, v in clusters.items()},
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    md: List[str] = []
    md.append("# D4 triality decomposition induced by an affine firewall section\n")
    md.append("")
    md.append(f"- stabilizer dim: `{stab_dim}` (expected `30`)")
    md.append(f"- inferred center dim (Cartan commuting directions): `{center_dim}`")
    md.append(f"- charge cluster size histogram: `{dict(size_hist)}`")
    md.append("")
    md.append("## Result\n")
    if ok:
        md.append(
            "Recovered the expected split: `27 = 8 + 8 + 8 + 1 + 1 + 1` under `D4 ⊕ u(1)^2`."
        )
    else:
        md.append("Cluster sizes did not match the expected `8,8,8,1,1,1` pattern.")
    md.append("")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
