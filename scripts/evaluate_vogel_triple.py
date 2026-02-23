#!/usr/bin/env python3
"""Evaluate Vogel invariants for a given rational triple.

This is a convenience tool to plug in one of the rational solutions produced by
`vogel_param_search.py` and inspect the resulting universal adjoint dimension,
polynomial loci and Casimir characters.  Useful when "cracking the algebra"
search yields a candidate triple.

Usage examples:
    python scripts/evaluate_vogel_triple.py -a -2 -b 5 -g 35
    python scripts/evaluate_vogel_triple.py --alpha -2 --beta -27 --gamma 2
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import sys

# import the helper functions from the Vogel universality script
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))
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
    omega_factor,
    vogel_t_sigma_omega,
    vogel_chi_x1,
    vogel_chi_x3,
    vogel_chi_x5,
)
from tools.vogel_universal_snapshot import vogel_dimension


def rational(value: str) -> Fraction:
    try:
        return Fraction(value)
    except Exception:
        raise argparse.ArgumentTypeError(f"invalid rational: {value}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Vogel invariants.")
    parser.add_argument("-a", "--alpha", type=rational, required=True)
    parser.add_argument("-b", "--beta", type=rational, required=True)
    parser.add_argument("-g", "--gamma", type=rational, required=True)
    args = parser.parse_args()

    a, b, c = args.alpha, args.beta, args.gamma
    t = a + b + c
    print(f"Vogel triple (alpha,beta,gamma) = ({a}, {b}, {c})")
    try:
        dim = vogel_dimension(a, b, c)
    except ZeroDivisionError:
        print("  degenerate: denominator zero in dimension formula")
        return
    print(f"  adjoint dimension = {dim}")
    print("  basic polynomials:")
    print(f"    P_sl = {P_sl(a,b,c)}")
    print(f"    P_osp = {P_osp(a,b,c)}")
    print(f"    P_exc = {P_exc(a,b,c)}")
    print(f"    P_Lie = {P_Lie(a,b,c)}")
    print("  refined loci (exceptional factors):")
    for name, P_fn in [("G2", P_G2), ("F4", P_F4), ("E6", P_E6), ("E7", P_E7), ("E8", P_E8)]:
        print(f"    P_{name} = {P_fn(a,b,c)}")
    print(f"    P_Lie_refined = {P_Lie_refined(a,b,c)}")
    print(f"  omega factor = {omega_factor(a,b,c)}")
    t, sigma, omega = vogel_t_sigma_omega(a,b,c)
    print(f"  invariants t={t}, sigma={sigma}, omega={omega}")
    print(f"  chi(x1)=2t = {vogel_chi_x1(t)}")
    print(f"  chi(x3) = {vogel_chi_x3(t,omega)}")
    print(f"  chi(x5) = {vogel_chi_x5(t,sigma,omega)}")

if __name__ == "__main__":
    main()
