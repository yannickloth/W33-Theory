#!/usr/bin/env python3
"""Golay s12 -> Weyl-Heisenberg -> sl(27): a concrete algebraic closure.

This repo contains an s12 "grade-defined Jordan-Lie" toy model built from the
ternary Golay code (see `tools/s12_universal_algebra.py`).  That model captures
the 728 = 27^2 - 1 dimension count and the (242,243,243) Z3 grade split, but it
has a *finite Jacobi obstruction set* at the grade-coefficient level.

This script shows the standard resolution path:

  1) Identify the Golay code C as F3^6 (systematic generator => first 6 coords).
  2) Put a nondegenerate symplectic form on F3^6 (3-qutrit phase space).
  3) Build Weyl operators D(p,q) on (C^3)^{\otimes 3} and verify the commutation
     phase is exactly the symplectic pairing.
  4) Use the induced commutator bracket to recover a Jacobi-satisfying Lie
     algebra with basis size 3^6-1 = 728 (i.e., sl(27) in the usual Pauli basis).

The point is not that the symplectic form is uniquely determined here, but that
once a symplectic pairing is chosen, the Jacobi identity becomes automatic
(commutator in an associative algebra).

Run:
  & .venv\\Scripts\\python.exe -X utf8 scripts\\s12_sl27_heisenberg_algebra.py
"""

from __future__ import annotations

import random
import sys
from dataclasses import dataclass
from itertools import product
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tools.s12_universal_algebra as s12


def add_mod3(u: tuple[int, ...], v: tuple[int, ...]) -> tuple[int, ...]:
    return tuple((int(a) + int(b)) % 3 for a, b in zip(u, v))


def symplectic_3qutrit(u: tuple[int, ...], v: tuple[int, ...]) -> int:
    """Standard symplectic form on F3^6 interpreted as (p1,p2,p3,q1,q2,q3)."""
    p = u[:3]
    q = u[3:]
    p2 = v[:3]
    q2 = v[3:]
    total = 0
    for i in range(3):
        # With D(p,q)=X^p Z^q, the commutation phase satisfies:
        #   D(p,q) D(p',q') = omega^{ q·p' - p·q' } D(p',q') D(p,q).
        total += int(q[i]) * int(p2[i]) - int(p[i]) * int(q2[i])
    return int(total % 3)


def jacobi_coeff(u: tuple[int, ...], v: tuple[int, ...], w: tuple[int, ...]) -> int:
    """Coefficient on the (u+v+w) basis term for [ [u,v], w ] + cyclic."""
    uv = add_mod3(u, v)
    vw = add_mod3(v, w)
    wu = add_mod3(w, u)
    return int(
        (
            symplectic_3qutrit(u, v) * symplectic_3qutrit(uv, w)
            + symplectic_3qutrit(v, w) * symplectic_3qutrit(vw, u)
            + symplectic_3qutrit(w, u) * symplectic_3qutrit(wu, v)
        )
        % 3
    )


def _single_qutrit_XZ() -> tuple[np.ndarray, np.ndarray, complex]:
    omega = np.exp(2j * np.pi / 3)
    X = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]], dtype=complex)
    Z = np.array([[1, 0, 0], [0, omega, 0], [0, 0, omega**2]], dtype=complex)
    return X, Z, omega


def weyl_3qutrit(u: tuple[int, ...]) -> np.ndarray:
    """Weyl operator D(u) for u=(p1,p2,p3,q1,q2,q3)."""
    if len(u) != 6:
        raise ValueError("expected u in F3^6")
    X, Z, _ = _single_qutrit_XZ()
    p = u[:3]
    q = u[3:]
    mats = []
    for i in range(3):
        mats.append(
            np.linalg.matrix_power(X, int(p[i])) @ np.linalg.matrix_power(Z, int(q[i]))
        )
    return np.kron(np.kron(mats[0], mats[1]), mats[2])


@dataclass(frozen=True)
class GolayLabel:
    u: tuple[int, ...]  # F3^6 label (systematic coordinates)
    grade: int  # sum(codeword) mod 3


def _build_golay_labels() -> list[GolayLabel]:
    gen = s12.ternary_golay_generator_matrix()
    codewords = s12.enumerate_linear_code_f3(gen)
    zero = tuple([0] * len(gen[0]))
    labels: list[GolayLabel] = []
    for cw in codewords:
        if cw == zero:
            continue
        # Systematic generator: the first 6 coordinates are the combination coeffs.
        u = tuple(int(x) for x in cw[:6])
        grade = s12.grade_mod3(cw)
        labels.append(GolayLabel(u=u, grade=int(grade)))
    if len(labels) != 728:
        raise RuntimeError(f"expected 728 nonzero labels, got {len(labels)}")
    return labels


def main() -> None:
    labels = _build_golay_labels()
    by_grade = {0: 0, 1: 0, 2: 0}
    for lab in labels:
        by_grade[int(lab.grade)] += 1

    print("=" * 78)
    print("s12 -> Weyl-Heisenberg -> sl(27) (3-qutrit) closure")
    print("=" * 78)
    print("Golay nonzero basis size:", len(labels), "(expected 3^6-1 = 728)")
    print("Grade split (sum(codeword) mod 3):", by_grade, "(expected 242/243/243)")
    assert by_grade[0] == 242 and by_grade[1] == 243 and by_grade[2] == 243

    # Show the s12 grade-only omega has the known Jacobi obstruction set.
    laws = s12.verify_universal_grade_laws()
    print("s12 grade-only Jacobi holds?:", laws["jacobi_coefficient_identity_holds"])
    print("s12 grade-only Jacobi failure count:", laws["jacobi_failure_count"])
    assert laws["jacobi_failure_count"] == 6

    # Verify commutation phase for a few random pairs of Weyl operators.
    rng = random.Random(42)
    _, _, omega = _single_qutrit_XZ()
    print()
    print("Weyl commutation phase spot-checks (should match symplectic form):")
    for t in range(12):
        a, b = rng.sample(labels, 2)
        u = a.u
        v = b.u
        P = weyl_3qutrit(u)
        Q = weyl_3qutrit(v)
        PQ = P @ Q
        QP = Q @ P
        phase = None
        for k in (0, 1, 2):
            if np.allclose(PQ, (omega**k) * QP):
                phase = k
                break
        expected = symplectic_3qutrit(u, v)
        if phase is None:
            raise RuntimeError("failed to identify commutation phase (unexpected)")
        print(f"  {t:2d}: phase={phase} expected={expected}")
        assert int(phase) == int(expected)

    # Jacobi check for the bilinear symplectic coefficient bracket.
    #
    # For a Lie algebra with basis e_u (u in F3^6), bracket
    #   [e_u, e_v] = <u,v> e_{u+v}
    # has Jacobi coefficient sum exactly:
    #   <u,v><u+v,w> + <v,w><v+w,u> + <w,u><w+u,v>
    # which vanishes by bilinearity/alternation of <,>.
    #
    # We still sample to catch implementation errors.
    print()
    trials = 5000
    fails = 0
    for _ in range(trials):
        a, b, c = rng.sample(labels, 3)
        if jacobi_coeff(a.u, b.u, c.u) != 0:
            fails += 1
            break
    print(f"Jacobi sample failures: {fails} / {trials}")
    assert fails == 0

    print()
    print("OK: sl(27) Pauli-basis bracket is consistent (Jacobi via symplectic form).")


if __name__ == "__main__":
    main()
