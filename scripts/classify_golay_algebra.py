#!/usr/bin/env python3
"""Heuristic classification notes for the 24-dimensional Golay Lie algebra over F3.

This repo constructs a concrete 24-dimensional Lie algebra over GF(3) that
recurs in the s12 / 3-qutrit Heisenberg closure machinery. The goal of this
script is *not* to prove a literature identification, but to provide a
reproducible invariant fingerprint that can be compared to known modular
families.

What we can assert computationally (see `scripts/w33_golay_lie_algebra.py`):
  - dim(L)=24 over GF(3)
  - Jacobi holds, [L,L]=L (perfect), center=0, Killing rank=0
  - dim Der(L)=33 = 24 inner + 9 outer
  - a strong tensor/product structure in the deterministic basis:
        L ≅ L0 ⊗ A
    with dim(L0)=8 (a "c=0 slice") and A a 3-dim local algebra
    A ≅ F3[ε]/(ε^3) (equivalently, group algebra F3[C3]).
  - outer derivations decompose as 6+3 in a canonical way:
        Out(L) = (Out(L0) ⊗ A) ⊕ (Cent(L0) ⊗ Der(A))

These invariants are consistent with Cartan-type / modular Lie algebra
phenomena in characteristic 3; a plausible lead is the Skryabin family.
Reference (lead, not a proof of isomorphism):
  - S. Skryabin, "New series of simple Lie algebras of characteristic 3",
    Sbornik: Mathematics 76 (1993) 297–317.

Run:
  & .venv\\Scripts\\python.exe -X utf8 scripts\\classify_golay_algebra.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
for p in (ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from scripts.w33_golay_lie_algebra import analyze


def _pp_kv(k: str, v: Any) -> str:
    if isinstance(v, float):
        return f"{k}={v:.6g}"
    return f"{k}={v}"


def main() -> None:
    rep = analyze(compute_derivations=True)
    if rep.get("available") is not True:
        raise SystemExit(f"Unavailable: {rep}")

    lie = rep.get("lie", {})
    deriv = rep.get("derivations", {})
    nf = rep.get("normal_form", {})
    td = rep.get("tensor_decomposition", {})
    l0 = td.get("l0_slice", {}) if isinstance(td, dict) else {}
    fiber = td.get("fiber_algebra", {}) if isinstance(td, dict) else {}
    decomp = td.get("derivation_decomposition", {}) if isinstance(td, dict) else {}

    print("Invariant fingerprint (GF(3))")
    print("-" * 60)
    print(_pp_kv("dim(L)", rep.get("dim")))
    if isinstance(lie, dict):
        print(
            "  "
            + ", ".join(
                [
                    _pp_kv("perfect", lie.get("perfect")),
                    _pp_kv("center", lie.get("center_dim")),
                    _pp_kv("kill_rank", lie.get("killing_form_rank_mod3")),
                ]
            )
        )
    if isinstance(deriv, dict):
        print(
            "  "
            + ", ".join(
                [
                    _pp_kv("Der", deriv.get("dim_derivations")),
                    _pp_kv("Inn", deriv.get("dim_inner")),
                    _pp_kv("Out", deriv.get("dim_outer")),
                ]
            )
        )

    if isinstance(nf, dict) and nf.get("available") is True:
        print(
            "  normal_form: "
            + ", ".join(
                [
                    _pp_kv("phi_is_zero", nf.get("phi_is_zero")),
                    _pp_kv("fiber_addition", nf.get("c_addition_holds")),
                ]
            )
        )

    if isinstance(l0, dict) and l0.get("available") is True:
        d0 = l0.get("derivations", {}) if isinstance(l0.get("derivations"), dict) else {}
        print(
            "  tensor_factor: "
            + ", ".join(
                [
                    _pp_kv("dim(L0)", l0.get("dim")),
                    _pp_kv("Der(L0)", d0.get("dim_derivations")),
                    _pp_kv("Out(L0)", d0.get("dim_outer")),
                ]
            )
        )
    if isinstance(fiber, dict) and fiber.get("available") is True:
        print(
            "  fiber_factor: "
            + ", ".join(
                [
                    _pp_kv("dim(A)", fiber.get("dim")),
                    _pp_kv("Der(A)", fiber.get("dim_derivations")),
                ]
            )
        )
    if isinstance(decomp, dict) and decomp.get("available") is True:
        comps = decomp.get("constructed_outer_components", {})
        if isinstance(comps, dict):
            print(
                "  outer_split: "
                + ", ".join(
                    [
                        _pp_kv("Out(L0)⊗A", comps.get("outer_l0_tensor_A")),
                        _pp_kv("Cent(L0)⊗Der(A)", comps.get("centroid_l0_tensor_derA")),
                    ]
                )
            )    # probe inner automorphism commutation using ad matrices
    try:
        from scripts.w33_golay_lie_algebra import _ad_matrices
        import numpy as np
        adm = _ad_matrices(alg)
        size = 24
        I = np.eye(size, dtype=int)
        mod3 = lambda A: A % 3
        T = [mod3(I + A) for A in adm]
        commuting = all(
            np.array_equal(mod3(T[i].dot(T[j])), mod3(T[j].dot(T[i])))
            for i in range(size)
            for j in range(size)
        )
        print("  inner_aut_commuting?", commuting)
    except Exception as e:
        print("  inner_aut_commuting? check failed", e)
    print()
    print("Suggested lead (heuristic)")
    print("-" * 60)
    print("  - characteristic 3 Cartan-type phenomena are plausible")
    print("  - compare invariants to Skryabin 1993 new series (e.g. S(1,2) family)")


if __name__ == "__main__":
    main()
