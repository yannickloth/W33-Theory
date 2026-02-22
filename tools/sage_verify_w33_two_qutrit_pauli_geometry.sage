#!/usr/bin/env sage
"""
Sage cross-check: W33 = W(3,3) = 2-qutrit Pauli commutation geometry.

This mirrors (and independently verifies) the Python certificate in:
  tools/verify_w33_two_qutrit_pauli_geometry.py

We verify:
  - 40 projective points of PG(3,3) (1D subspaces of F3^4)
  - adjacency via symplectic orthogonality gives SRG(40,12,2,4)
  - 40 totally isotropic lines, each of size 4
  - 36 spreads (10 disjoint lines covering all points)
  - exact commutation check using 2-qutrit Pauli matrices over CyclotomicField(3)

Outputs:
  - artifacts/sage_w33_two_qutrit_pauli_geometry.json
  - artifacts/sage_w33_two_qutrit_pauli_geometry.md
"""

import json
from pathlib import Path

ROOT = Path(".").resolve()
OUT_JSON = ROOT / "artifacts" / "sage_w33_two_qutrit_pauli_geometry.json"
OUT_MD = ROOT / "artifacts" / "sage_w33_two_qutrit_pauli_geometry.md"

F = GF(3)
V = VectorSpace(F, 4)


def omega(x, y):
    # x=(b1,b2,a1,a2), y=(b1',b2',a1',a2')
    return (x[0] * y[2] - x[2] * y[0] + x[1] * y[3] - x[3] * y[1]) % 3


def proj_normalize(v):
    v = list(v)
    for i in range(4):
        if v[i] != 0:
            inv = 1 if v[i] == 1 else 2  # inverse in F3
            return tuple((inv * x) % 3 for x in v)
    raise ValueError("zero vector")


def construct_points():
    pts = []
    seen = set()
    for v in V:
        if v == V.zero():
            continue
        pv = proj_normalize(tuple(int(x) for x in v))
        if pv not in seen:
            seen.add(pv)
            pts.append(pv)
    if len(pts) != 40:
        raise RuntimeError(f"Expected 40 points, got {len(pts)}")
    return pts


def line_from_pair(points, i, j):
    vi, vj = points[i], points[j]
    if omega(vi, vj) != 0:
        raise ValueError("pair not orthogonal")
    combos = []
    for a in [0, 1, 2]:
        for b in [0, 1, 2]:
            if a == 0 and b == 0:
                continue
            w = tuple((a * vi[k] + b * vj[k]) % 3 for k in range(4))
            combos.append(proj_normalize(w))
    uniq = sorted(set(combos))
    if len(uniq) != 4:
        raise RuntimeError(f"Expected 4 points on a line, got {len(uniq)}")
    idx = {p: t for t, p in enumerate(points)}
    return tuple(sorted(idx[p] for p in uniq))


def construct_lines(points):
    lines = set()
    n = len(points)
    for i in range(n):
        for j in range(i + 1, n):
            if omega(points[i], points[j]) == 0:
                lines.add(line_from_pair(points, i, j))
    lines = sorted(lines)
    if len(lines) != 40:
        raise RuntimeError(f"Expected 40 lines, got {len(lines)}")
    if any(len(L) != 4 for L in lines):
        raise RuntimeError("Line size mismatch")
    return lines


def adjacency(points):
    n = len(points)
    A = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if omega(points[i], points[j]) == 0:
                A[i][j] = 1
                A[j][i] = 1
    return Matrix(ZZ, A)


def verify_srg(A):
    n = int(A.nrows())
    degs = [int(sum(A.row(i))) for i in range(n)]
    if len(set(degs)) != 1:
        raise RuntimeError(f"Non-regular degrees: {sorted(set(degs))}")
    k = degs[0]
    lam = set()
    mu = set()
    for i in range(n):
        for j in range(i + 1, n):
            c = int(A.row(i).dot_product(A.row(j)))
            if A[i, j] == 1:
                lam.add(int(c))
            else:
                mu.add(int(c))
    if len(lam) != 1 or len(mu) != 1:
        raise RuntimeError(f"SRG params not constant: λ={lam}, μ={mu}")
    return {"n": int(n), "k": int(k), "lambda": int(list(lam)[0]), "mu": int(list(mu)[0])}


