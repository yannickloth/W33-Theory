#!/usr/bin/env python3
"""
Search for low‑weight codewords in the binary incidence code of the
generalised quadrangle W(3,3).

The W(3,3) configuration has 40 points and 40 lines.  Each line
is represented by a 4‑element subset of the 40 points, and the
binary incidence code is the span (over GF(2)) of the 40 incidence
vectors (one per line).  Many sources claim this code has
parameters [40,24,6], but our investigations suggest the dimension
is 25 and that codewords of weight 4 and 6 exist.

This script reproduces the W(3,3) incidence structure and performs
a targeted search for a weight‑6 codeword formed by the XOR of two
line incidence vectors.  It then reports the line indices and
point indices of such a codeword.

Usage:

    python3 w33_code_minweight_search.py

It prints the number of lines, then either reports a weight‑6
combination of two lines, or indicates that no such pair exists.
"""

from __future__ import annotations

import itertools
from typing import List, Tuple


def construct_projective_points() -> Tuple[List[Tuple[int, int, int, int]], dict]:
    """Return the 40 projective points in F3^4 and a mapping to indices."""
    F3 = [0, 1, 2]
    points: List[Tuple[int, int, int, int]] = []
    seen = set()
    # Generate non‑zero vectors up to scalar multiples
    for vec in itertools.product(F3, repeat=4):
        if not any(vec):
            continue
        v = list(vec)
        # Normalize the first non‑zero coordinate to 1
        for i in range(4):
            if v[i] != 0:
                inv = 1 if v[i] == 1 else 2  # 1^−1=1, 2^−1=2 in F3
                v = [(x * inv) % 3 for x in v]
                break
        t = tuple(v)
        if t not in seen:
            seen.add(t)
            points.append(t)
    index = {p: i for i, p in enumerate(points)}
    return points, index


def omega(x: Tuple[int, int, int, int], y: Tuple[int, int, int, int]) -> int:
    """Symplectic form on F3^4 used to define isotropic subspaces."""
    return (x[0] * y[2] - x[2] * y[0] + x[1] * y[3] - x[3] * y[1]) % 3


def compute_lines(
    points: List[Tuple[int, int, int, int]], index: dict
) -> List[Tuple[int, int, int, int]]:
    """Compute the 2‑dimensional isotropic subspaces (lines) of W(3,3).

    Each line is returned as a 4‑tuple of point indices.
    """
    F3 = [0, 1, 2]
    lines = set()
    n = len(points)
    for i in range(n):
        p = points[i]
        for j in range(i + 1, n):
            q = points[j]
            if omega(p, q) != 0:
                continue
            sub = set()
            # Generate the 2‑dimensional subspace spanned by p and q
            for a in F3:
                for b in F3:
                    if a == 0 and b == 0:
                        continue
                    vec = [(a * p[k] + b * q[k]) % 3 for k in range(4)]
                    # Normalize to projective representative
                    for t in range(4):
                        if vec[t] != 0:
                            inv = 1 if vec[t] == 1 else 2
                            vec = [(x * inv) % 3 for x in vec]
                            break
                    sub.add(tuple(vec))
            if len(sub) == 4:
                line_indices = tuple(sorted(index[v] for v in sub))
                lines.add(line_indices)
    return sorted(lines)


def find_weight6_pair(
    lines: List[Tuple[int, int, int, int]]
) -> Tuple[Tuple[int, int, int, int], Tuple[int, int, int, int], List[int]]:
    """Search for a pair of lines whose XOR incidence vector has Hamming weight 6.

    Returns a triple `(line1, line2, six_points)` if found, else raises
    `ValueError`.
    """
    # Convert lines to integer bitmasks
    bitmasks = [sum(1 << p for p in line) for line in lines]
    for i, bm1 in enumerate(bitmasks):
        for j in range(i + 1, len(bitmasks)):
            bm2 = bitmasks[j]
            xor = bm1 ^ bm2
            weight = xor.bit_count()
            # If lines intersect in one point then weight is 6
            if weight == 6 and xor != 0:
                six_points = [p for p in range(40) if (xor >> p) & 1]
                return lines[i], lines[j], six_points
    raise ValueError("No weight‑6 pair of lines found.")


def main() -> None:
    points, index = construct_projective_points()
    lines = compute_lines(points, index)
    print(f"Total number of lines: {len(lines)}")
    try:
        line1, line2, pts = find_weight6_pair(lines)
        print("Found a pair of lines whose XOR has weight 6:")
        print(f"  Line 1 (point indices): {line1}")
        print(f"  Line 2 (point indices): {line2}")
        print(f"  XOR weight‑6 points:      {pts}")
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    main()
