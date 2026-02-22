#!/usr/bin/env python3
"""
Deterministic ±1 cocycle on the E8 root lattice (for Chevalley-sign experiments).

This implements a standard "lattice cocycle" construction used e.g. in
even-lattice vertex-operator-algebra setups:

  - Choose an ordered Z-basis (b1,...,b8) for the E8 lattice.
  - Define a bimultiplicative map ε: L×L -> {±1} by
        ε(bi,bj) = (-1)^{(bi,bj)}  if i>j
                 = +1             if i<=j
    and extend multiplicatively to all α=Σ ai bi, β=Σ bj bj:
        ε(α,β) = (-1)^{ Σ_{i>j} ai*bj*(bi,bj) }.

For simply-laced roots, when α+β is a root we have (α,β)=-1, hence
ε(β,α) = -ε(α,β), giving the antisymmetry needed for a bracket
  [e_α,e_β] = ε(α,β) e_{α+β}
on root spaces (Cartan terms ignored here).

Important:
  - This is a *choice* of cocycle; it is not claimed to be the unique
    Chevalley basis sign convention.
  - It is deterministic and compatible with the E8 lattice arithmetic used
    throughout this repo (roots have coordinates in (1/2)Z).
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from typing import Iterable, List, Sequence, Tuple

IntVec = Tuple[int, ...]  # length 8; doubled coordinates (2*root) in Z^8


def _e8_simple_root_basis_doubled_columns() -> List[IntVec]:
    """
    Return a Z-basis for the E8 root lattice: the Bourbaki simple roots, doubled.

    In this repo's coordinate convention (used by `tools/compute_double_sixes.py`),
    the simple roots are:
      a1 = ( 1,-1, 0, 0, 0, 0, 0, 0)
      a2 = ( 0, 1,-1, 0, 0, 0, 0, 0)
      a3 = ( 0, 0, 1,-1, 0, 0, 0, 0)
      a4 = ( 0, 0, 0, 1,-1, 0, 0, 0)
      a5 = ( 0, 0, 0, 0, 1,-1, 0, 0)
      a6 = ( 0, 0, 0, 0, 0, 1,-1, 0)
      a7 = ( 0, 0, 0, 0, 0, 1, 1, 0)
      a8 = (-1/2,...,-1/2)

    We work in doubled coordinates (multiply by 2) so all basis vectors are integral.
    """

    return [
        (2, -2, 0, 0, 0, 0, 0, 0),  # 2*a1
        (0, 2, -2, 0, 0, 0, 0, 0),  # 2*a2
        (0, 0, 2, -2, 0, 0, 0, 0),  # 2*a3
        (0, 0, 0, 2, -2, 0, 0, 0),  # 2*a4
        (0, 0, 0, 0, 2, -2, 0, 0),  # 2*a5
        (0, 0, 0, 0, 0, 2, -2, 0),  # 2*a6
        (0, 0, 0, 0, 0, 2, 2, 0),  # 2*a7
        (-1, -1, -1, -1, -1, -1, -1, -1),  # 2*a8
    ]


def _dot_int(u: IntVec, v: IntVec) -> int:
    return sum(int(a) * int(b) for a, b in zip(u, v, strict=True))


@dataclass(frozen=True)
class E8Cocycle:
    basis_cols_doubled: Tuple[IntVec, ...]
    gram_basis: Tuple[Tuple[int, ...], ...]  # (bi,bj) in undoubled inner product

    @staticmethod
    def standard() -> "E8Cocycle":
        cols = tuple(_e8_simple_root_basis_doubled_columns())
        # (bi,bj) = <2bi,2bj>/4 in undoubled coordinates
        gram: List[List[int]] = [[0] * 8 for _ in range(8)]
        for i in range(8):
            for j in range(8):
                d = _dot_int(cols[i], cols[j])
                if d % 4 != 0:
                    raise ValueError(
                        "Basis dot product not divisible by 4 (unexpected)"
                    )
                gram[i][j] = d // 4
        return E8Cocycle(
            basis_cols_doubled=cols, gram_basis=tuple(tuple(r) for r in gram)
        )

    def coeffs_in_basis(self, v_doubled: IntVec) -> Tuple[int, ...]:
        """
        Solve for integer coefficients a with Σ a_i * (2*b_i) = v_doubled.
        """

        return _solve_int_coeffs_in_basis(self.basis_cols_doubled, v_doubled)

    def epsilon(self, alpha_doubled: IntVec, beta_doubled: IntVec) -> int:
        """
        ε(alpha,beta) in {+1,-1} for lattice vectors given in doubled coordinates.
        """

        a = self.coeffs_in_basis(alpha_doubled)
        b = self.coeffs_in_basis(beta_doubled)
        parity = 0
        for i in range(8):
            ai = a[i] & 1
            if ai == 0:
                continue
            for j in range(i):
                bj = b[j] & 1
                if bj == 0:
                    continue
                gij = self.gram_basis[i][j] & 1
                parity ^= ai & bj & gij
        return -1 if parity else 1


def _solve_int_coeffs_in_basis(
    basis_cols_doubled: Sequence[IntVec], v_doubled: IntVec
) -> Tuple[int, ...]:
    """
    Exact integer solve using Fraction Gaussian elimination.
    """

    if len(basis_cols_doubled) != 8:
        raise ValueError("Expected 8 basis vectors")
    if len(v_doubled) != 8:
        raise ValueError("Expected length-8 vector")

    # Build augmented matrix for B a = v, with B columns given.
    # Work row-wise in Fractions.
    B = [
        [Fraction(int(basis_cols_doubled[col][row])) for col in range(8)]
        for row in range(8)
    ]
    aug = [B[row] + [Fraction(int(v_doubled[row]))] for row in range(8)]

    # Gaussian elimination
    pivot_col_for_row = [-1] * 8
    row = 0
    for col in range(8):
        # Find pivot row
        pivot = None
        for r in range(row, 8):
            if aug[r][col] != 0:
                pivot = r
                break
        if pivot is None:
            continue
        aug[row], aug[pivot] = aug[pivot], aug[row]
        pivot_val = aug[row][col]
        aug[row] = [x / pivot_val for x in aug[row]]
        pivot_col_for_row[row] = col
        # Eliminate
        for r in range(8):
            if r == row:
                continue
            factor = aug[r][col]
            if factor == 0:
                continue
            aug[r] = [aug[r][c] - factor * aug[row][c] for c in range(9)]
        row += 1
        if row == 8:
            break

    # Extract solution a, checking exactness.
    a = [Fraction(0) for _ in range(8)]
    for r in range(8):
        col = pivot_col_for_row[r]
        if col == -1:
            # All-zero row: must also have 0 rhs.
            if aug[r][8] != 0:
                raise ValueError(
                    "Vector is not in the span of the basis (inconsistent)"
                )
            continue
        a[col] = aug[r][8]

    out: List[int] = []
    for x in a:
        if x.denominator != 1:
            raise ValueError(
                "Non-integer coefficient encountered (unexpected for E8 roots)"
            )
        out.append(int(x.numerator))
    return tuple(out)


@lru_cache(maxsize=None)
def epsilon_e8(alpha_doubled: IntVec, beta_doubled: IntVec) -> int:
    """
    Convenience wrapper: ε(alpha,beta) for the standard cocycle.
    """

    return E8Cocycle.standard().epsilon(alpha_doubled, beta_doubled)


def sign_to_bit(s: int) -> int:
    if s not in (-1, 1):
        raise ValueError("Expected sign ±1")
    return 1 if s == -1 else 0


def bit_to_sign(b: int) -> int:
    if b not in (0, 1):
        raise ValueError("Expected bit 0/1")
    return -1 if b else 1
