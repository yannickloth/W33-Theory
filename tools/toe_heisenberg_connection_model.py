#!/usr/bin/env python3
"""
TOE: Identify the firewall AG(2,3)+Z3 connection with the qutrit Heisenberg/Weyl structure.

Motivation:
  The derived Z3 holonomy law on the affine plane (F3^2):
      hol(d1,d2) = -det(d1,d2)  (mod 3)
  is exactly the symplectic form on discrete phase space.

In quantum information, the qutrit Weyl operators satisfy:
  Z X = ω X Z,  ω = exp(2π i / 3),
and the Heisenberg displacement operators have commutators controlled by det.

This script builds the qutrit Weyl operators and verifies that the model's Z3 curvature
matches the Heisenberg commutator phase.

Inputs:
  - artifacts/toe_affine_plane_z3_holonomy.json

Outputs:
  - artifacts/toe_heisenberg_connection_model.json
  - artifacts/toe_heisenberg_connection_model.md
"""

from __future__ import annotations

import cmath
import json
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def _write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _mod3(x: int) -> int:
    return int(x) % 3


def _det(d1: Tuple[int, int], d2: Tuple[int, int]) -> int:
    return _mod3(d1[0] * d2[1] - d1[1] * d2[0])


def _matmul(A: List[List[complex]], B: List[List[complex]]) -> List[List[complex]]:
    n = len(A)
    return [
        [sum(A[i][k] * B[k][j] for k in range(n)) for j in range(n)] for i in range(n)
    ]


def _mateq(A: List[List[complex]], B: List[List[complex]], tol: float = 1e-9) -> bool:
    for i in range(len(A)):
        for j in range(len(A)):
            if abs(A[i][j] - B[i][j]) > tol:
                return False
    return True


def _mat_scalar(A: List[List[complex]], s: complex) -> List[List[complex]]:
    return [[s * x for x in row] for row in A]


def _mat_pow(A: List[List[complex]], k: int) -> List[List[complex]]:
    n = len(A)
    # identity
    I = [[(1.0 + 0.0j) if i == j else (0.0 + 0.0j) for j in range(n)] for i in range(n)]
    if k % 3 == 0:
        return I
    if k % 3 == 1:
        return A
    return _matmul(A, A)


def main() -> None:
    hol_path = ROOT / "artifacts" / "toe_affine_plane_z3_holonomy.json"
    hol = _load_json(hol_path)
    if hol.get("status") != "ok":
        raise RuntimeError("toe_affine_plane_z3_holonomy.json status != ok")
    if hol.get("constant_curvature_minus_det") is not True:
        raise RuntimeError("Expected constant_curvature_minus_det == True")

    omega = cmath.exp(2j * cmath.pi / 3.0)
    # Qutrit Weyl operators
    X = [
        # X|j> = |j+1> (cyclic forward shift)
        [0.0 + 0.0j, 0.0 + 0.0j, 1.0 + 0.0j],
        [1.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
        [0.0 + 0.0j, 1.0 + 0.0j, 0.0 + 0.0j],
    ]
    Z = [
        [1.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
        [0.0 + 0.0j, omega, 0.0 + 0.0j],
        [0.0 + 0.0j, 0.0 + 0.0j, omega**2],
    ]

    # Verify Weyl commutation: Z X = ω X Z
    ZX = _matmul(Z, X)
    XZ = _matmul(X, Z)
    ok_zx = _mateq(ZX, _mat_scalar(XZ, omega))

    # Define displacement operators D(p,q) = X^p Z^q (one common convention).
    #
    # With Z X = ω X Z we get:
    #   (X^p Z^q)(X^r Z^s) = ω^{q r} X^{p+r} Z^{q+s}
    # so the commutator phase is ω^{q r - s p} = ω^{-det((p,q),(r,s))}.
    def D(p: int, q: int) -> List[List[complex]]:
        p = _mod3(p)
        q = _mod3(q)
        return _matmul(_mat_pow(X, p), _mat_pow(Z, q))

    # Check commutator phase: D(a)D(b) = ω^{-det(a,b)} D(b)D(a)
    # (sign convention matches the holonomy output).
    comm_ok = True
    comm_table: Dict[str, int] = {}
    vecs = [(1, 0), (0, 1), (1, 1), (1, 2)]
    for a in vecs:
        for b in vecs:
            if a == b:
                continue
            det = _det(a, b)
            lhs = _matmul(D(*a), D(*b))
            rhs = _matmul(D(*b), D(*a))
            expect = omega ** _mod3(-det)
            if not _mateq(lhs, _mat_scalar(rhs, expect)):
                comm_ok = False
            comm_table[f"{a}->{b}"] = _mod3(-det)

    out = {
        "status": "ok",
        "sources": {"toe_affine_plane_z3_holonomy": str(hol_path)},
        "omega": {"re": omega.real, "im": omega.imag},
        "weyl": {
            "ZX_equals_omega_XZ": bool(ok_zx),
            "commutator_matches_minus_det": bool(comm_ok),
            "commutator_exponent_table_mod3": comm_table,
        },
        "note": (
            "The affine-plane Z3 connection has curvature hol=-det, matching the "
            "symplectic form controlling qutrit Heisenberg/Weyl commutators."
        ),
    }

    out_json = ROOT / "artifacts" / "toe_heisenberg_connection_model.json"
    out_md = ROOT / "artifacts" / "toe_heisenberg_connection_model.md"
    _write_json(out_json, out)

    md = []
    md.append("# TOE Heisenberg connection model (qutrit)")
    md.append("")
    md.append("## Checks")
    md.append(f"- ZX = ωXZ: {out['weyl']['ZX_equals_omega_XZ']}")
    md.append(
        f"- commutator exponent = -det mod 3: {out['weyl']['commutator_matches_minus_det']}"
    )
    md.append("")
    md.append("## Sample commutator exponents")
    for k, v in sorted(comm_table.items()):
        md.append(f"- {k}: {v}")
    _write_md(out_md, "\n".join(md) + "\n")

    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
