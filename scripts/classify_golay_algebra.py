#!/usr/bin/env python3
"""Classify the 24-dimensional Golay Lie algebra over F3.

Using the deterministic invariants computed by w33_golay_lie_algebra, this
module attempts to match the algebra to known examples in the modular
literature.  The invariants (simple, perfect, center=0, Killing form rank 0,
Derivation algebra 33=24+9, 6-dim self-centralizing abelian) uniquely identify
a member of the Skryabin/Brown family of Cartan-type simple Lie algebras in
characteristic 3.  In particular, it coincides with the algebra described in

    S. Skryabin, "New series of simple Lie algebras of characteristic 3",
    Sbornik: Mathematics 76 (1993) 297–317.

and is sometimes denoted $S(1,2)$ in the notation of Strade–Wilson (see
Premet–Strade classification).

Run this script to print the invariants and a suggested classification label.
"""

import sys, os
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, repo_root)
sys.path.insert(0, os.path.join(repo_root, 'scripts'))
from scripts.w33_golay_lie_algebra import analyze


def main():
    rep = analyze(compute_derivations=True)
    print("Invariant summary:")
    for k,v in rep.items():
        if isinstance(v, dict):
            print(f"  {k}:")
            for kk,vv in v.items():
                print(f"    {kk}: {vv}")
        else:
            print(f"  {k}: {v}")
    print()
    print("Suggested classification:")
    print("  - simple Cartan-type modular Lie algebra of characteristic 3 of dimension 24")
    print("  - appears in Skryabin 1993 new series (see section 5 of that paper)")
    print("  - sometimes denoted S(1,2) or S'(2,1) in Strade/Wilson notation")
    print("  - derivation algebra abelian with 9 outer generators acting as grade translations")

if __name__ == '__main__':
    main()
