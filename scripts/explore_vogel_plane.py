#!/usr/bin/env python3
"""Scan a portion of the Vogel plane and classify triples.

This utility is meant to help answer the question "why does Vogel's
universal formula work?" by generating many rational triples and seeing
which polynomial loci they satisfy.  We also look for small integer
adjoint dimensions and record which of the SL/OSP/exceptional/refined
polynomials vanish.

The output can be dumped as JSON or printed; it is easy to feed the
results into a notebook for visualization.

Usage examples:
    python scripts/explore_vogel_plane.py --max-num 5 --max-den 5 --dim-bound 500
    python scripts/explore_vogel_plane.py --alpha -2 --max-num 50 --max-den 10
"""
from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path
import sys

# reuse functions from previous modules
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.vogel_universal_snapshot import vogel_dimension
from scripts.w33_vogel_universality import (
    P_sl,
    P_osp,
    P_exc,
    P_Lie,
    P_G2,
    P_F4,
    P_E6,
    P_E7,
    P_E8,
    P_Lie_refined,
    vogel_t_sigma_omega,
    vogel_chi_x1,
)


def canonicalize_triple(a: Fraction, b: Fraction, c: Fraction) -> tuple[int,int,int]:
    """Return primitive integer tuple up to scale/permutation."""
    den = a.denominator * b.denominator * c.denominator
    A = int(a * den); B = int(b * den); C = int(c * den)
    g = math.gcd(math.gcd(abs(A), abs(B)), abs(C))
    if g:
        A //= g; B //= g; C //= g
    vals = sorted([A, B, C], key=lambda x:(abs(x), x))
    return tuple(vals)


def classify(a: Fraction, b: Fraction, c: Fraction) -> dict[str, object]:
    d = vogel_dimension(a, b, c)
    t, sigma, omega = vogel_t_sigma_omega(a, b, c)
    chi1 = vogel_chi_x1(t)
    info = {
        "alpha": str(a),
        "beta": str(b),
        "gamma": str(c),
        "dim": float(d) if d.denominator != 1 else int(d),
        "t": str(t),
        "sigma": str(sigma),
        "omega": str(omega),
        "chi_x1": str(chi1),
    }
    # record vanishing of various polynomials
    info.update({
        "P_sl": bool(P_sl(a, b, c) == 0),
        "P_osp": bool(P_osp(a, b, c) == 0),
        "P_exc": bool(P_exc(a, b, c) == 0),
        "P_Lie": bool(P_Lie(a, b, c) == 0),
        "P_Lie_refined": bool(P_Lie_refined(a, b, c) == 0),
    })
    # if on SL locus and dimension integer, attempt to identify sl_{n+1}
    if info["P_sl"] and isinstance(info["dim"], int):
        # solve n(n+2)=dim for integer n
        dim_val = info["dim"]
        # quadratic n^2+2n-dim=0 -> n = -1 + sqrt(1+dim)
        import math
        disc = 1 + dim_val
        if int(math.isqrt(disc))**2 == disc:
            n = int(math.isqrt(disc)) - 1
            if n >= 1 and n*(n+2) == dim_val:
                info['classical'] = f'sl_{n+1}'
    # exceptional factors
    for name, fn in [("G2", P_G2), ("F4", P_F4), ("E6", P_E6), ("E7", P_E7), ("E8", P_E8)]:
        info[f"P_{name}"] = bool(fn(a, b, c) == 0)
    return info


def scan(max_num: int, max_den: int, dim_bound: int, fix_alpha: Fraction | None):
    seen = set()
    results = []
    alphas = [fix_alpha] if fix_alpha is not None else []
    if fix_alpha is None:
        for an in range(-max_num, max_num + 1):
            for ad in range(1, max_den + 1):
                alphas.append(Fraction(an, ad))
    for a in alphas:
        for bn in range(-max_num, max_num + 1):
            for bd in range(1, max_den + 1):
                b = Fraction(bn, bd)
                for gn in range(-max_num, max_num + 1):
                    for gd in range(1, max_den + 1):
                        c = Fraction(gn, gd)
                        try:
                            d = vogel_dimension(a, b, c)
                        except ZeroDivisionError:
                            continue
                        if d <= 0:
                            continue
                        if d > dim_bound:
                            continue
                        key = canonicalize_triple(a, b, c)
                        if key in seen:
                            continue
                        seen.add(key)
                        results.append(classify(a, b, c))
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-num", type=int, default=5)
    parser.add_argument("--max-den", type=int, default=5)
    parser.add_argument("--dim-bound", type=int, default=500)
    parser.add_argument("--alpha", type=Fraction, default=None,
                        help="fix alpha value")
    parser.add_argument("--out-json", type=Path, default=None)
    args = parser.parse_args()

    res = scan(args.max_num, args.max_den, args.dim_bound, args.alpha)
    if args.out_json:
        args.out_json.write_text(json.dumps(res, indent=2), encoding="utf-8")
        print(f"wrote {len(res)} triples to {args.out_json}")
    else:
        for r in res:
            print(r)

if __name__ == "__main__":
    main()