def find_spreads(lines, n_points=40):
    # exact cover backtracking on 40 lines (size 4) to choose 10 disjoint lines covering all points
    n_points = int(n_points)
    line_masks = []
    point_to_lines = [[] for _ in range(n_points)]
    for idx, L in enumerate(lines):
        mask = int(0)
        for p in L:
            p = int(p)
            mask |= (int(1) << p)
            point_to_lines[p].append(idx)
        line_masks.append(mask)
    full_mask = (int(1) << n_points) - int(1)
    spreads = set()

    counts = [len(point_to_lines[i]) for i in range(n_points)]
    if len(set(counts)) != 1:
        raise RuntimeError(f"Point-line incidences not uniform: {sorted(set(counts))}")
    if counts[0] != 4:
        raise RuntimeError(f"Expected each point on 4 lines, got {counts[0]}")

    def backtrack(chosen, used_mask):
        if used_mask == full_mask:
            if len(chosen) != 10:
                raise RuntimeError("cover reached with wrong line count")
            spreads.add(tuple(sorted(chosen)))
            return
        # first uncovered point (simple scan; n_points=40 so this is fine)
        p = None
        for pp in range(n_points):
            if ((used_mask >> pp) & 1) == 0:
                p = pp
                break
        if p is None:
            raise RuntimeError("no uncovered point but mask not full")
        for li in point_to_lines[p]:
            m = line_masks[li]
            if used_mask & m:
                continue
            if len(chosen) >= 10:
                continue
            chosen.append(li)
            backtrack(chosen, used_mask | m)
            chosen.pop()

    backtrack([], int(0))
    return [list(s) for s in sorted(spreads)]


def pauli_2qutrit(v):
    # v=(b1,b2,a1,a2) -> (Z^a1 X^b1) ⊗ (Z^a2 X^b2)
    b1, b2, a1, a2 = [int(x) % 3 for x in v]
    K = CyclotomicField(3)
    w = K.gen()
    X = matrix(K, 3, 3, [[0, 0, 1], [1, 0, 0], [0, 1, 0]])
    Z = diagonal_matrix(K, [1, w, w^2])
    if Z * X != w * (X * Z):
        raise RuntimeError("ZX = ωXZ failed")

    def single(a, b):
        return (Z^a) * (X^b)

    return single(a1, b1).tensor_product(single(a2, b2))


def commutes(U, V):
    return (U * V) == (V * U)


def main():
    pts = construct_points()
    lines = construct_lines(pts)
    A = adjacency(pts)
    srg = verify_srg(A)

    # Exact commutation check on all pairs
    max_pairs = int(0)
    for i in range(40):
        Ui = pauli_2qutrit(pts[i])
        for j in range(i + 1, 40):
            Uj = pauli_2qutrit(pts[j])
            commute = commutes(Ui, Uj)
            ortho = omega(pts[i], pts[j]) == 0
            if commute != ortho:
                raise RuntimeError(f"Mismatch commute/orth at pair {(i, j)}")
            if ortho:
                max_pairs += 1

    spreads = find_spreads(lines, n_points=40)
    if len(spreads) != 36:
        raise RuntimeError(f"Expected 36 spreads, got {len(spreads)}")

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "ok",
        "srg": srg,
        "points": len(pts),
        "lines": len(lines),
        "spreads": len(spreads),
        "orthogonal_pairs": max_pairs,
        "sage_available": True,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=int(2), sort_keys=True), encoding="utf-8")

    OUT_MD.write_text(
        "\n".join(
            [
                "# Sage cross-check: W33 as 2-qutrit Pauli commutation geometry",
                "",
                f"- SRG: `{srg}`",
                f"- Points: `{len(pts)}`  Lines: `{len(lines)}`  Spreads: `{len(spreads)}`",
                f"- Verified exact matrix commutation ⇔ symplectic orthogonality on all point pairs.",
                "",
                f"Wrote `{OUT_JSON}`",
            ]
        ),
        encoding="utf-8",
    )

    print("OK")
    print(payload)


main()
