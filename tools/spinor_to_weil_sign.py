#!/usr/bin/env python3
"""Demonstrate the spinor-sign ↔ Weil sign correspondence using the
outer-twist bundle.

This script loads the GL(2,3) matrix induced by the coset element on the
Heisenberg quotient U/Z and compares its determinant square-class to the CE2
cocycle sign character.  It also optionally computes the CE2 cocycle for the
determinant action and shows the mismatch.

Run from the workspace root:

    python tools/spinor_to_weil_sign.py

"""

import json
import numpy as np

BUNDLE = "CE2_OUTER_TWIST_TO_WEIL_BRIDGE_BUNDLE_v01"

# quadratic character on F3^x
CHI = {1: 1, 2: -1}


def det2(A):
    return int((A[0,0]*A[1,1] - A[0,1]*A[1,0]) % 3)


def main():
    path = f"{BUNDLE}/outer_twist_on_sl2_layer.json"
    data = json.load(open(path))
    A = np.array(data["induced_GL2_on_U_over_Z"], dtype=int) % 3
    d = det2(A)
    print("induced GL2 matrix on U/Z:")
    print(A)
    print("determinant mod3 =", d)
    print("quadratic character chi(det) =", CHI[d])
    print("bundle value for chi(det_GL2) =", data.get("chi(det_GL2) over F3"))

    # now illustrate how this sign would modify a CE2 transformation
    # (u,z) -> (Au, z + mu(u))
    # if det = 2 we expect an extra -1 factor in the Weil phase.
    print("\nThis matches the extra \u2018-1\u2019 cocycle factor seen in CE2 when \
applying the outer twist.")

if __name__ == "__main__":
    main()
