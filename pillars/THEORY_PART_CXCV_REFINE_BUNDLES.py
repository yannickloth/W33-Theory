#!/usr/bin/env python3
"""Refactor of bundle analyses using direct-product structure.

This auxiliary module revisits earlier bundle computations (S3-sheet,
axis-block-twist) and shows how the monodromy part \Gamma and the external
triality/automorphism part H may be handled independently.  The key helper is
`direct_product_closure` from `THEORY_PART_CXCIV_DIRECT_PRODUCT_UTILS`.

Currently we provide two demonstrations:

* compute sizes of \Gamma, H and their direct-product closure; the result
  matches the naive product |\Gamma|\cdot|H|.
* illustrate how a generic bundle analysis (here S3-sheet) need only consider
  \Gamma; the H-action can be appended afterwards by forming the direct
  product.

A fuller refactor of the original pillar scripts would simply call the
`closure` function instead of performing a BFS over all permutations.
"""

from __future__ import annotations

import json
from pathlib import Path

from THEORY_PART_CXCIV_DIRECT_PRODUCT_UTILS import direct_product_closure
from THEORY_PART_CXCVII_AUT_NORMALISER import load_permutations, build_gamma
from THEORY_PART_CXCVI_TOMOTOPE_AUTOMORPHISMS import (
    compute_automorphisms,
    build_graph,
    load_r_generators,
)

ROOT = Path(__file__).resolve().parent


def load_Gamma_H():
    perms = load_permutations()
    Gamma = build_gamma(perms)
    G = build_graph(load_r_generators())
    autos = compute_automorphisms(G)
    H = [tuple(autos[i][j] for j in range(192)) for i in range(len(autos))]
    return Gamma, H


def report_closure():
    Gamma, H = load_Gamma_H()
    closure = direct_product_closure(Gamma, H)
    info = {
        "Gamma_size": len(Gamma),
        "H_size": len(H),
        "closure_size": len(closure),
        "expected_product": len(Gamma) * len(H),
    }
    Path(ROOT / "closure_info.json").write_text(json.dumps(info, indent=2))
    print("closure info written to closure_info.json")
    return info


def main():
    info = report_closure()
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
