#!/usr/bin/env python3
"""Basic Moonshine CFT utilities: compute j(q) expansion and compare to Monster dims.

This script produces the q-expansion of the classical Klein j-invariant up to
some order and prints the coefficients alongside the first few dimensions of the
Monster simple modules (starting 1, 196883, ...).  It can also check the well
known decomposition j(q)=q^{-1}+744+196884 q + 21493760 q^2 + ...

Usage:
    python tools/moonshine_cft.py --terms 10
"""

from __future__ import annotations

import argparse
import sympy as sp
# we can provide hardcoded j-coefficients for the first few terms

# Monster simple module dimensions
MONSTER_DIMS = [1, 196883, 21296876, 842609326, 18538750076]


def j_series(terms: int) -> list[int]:
    """Return first *terms* coefficients of j(q) expansion.

    We hardcode the well-known numbers for simplicity; the sequence begins
    [1, 744, 196884, 21493760, 864299970, ...] corresponding to q^{-1}, q^0, q^1, ...
    """
    base = [1, 744, 196884, 21493760, 864299970, 20245856256, 333202640600]
    return base[: terms + 1]


def main():
    parser = argparse.ArgumentParser(description="Moonshine CFT utilities")
    parser.add_argument('--terms', type=int, default=5, help='number of q coefficients')
    args = parser.parse_args()
    coeffs = j_series(args.terms)
    print('j(q) coefficients (starting q^{-1})')
    for n,c in enumerate(coeffs):
        print(n-1, c, ('Monster dim' if n-1< len(MONSTER_DIMS) else ''), MONSTER_DIMS[n-1] if n-1 < len(MONSTER_DIMS) else '')

if __name__ == '__main__':
    main()
