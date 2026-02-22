#!/usr/bin/env python3
"""Compute cubic roots for the Vogel cubic polynomial for given target dims D.
This script prints numeric roots and attempts rational approximations up to denom cap.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
from math import isclose
from typing import List

import numpy as np


def cubic_coeffs(D: int):
    # From expansion in vogel_rational_cubic_search:
    # N(m) = (6m+14)*(5m+8)*(4m+8) - 4*D*(m+4)*(m+2)
    a = 120
    b = 712 - 4 * D
    c = 1392 - 24 * D
    d = 896 - 32 * D
    return [a, b, c, d]


def rational_approx(root: float, cap: int = 500, tol: float = 1e-12):
    # Find closest rational with denominator <= cap
    best = None
    for q in range(1, cap + 1):
        p = round(root * q)
        frac = Fraction(p, q)
        if abs(float(frac) - root) < tol:
            best = frac
            break
    return best


def roots_for_targets(targets: List[int]):
    results = {}
    for D in targets:
        coeffs = cubic_coeffs(D)
        poly = np.roots(coeffs)
        results[D] = {
            "coeffs": coeffs,
            "roots": [complex(x) for x in poly],
            "rational_approxs": [
                rational_approx(float(x.real)) if abs(x.imag) < 1e-12 else None
                for x in poly
            ],
        }
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", nargs="+", type=int, default=[728, 486, 242])
    parser.add_argument("--out-json", default=None)
    args = parser.parse_args()

    res = roots_for_targets(args.targets)
    for D, info in res.items():
        print(f"Target D={D}")
        print(" coeffs:", info["coeffs"])
        for idx, r in enumerate(info["roots"]):
            print(
                f"  root[{idx}] = {r} (rational approx={info['rational_approxs'][idx]})"
            )
        print("")


if __name__ == "__main__":
    main()
