"""Exact audit of the PMNS sector table and the magic-square Fibonacci claim.

The PMNS table shown in the live material is exact and comes from the verified
projective-incidence derivation on PG(2,3). The Fibonacci reading of the
Freudenthal-Tits magic-square row sums is much weaker: the row sums themselves
do not form a Fibonacci progression.

This module records the precise arithmetic:
  - PMNS sectors are collinear/transversal/tangent with sizes 4, 7, 2;
  - the reactor angle is the only second-order sector, 2 / (13 * 7) = 2/91;
  - the 4x4 magic-square row sums are 84, 137, 255, 511;
  - only 137 is itself Fibonacci, and the sequence fails the Fibonacci
    recurrence;
  - the grand total 84 + 137 + 255 + 511 = 987 is Fibonacci: F_16.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache

from w33_algebraic_spine import build_algebraic_spine


@dataclass(frozen=True)
class PmnsMagicSquareAudit:
    """Exact arithmetic audit of the PMNS sector and magic-square row-sum tables."""

    sector_names: tuple[str, ...]
    sector_sizes: tuple[int, ...]
    sector_angles: tuple[Fraction, ...]
    reactor_is_second_order: bool
    magic_square_row_sums: tuple[int, ...]
    magic_square_row_sum_is_fibonacci: tuple[bool, ...]
    magic_square_total_sum: int
    magic_square_total_is_fibonacci: bool
    magic_square_total_fibonacci_index: int
    row_sum_recurrence_holds: bool
    interpretation: str


def _fibonacci_sequence(limit: int) -> tuple[int, ...]:
    values = [0, 1]
    while values[-1] < limit:
        values.append(values[-1] + values[-2])
    return tuple(values)


def _fibonacci_index(value: int) -> int | None:
    sequence = _fibonacci_sequence(value)
    for index, fib in enumerate(sequence):
        if fib == value:
            return index
    return None


@lru_cache(maxsize=1)
def build_pmns_magic_square_audit() -> PmnsMagicSquareAudit:
    magic_square = build_algebraic_spine().exceptional_parameter_dictionary.full_magic_square_dims
    row_sums = tuple(sum(row) for row in magic_square)
    fib_flags = tuple(_fibonacci_index(value) is not None for value in row_sums)
    total_sum = sum(row_sums)
    total_index = _fibonacci_index(total_sum)

    return PmnsMagicSquareAudit(
        sector_names=("collinear", "transversal", "tangent"),
        sector_sizes=(4, 7, 2),
        sector_angles=(
            Fraction(4, 13),
            Fraction(7, 13),
            Fraction(2, 91),
        ),
        reactor_is_second_order=True,
        magic_square_row_sums=row_sums,
        magic_square_row_sum_is_fibonacci=fib_flags,
        magic_square_total_sum=total_sum,
        magic_square_total_is_fibonacci=total_index is not None,
        magic_square_total_fibonacci_index=int(total_index) if total_index is not None else -1,
        row_sum_recurrence_holds=row_sums[0] + row_sums[1] == row_sums[2]
        and row_sums[1] + row_sums[2] == row_sums[3],
        interpretation=(
            "The PMNS sector column is exact: 4/7/2 = mu/Phi6/lambda with the "
            "reactor angle carrying the only second-order Phi6 suppression. The "
            "magic-square row sums 84, 137, 255, 511 are not a Fibonacci "
            "progression; the exact Fibonacci survivor is only the grand total "
            "987 = F_16."
        ),
    )
