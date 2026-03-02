
"""
gf2lin.py - fast GF(2) linear algebra using Python int bitmasks.

Core idea:
- represent each row as a Python int whose binary expansion encodes columns.
- do Gaussian elimination via XOR.

This is designed for *wide* sparse-ish matrices (hundreds to a few thousand cols)
where Python's big-int XOR is extremely fast.

Main utilities:
- rank()
- rref()  (reduced row echelon form)
- solve(A, b)
- nullspace_basis(A)
- image_basis(A)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

def _bit(i: int) -> int:
    return 1 << i

@dataclass
class GF2Matrix:
    ncols: int
    rows: List[int]

    def copy(self) -> "GF2Matrix":
        return GF2Matrix(self.ncols, self.rows[:])

    @staticmethod
    def from_rows(ncols: int, rows: List[int]) -> "GF2Matrix":
        return GF2Matrix(ncols, rows[:])

    def rank(self) -> int:
        r, _, _ = echelon(self.rows, self.ncols)
        return r

    def rref(self) -> Tuple["GF2Matrix", List[int]]:
        rr, pivots = rref(self.rows, self.ncols)
        return GF2Matrix(self.ncols, rr), pivots

    def transpose_as_rows(self, nrows: int) -> "GF2Matrix":
        """
        Return transpose A^T as a GF2Matrix with nrows rows and self.ncols columns.
        This is O(nrows*ncols) and only intended for small-ish dense cases.
        For sparse boundary operators, prefer building the rows directly.
        """
        cols = [0]*self.ncols
        for r_idx, row in enumerate(self.rows):
            x=row
            while x:
                lsb = x & -x
                c = (lsb.bit_length()-1)
                cols[c] ^= _bit(r_idx)
                x ^= lsb
        return GF2Matrix(nrows, cols)

def echelon(rows: List[int], ncols: int) -> Tuple[int, Dict[int,int], List[int]]:
    """
    Row echelon (not reduced).
    Returns (rank, pivot_row_by_col, echelon_rows).
    pivot_row_by_col maps pivot column -> row index in the returned rows list.
    """
    rows = rows[:]  # copy
    pivot_row_by_col: Dict[int,int] = {}
    rank = 0
    for r in range(len(rows)):
        x = rows[r]
        # eliminate against existing pivots
        while x:
            c = x.bit_length() - 1  # highest 1 bit as pivot candidate
            pr = pivot_row_by_col.get(c)
            if pr is None:
                pivot_row_by_col[c] = r
                rows[r] = x
                rank += 1
                break
            x ^= rows[pr]
        else:
            rows[r] = 0
    return rank, pivot_row_by_col, rows

def rref(rows: List[int], ncols: int) -> Tuple[List[int], List[int]]:
    """
    Reduced row echelon form.
    Returns (rref_rows, pivots) with pivots listed in descending column order.
    """
    rank, pivot_row_by_col, rows_e = echelon(rows, ncols)
    pivots = sorted(pivot_row_by_col.keys(), reverse=True)

    # Back-substitute to clear pivot columns in other rows
    for c in pivots:
        r = pivot_row_by_col[c]
        pivot_row = rows_e[r]
        for rr in range(len(rows_e)):
            if rr == r:
                continue
            if (rows_e[rr] >> c) & 1:
                rows_e[rr] ^= pivot_row

    # Normalize: ensure each pivot row has pivot bit set (already true)
    # Optional: remove zero rows and sort by pivot position
    return rows_e, pivots

def solve(rows: List[int], ncols: int, b: List[int]) -> Tuple[Optional[int], List[int], List[int]]:
    """
    Solve A x = b over GF(2), where A is given by 'rows' (bitmasks over ncols),
    and b is a list of 0/1 with len(b)==len(rows).

    Returns:
      (particular_solution_mask or None if inconsistent,
       pivots,
       free_vars)

    The returned x is an int bitmask of length ncols.
    """
    if len(b) != len(rows):
        raise ValueError("len(b) must equal number of rows")

    aug = [ (rows[i] | (b[i] << ncols)) for i in range(len(rows)) ]
    ncols_aug = ncols + 1

    # echelon on augmented matrix
    rank, pivot_row_by_col, aug_e = echelon(aug, ncols_aug)
    pivots = sorted([c for c in pivot_row_by_col.keys() if c != ncols], reverse=True)

    # Check inconsistency: row with all-zero in A part but 1 in augmented bit
    for row in aug_e:
        if (row & ((1<<ncols)-1)) == 0 and ((row >> ncols) & 1):
            return None, pivots, []

    # Back substitute for particular solution (set free vars=0)
    x = 0
    # Build pivot rows in descending pivot column order
    pivot_items = sorted([(c, pivot_row_by_col[c]) for c in pivot_row_by_col.keys() if c != ncols], reverse=True)
    for c, r in pivot_items:
        row = aug_e[r]
        rhs = (row >> ncols) & 1
        # sum of known vars on this row excluding pivot
        mask = row & ((1<<ncols)-1)
        mask_without_pivot = mask & ~_bit(c)
        # parity of (mask_without_pivot & x)
        if (mask_without_pivot & x).bit_count() & 1:
            rhs ^= 1
        if rhs:
            x |= _bit(c)
        else:
            x &= ~_bit(c)

    free_vars = [c for c in range(ncols) if c not in set(pivots)]
    return x, pivots, free_vars

def nullspace_basis(rows: List[int], ncols: int) -> List[int]:
    """
    Return a basis for ker(A) as list of bitmasks (each length ncols).
    """
    rr, pivots = rref(rows, ncols)
    pivot_set = set(pivots)
    free = [c for c in range(ncols) if c not in pivot_set]
    # Map pivot col -> row
    pivot_row = {}
    for r, row in enumerate(rr):
        if row==0:
            continue
        c = row.bit_length()-1
        if c in pivot_set:
            pivot_row[c]=row

    basis=[]
    for f in free:
        x = _bit(f)
        # For each pivot col, set pivot variable so that row equation holds
        for c in pivots:
            row = pivot_row[c]
            # row corresponds to x_c + sum_{j in free} a_j x_j = 0
            if ((row >> f) & 1):
                x |= _bit(c)
        basis.append(x)
    return basis

def image_basis(rows: List[int], ncols: int) -> List[int]:
    """
    Return a basis for the row space (image of A^T) as echelon nonzero rows.
    """
    _, _, eche = echelon(rows, ncols)
    return [r for r in eche if r != 0]
