"""Utilities for computing cross ratios and exploring Möbius transformations.

This module provides basic operations over real numbers, SymPy objects, or
finite fields (using SymPy's GF domain).  It is intended to support the
notebook exploration of projective invariants and may later be extended to work
on coordinates coming from W(3,3) geometry or Yukawa tensors.
"""

from __future__ import annotations

import random
from typing import Any, Sequence, Tuple, Union

import sympy as sp

# numeric types accepted: float, complex, sympy.Expr, integers

Number = Union[int, float, complex, sp.Expr]


def cross_ratio(a: Number, b: Number, c: Number, d: Number, *, field: int | None = None) -> Number:
    """Return the cross ratio (A,B;C,D) of four points.

    If ``field`` is provided, arithmetic is carried out in the Galois field
    GF(field) using SymPy's modular arithmetic.  ``field`` must be prime.
    Otherwise, plain Python / SymPy arithmetic is used.
    """
    if field is not None:
        # convert inputs to integers mod p
        p = field
        if not sp.isprime(p):
            raise ValueError("field must be a prime number")
        # ensure all inputs are integers
        vals = [int(v) % p for v in (a, b, c, d)]
        a_, b_, c_, d_ = vals
        num = (a_ - c_) * (b_ - d_) % p
        den = (a_ - d_) * (b_ - c_) % p
        if den == 0:
            raise ZeroDivisionError("cross ratio denominator zero modulo %d" % p)
        inv_den = sp.mod_inverse(den, p)
        return (num * inv_den) % p
    else:
        # use SymPy to handle symbolic expressions gracefully
        return (a - c) * (b - d) / ((a - d) * (b - c))


def mobius_transform(z: Number, a: Number, b: Number, c: Number, d: Number, *, field: int | None = None) -> Number:
    r"""Apply the Möbius transformation $z\mapsto\frac{az+b}{cz+d}$.

    By default this just does normal arithmetic. If ``field`` is provided, the
    computation is carried out in GF(field) similarly to :func:`cross_ratio`.
    This means inputs are reduced mod ``field`` and division uses the modular
    inverse; a ZeroDivisionError is raised if ``cz+d\equiv0\pmod{field}``.
    """
    if field is not None:
        p = field
        if not sp.isprime(p):
            raise ValueError("field must be a prime number")
        z_mod = int(z) % p
        a_, b_, c_, d_ = [int(v) % p for v in (a, b, c, d)]
        num = (a_ * z_mod + b_) % p
        den = (c_ * z_mod + d_) % p
        if den == 0:
            raise ZeroDivisionError("mobius denominator zero modulo %d" % p)
        inv = sp.mod_inverse(den, p)
        return (num * inv) % p
    else:
        return (a * z + b) / (c * z + d)


def random_mobius(field: int | None = None) -> Tuple[Any, Any, Any, Any]:
    """Return random coefficients (a,b,c,d) for an invertible Mobius map.

    If ``field`` is given, coefficients are drawn uniformly from integers mod
    ``field`` with the condition that ad-bc is nonzero modulo ``field``.
    Otherwise, random floats in [-1,1] are chosen until the determinant is
    nonzero.
    """
    if field is not None:
        p = field
        if not sp.isprime(p):
            raise ValueError("field must be prime")
        while True:
            a, b, c, d = [random.randrange(p) for _ in range(4)]
            if (a * d - b * c) % p != 0:
                return a, b, c, d
    else:
        while True:
            a, b, c, d = [random.uniform(-1, 1) for _ in range(4)]
            if abs(a * d - b * c) > 1e-8:
                return a, b, c, d


def apply_mobius_to_list(points: Sequence[Number], a: Number, b: Number, c: Number, d: Number, *, field: int | None = None) -> list[Number]:
    """Apply a Möbius transformation to a list of points.

    ``field`` is forwarded to :func:`mobius_transform` if provided.
    """
    return [mobius_transform(z, a, b, c, d, field=field) for z in points]


if __name__ == "__main__":
    # simple demonstration
    import argparse

    parser = argparse.ArgumentParser(description="Cross ratio demo")
    parser.add_argument("--field", type=int, help="prime field for arithmetic")
    args = parser.parse_args()
    if args.field:
        print("Cross ratio in GF(%d):" % args.field, cross_ratio(1, 2, 3, 4, field=args.field))
    else:
        print("Cross ratio (1,2;3,4) =", cross_ratio(1, 2, 3, 4))
