#!/usr/bin/env python3
"""Efficient rational search for Vogel exceptional-line cubic condition.

Find rational m such that vogel_dim(alpha=-2, beta=m+4, gamma=2m+4) equals target D.
This reduces to a cubic polynomial N(m)=0; rational roots p/q satisfy p|d and q|a.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from math import isqrt
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]


def _divisors(n: int) -> List[int]:
    n = abs(n)
    if n == 0:
        return [0]
    divs = set()
    for i in range(1, isqrt(n) + 1):
        if n % i == 0:
            divs.add(i)
            divs.add(n // i)
    res = sorted(divs)
    return res


def find_rational_m_for_dim(D: int, denom_cap: int = 200) -> Dict[str, List[str]]:
    """Return list of rational m (as "p/q") solving the cubic for target dim D."""
    # Build polynomial N(m) = (6m+14)*(5m+8)*(4m+8) - 4*D*(m+4)*(m+2)
    # Expand to integer coefficients a*m^3 + b*m^2 + c*m + d
    # We'll compute coefficients by expansion
    # Expand (6m+14)*(5m+8)*(4m+8)
    # = (6m+14)*((5m+8)*(4m+8))
    # Compute stepwise
    # Use integer arithmetic
    # Coeffs of (6m+14)*(5m+8)*(4m+8)
    # Multiply out directly
    # Let’s symbolically expand
    a = 6 * 5 * 4  # coefficient for m^3 from product = 120
    # Compute full expansion
    # (6m+14)*(5m+8)*(4m+8) -> expand
    # Use simple algebra
    # Expand using Python integer arithmetic
    # Compute polynomial coefficients for first term
    # First product (5m+8)*(4m+8) = 20 m^2 + (40+32)m + 64 = 20m^2 + 72m + 64
    # Then multiply by (6m+14):
    # (6m)*(20m^2 + 72m + 64) = 120 m^3 + 432 m^2 + 384 m
    # (14)*(20m^2 + 72m + 64) = 280 m^2 + 1008 m + 896
    # Sum: 120 m^3 + (432+280)=712 m^2 + (384+1008)=1392 m + 896
    a = 120
    b = 712
    c = 1392
    d = 896

    # subtract 4*D*(m+4)*(m+2) = 4D*(m^2 + 6m + 8)
    # so subtract 4D*m^2 + 24D*m + 32D
    b -= 4 * D
    c -= 24 * D
    d -= 32 * D

    # Now we have integer polynomial coefficients a,b,c,d
    # Use rational root theorem: possible rational roots p/q with p|d and q|a
    possible_ps = _divisors(d) if d != 0 else [0]
    possible_qs = _divisors(a)

    hits: List[Fraction] = []
    for p in possible_ps:
        for q in possible_qs:
            for sign in (1, -1):
                num = sign * p
                den = q
                if den == 0:
                    continue
                frac = Fraction(num, den)
                # Check denom cap
                if abs(frac.denominator) > denom_cap:
                    continue
                m = frac
                # Evaluate polynomial at m
                # Using integer arithmetic with Fractions
                val = a * m**3 + b * m**2 + c * m + d
                if val == 0:
                    hits.append(m)
    # Deduplicate and sort
    hits = sorted(set(hits))
    # exclude degenerate params that zero out Vogel denominator (m=-2 or m=-4) as they
    # make beta or gamma zero and lead to division-by-zero in the original formula
    filtered = [h for h in hits if h != Fraction(-2, 1) and h != Fraction(-4, 1)]
    return {
        "target_dim": D,
        "denom_cap": denom_cap,
        "hits": [
            f"{h.numerator}/{h.denominator}" if h.denominator != 1 else str(h.numerator)
            for h in filtered
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-dims", nargs="+", type=int, default=[728, 486, 242])
    parser.add_argument("--denom-cap", type=int, default=200)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "vogel_rational_search.json",
    )
    args = parser.parse_args()

    results = {
        str(D): find_rational_m_for_dim(D, denom_cap=int(args.denom_cap))
        for D in args.target_dims
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {args.out_json}")
