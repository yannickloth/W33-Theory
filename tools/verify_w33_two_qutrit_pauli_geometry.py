#!/usr/bin/env python3
"""
Certificate: W(3,3) / W33 is the commutation geometry of the 2-qutrit Pauli group.

Facts we verify computationally (no physics interpretation required):
  1) Points of W(3,3) are the 40 projective 1D subspaces of F3^4.
  2) Collinearity (W33 adjacency) is symplectic orthogonality ω(u,v)=0.
     This yields SRG(40,12,2,4).
  3) Identifying a phase-space vector (b1,b2,a1,a2) with the 2-qutrit Pauli
     operator (Z^a1 X^b1) ⊗ (Z^a2 X^b2), the orthogonality relation is exactly
     the operator commutation relation.
  4) Lines (40 of them) are maximal commuting classes (projectivized isotropic
     2D subspaces), each with 4 points.
  5) Spreads (36 of them) are partitions of the 40 points into 10 disjoint lines.
     In the 2-qutrit Hilbert space (dim 9), these correspond to stabilizer MUB sets
     (p^n+1 = 10 bases). We numerically verify MUB overlaps for one spread.

Outputs:
  - artifacts/w33_two_qutrit_pauli_geometry.json
  - artifacts/w33_two_qutrit_pauli_geometry.md
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from itertools import product
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "artifacts" / "w33_two_qutrit_pauli_geometry.json"
OUT_MD = ROOT / "artifacts" / "w33_two_qutrit_pauli_geometry.md"

MOD3 = 3


def _omega(x: tuple[int, int, int, int], y: tuple[int, int, int, int]) -> int:
    # Keep convention consistent with tools/compute_w33_incidence_code_ranks.py:
    # x = (b1,b2,a1,a2), y = (b1',b2',a1',a2')
    # ω(x,y) = b1*a1' - a1*b1' + b2*a2' - a2*b2'  (mod 3)
    return (x[0] * y[2] - x[2] * y[0] + x[1] * y[3] - x[3] * y[1]) % MOD3


def _proj_normalize(v: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    for i in range(4):
        if v[i] % MOD3 != 0:
            inv = 1 if v[i] % MOD3 == 1 else 2
            return tuple((inv * x) % MOD3 for x in v)
    raise ValueError("zero vector")


def _construct_points() -> list[tuple[int, int, int, int]]:
    pts: list[tuple[int, int, int, int]] = []
    seen: set[tuple[int, int, int, int]] = set()
    for v in product([0, 1, 2], repeat=4):
        if v == (0, 0, 0, 0):
            continue
        pv = _proj_normalize(v)
        if pv not in seen:
            seen.add(pv)
            pts.append(pv)
    if len(pts) != 40:
        raise RuntimeError(f"Expected 40 points, got {len(pts)}")
    return pts


def _line_from_pair(
    points: list[tuple[int, int, int, int]], i: int, j: int
) -> tuple[int, ...]:
    vi, vj = points[i], points[j]
    if _omega(vi, vj) != 0:
        raise ValueError("pair not orthogonal")
    combos = []
    for a in [0, 1, 2]:
        for b in [0, 1, 2]:
            if a == 0 and b == 0:
                continue
            w = tuple((a * vi[k] + b * vj[k]) % MOD3 for k in range(4))
            combos.append(_proj_normalize(w))
    uniq = sorted(set(combos))
    if len(uniq) != 4:
        raise RuntimeError(f"Expected 4 points on a line, got {len(uniq)}")
    idx = {p: t for t, p in enumerate(points)}
    return tuple(sorted(idx[p] for p in uniq))


def _construct_lines(points: list[tuple[int, int, int, int]]) -> list[tuple[int, ...]]:
    lines: set[tuple[int, ...]] = set()
    n = len(points)
    for i in range(n):
        for j in range(i + 1, n):
            if _omega(points[i], points[j]) == 0:
                lines.add(_line_from_pair(points, i, j))
    out = sorted(lines)
    if len(out) != 40:
        raise RuntimeError(f"Expected 40 lines, got {len(out)}")
    if any(len(L) != 4 for L in out):
        raise RuntimeError("Line size mismatch")
    return out


def _adjacency(points: list[tuple[int, int, int, int]]) -> np.ndarray:
    n = len(points)
    A = np.zeros((n, n), dtype=np.int8)
    for i in range(n):
        for j in range(i + 1, n):
            if _omega(points[i], points[j]) == 0:
                A[i, j] = 1
                A[j, i] = 1
    np.fill_diagonal(A, 0)
    return A


def _verify_srg(A: np.ndarray) -> dict[str, int]:
    n = A.shape[0]
    degs = A.sum(axis=1)
    if not np.all(degs == degs[0]):
        raise RuntimeError(f"Non-regular degrees: {sorted(set(degs.tolist()))}")
    k = int(degs[0])
    lam_set: set[int] = set()
    mu_set: set[int] = set()
    for i in range(n):
        for j in range(i + 1, n):
            c = int(np.dot(A[i], A[j]))
            if A[i, j] == 1:
                lam_set.add(c)
            else:
                mu_set.add(c)
    if len(lam_set) != 1 or len(mu_set) != 1:
        raise RuntimeError(f"SRG params not constant: λ={lam_set}, μ={mu_set}")
    lam = next(iter(lam_set))
    mu = next(iter(mu_set))
    return {"n": n, "k": k, "lambda": lam, "mu": mu}


def _qutrit_XZ() -> tuple[np.ndarray, np.ndarray, complex]:
    w = np.exp(2j * np.pi / 3)
    X = np.zeros((3, 3), dtype=np.complex128)
    for i in range(3):
        X[(i + 1) % 3, i] = 1.0
    Z = np.diag([w**i for i in range(3)]).astype(np.complex128)
    # Verify Z X = w X Z
    if not np.allclose(Z @ X, w * (X @ Z)):
        raise RuntimeError("qutrit relation ZX = ω XZ failed")
    return X, Z, w


def _pauli_2qutrit(
    v: tuple[int, int, int, int], X: np.ndarray, Z: np.ndarray
) -> np.ndarray:
    # v = (b1,b2,a1,a2)
    b1, b2, a1, a2 = [int(x) % MOD3 for x in v]

    def single(a: int, b: int) -> np.ndarray:
        return np.linalg.matrix_power(Z, a) @ np.linalg.matrix_power(X, b)

    return np.kron(single(a1, b1), single(a2, b2))


def _commutes(U: np.ndarray, V: np.ndarray, atol: float = 1e-12) -> bool:
    return np.allclose(U @ V, V @ U, atol=atol)


def _joint_eigenbasis(G1: np.ndarray, G2: np.ndarray) -> np.ndarray:
    """
    Stabilizer-style joint eigenbasis for commuting 3-torsion unitaries G1,G2.
    Uses projectors:
      P_{s,t} = (1/9) Σ_{i,j=0..2} ω^{-is - jt} G1^i G2^j
    Returns a 9×9 unitary matrix whose columns are eigenvectors.
    """
    _, _, w = _qutrit_XZ()
    basis = np.zeros((9, 9), dtype=np.complex128)
    col = 0
    for s in range(3):
        for t in range(3):
            P = np.zeros((9, 9), dtype=np.complex128)
            for i in range(3):
                for j in range(3):
                    P += (w ** (-(i * s + j * t))) * (
                        np.linalg.matrix_power(G1, i) @ np.linalg.matrix_power(G2, j)
                    )
            P /= 9.0
            # P should be rank-1 projector; extract a nonzero column
            norms = np.linalg.norm(P, axis=0)
            k = int(np.argmax(norms))
            v = P[:, k]
            nv = np.linalg.norm(v)
            if nv < 1e-10:
                raise RuntimeError("Failed to extract projector vector")
            basis[:, col] = v / nv
            col += 1
    # Orthonormalize (projectors should already yield orthonormal basis, but be robust)
    Q, _ = np.linalg.qr(basis)
    return Q


def _find_spreads(lines: list[tuple[int, ...]], n_points: int = 40) -> list[list[int]]:
    """
    Exact-cover backtracking: choose 10 pairwise disjoint lines covering all 40 points.
    Returns spreads as lists of line indices (sorted).
    """
    line_masks = []
    point_to_lines: list[list[int]] = [[] for _ in range(n_points)]
    for idx, L in enumerate(lines):
        mask = 0
        for p in L:
            mask |= 1 << p
            point_to_lines[p].append(idx)
        line_masks.append(mask)

    full_mask = (1 << n_points) - 1
    spreads: list[list[int]] = []

    def backtrack(chosen: list[int], used_mask: int) -> None:
        if used_mask == full_mask:
            if len(chosen) != 10:
                raise RuntimeError("cover reached with wrong line count")
            spreads.append(sorted(chosen))
            return
        # pick first uncovered point
        p = int((~used_mask) & full_mask).bit_length() - 1
        for li in point_to_lines[p]:
            m = line_masks[li]
            if used_mask & m:
                continue
            if len(chosen) >= 10:
                continue
            chosen.append(li)
            backtrack(chosen, used_mask | m)
            chosen.pop()

    backtrack([], 0)
    # Deduplicate (different construction orders)
    uniq = sorted({tuple(s) for s in spreads})
    return [list(s) for s in uniq]


@dataclass(frozen=True)
class MUBCheck:
    spread_index: int
    max_overlap_dev: float


def main() -> int:
    points = _construct_points()
    lines = _construct_lines(points)
    A = _adjacency(points)
    srg = _verify_srg(A)

    X, Z, _w = _qutrit_XZ()

    # Verify commutation <-> orthogonality on all pairs.
    max_comm_error = 0.0
    for i in range(40):
        Ui = _pauli_2qutrit(points[i], X, Z)
        for j in range(i + 1, 40):
            Uj = _pauli_2qutrit(points[j], X, Z)
            commute = _commutes(Ui, Uj)
            ortho = _omega(points[i], points[j]) == 0
            if commute != ortho:
                raise RuntimeError(f"Mismatch commute/orth at pair {(i,j)}")
            if ortho:
                err = float(np.linalg.norm(Ui @ Uj - Uj @ Ui))
                if err > max_comm_error:
                    max_comm_error = err

    spreads = _find_spreads(lines, n_points=40)
    if len(spreads) != 36:
        raise RuntimeError(f"Expected 36 spreads, got {len(spreads)}")

    # MUB check for the first spread: build 10 stabilizer bases and verify overlaps.
    spread0 = spreads[0]
    bases: list[np.ndarray] = []
    for li in spread0:
        L = lines[li]
        v1 = points[L[0]]
        v2 = points[L[1]]
        G1 = _pauli_2qutrit(v1, X, Z)
        G2 = _pauli_2qutrit(v2, X, Z)
        if not _commutes(G1, G2):
            raise RuntimeError("Line generators do not commute")
        B = _joint_eigenbasis(G1, G2)
        bases.append(B)

    target = 1.0 / 9.0
    max_dev = 0.0
    for i in range(len(bases)):
        for j in range(i + 1, len(bases)):
            M = bases[i].conj().T @ bases[j]
            dev = float(np.max(np.abs(np.abs(M) ** 2 - target)))
            if dev > max_dev:
                max_dev = dev

    mub_check = MUBCheck(spread_index=0, max_overlap_dev=max_dev)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "w33_srg": srg,
        "points_count": len(points),
        "lines_count": len(lines),
        "spreads_count": len(spreads),
        "max_commutation_error_on_edges": max_comm_error,
        "mub_check": asdict(mub_check),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    md = []
    md.append("# W33 as 2-qutrit Pauli commutation geometry\n")
    md.append(f"- Points: `{len(points)}` (projective 1D subspaces of F3^4)")
    md.append(
        f"- Lines: `{len(lines)}` (projective isotropic 2D subspaces; size 4 each)"
    )
    md.append(
        f"- W33 (collinearity graph): `SRG({srg['n']},{srg['k']},{srg['lambda']},{srg['mu']})`"
    )
    md.append(
        f"- Spreads: `{len(spreads)}` (each is 10 disjoint lines covering all points)"
    )
    md.append("")
    md.append("## Pauli mapping (2 qutrits, dim 9)\n")
    md.append(
        "- Identify a phase-space vector `v=(b1,b2,a1,a2)∈F3^4` with the operator\n"
        "  `(Z^a1 X^b1) ⊗ (Z^a2 X^b2)`.\n"
        "- Then `ω(u,v)=0` iff the corresponding operators commute.\n"
    )
    md.append(f"- Max commutator norm on commuting pairs: `{max_comm_error:.3e}`\n")
    md.append("## Stabilizer MUB certificate (one spread)\n")
    md.append(
        "- A spread gives `10 = 3^2 + 1` commuting classes → 10 stabilizer bases in dimension 9.\n"
        "- Verified unbiasedness for the first spread: max deviation of `|⟨ψ|φ⟩|^2` from `1/9` is\n"
        f"  `{mub_check.max_overlap_dev:.3e}`.\n"
    )
    OUT_MD.write_text("\n".join(md), encoding="utf-8")

    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"SRG: {srg}")
    print(f"Spreads: {len(spreads)}")
    print(f"MUB max dev (spread 0): {mub_check.max_overlap_dev:.3e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
