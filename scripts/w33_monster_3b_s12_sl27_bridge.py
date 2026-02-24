#!/usr/bin/env python3
"""Monster 3B -> (extraspecial) Heisenberg -> s12/sl(27): a concrete algebraic bridge.

One recurring pattern in the repo is that "missing Jacobi" / "missing phase"
phenomena get resolved by passing from grade-only coefficients to a genuine
Weyl–Heisenberg (extraspecial p-group) closure whose commutator bracket is
automatically Lie (Jacobi holds).

This script makes a sharp, *offline* Monster connection in that direction:

  - Monster has a prime-order class **3B** with centralizer

        C_M(3B)  =  3^{1+12} · 2Suz

    where 3^{1+12} is an extraspecial (Heisenberg) 3-group and 2Suz is the
    double cover of the Suzuki sporadic group.

  - For an extraspecial p-group p^{1+2n}, the Schrödinger/Heisenberg irrep has
    dimension p^n.  Here n=6, so p^n = 3^6 = 729.

  - The ternary Golay code has dimension 6 over F3, hence 3^6 codewords.  The
    s12 construction in this repo uses the nonzero codewords only:

        3^6 - 1 = 728 = 27^2 - 1 = dim sl(27)

So the "Golay Jordan–Lie algebra" basis size 728 sits exactly at the point
where Monster's 3B centralizer introduces a 3-adic Heisenberg structure.

Run:
  & .venv\\Scripts\\python.exe -X utf8 scripts\\w33_monster_3b_s12_sl27_bridge.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
for p in (ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def _int_from_factorization(fac: dict[int, int]) -> int:
    out = 1
    for p, e in fac.items():
        out *= int(p) ** int(e)
    return int(out)


def analyze() -> dict[str, Any]:
    from scripts.w33_leech_monster import (
        load_monster_atlas_ccls,
        load_sporadic_group_orders,
    )
    from scripts.w33_2suz_sp12_embedding import analyze as analyze_2suz_sp12

    atlas = load_monster_atlas_ccls()
    if atlas is None:
        return {"available": False, "reason": "monster_atlas_ccls.json missing"}
    classes = atlas.get("classes", {})
    if not isinstance(classes, dict) or "3B" not in classes:
        return {"available": False, "reason": "3B missing from ATLAS snapshot"}
    cent_3b = int(classes["3B"]["centralizer_order"])

    spor = load_sporadic_group_orders()
    if spor is None or "Suz" not in spor:
        return {"available": False, "reason": "sporadic_group_orders.json missing Suz"}
    suz_order = _int_from_factorization(
        {int(p): int(e) for p, e in spor["Suz"].items()}
    )
    two_suz_order = 2 * int(suz_order)

    heisenberg_order = 3**13  # 3^{1+12}
    expected = int(heisenberg_order) * int(two_suz_order)

    # Key Monster identity: 3B centralizer splits as extraspecial 3^{1+12} times 2Suz.
    assert cent_3b == expected, (
        "Expected |C_M(3B)| = 3^{13}·|2Suz|. "
        f"Got {cent_3b} vs {expected} (=3^{13}·{two_suz_order})."
    )

    # 3^{1+12} implies n=6, hence a Heisenberg irrep of dimension 3^6.
    heisenberg_n = 6
    heisenberg_irrep_dim = 3**heisenberg_n  # 729

    # s12 basis size: nonzero ternary Golay codewords = 3^6-1 = 728.
    import tools.s12_universal_algebra as s12

    gen = s12.ternary_golay_generator_matrix()
    G = np.array(gen, dtype=np.int64) % 3
    systematic = bool(np.array_equal(G[:, :6], np.eye(6, dtype=np.int64)))
    assert systematic, "Expected systematic Golay generator [I|A]."
    A = (G[:, 6:] % 3).astype(np.int64)
    A_symmetric = bool(np.array_equal(A, A.T))
    assert A_symmetric, "Expected symmetric A in systematic Golay generator [I|A]."

    codewords = s12.enumerate_linear_code_f3(gen)
    golay_words = len(codewords)
    golay_nonzero = golay_words - 1

    # Symplectic/Lagrangian bridge (6-qutrit phase space F3^{12}):
    # With generator [I|A], the code is the graph {(p, A p)} and since A is
    # symmetric it is isotropic for the standard symplectic form
    #   ω((p,q),(p',q')) = p·q' - q·p'.
    C = np.array(codewords, dtype=np.int64) % 3
    p = C[:, :6]
    q = C[:, 6:]
    omega = (p @ q.T - q @ p.T) % 3
    symplectic_isotropic = bool(np.all(omega == 0))
    assert symplectic_isotropic, "Golay codewords should be symplectic-isotropic."

    max_abelian_heisenberg_order = 3 ** (6 + 1)  # Lagrangian lift includes center

    hilbert_dim = 3**3  # 3 qutrits
    operator_basis = hilbert_dim**2  # 27^2 = 3^6
    traceless_basis = operator_basis - 1

    assert golay_words == 3**6, f"Expected 3^6 codewords, got {golay_words}"
    assert golay_nonzero == 3**6 - 1 == 728
    assert operator_basis == heisenberg_irrep_dim == 3**6 == 729
    assert traceless_basis == golay_nonzero == 728

    # ATLAS generators: verify 2.Suz acts symplectically on F3^12 (up to basis change).
    sp12 = analyze_2suz_sp12()
    assert sp12.get("available") is True
    assert sp12["field_p"] == 3
    assert sp12["dim"] == 12
    assert sp12["invariant_form"]["nullspace_dim"] == 1
    assert sp12["invariant_form"]["rank"] == 12
    assert sp12["standardized_generators"]["A_std_preserves_J0"] is True
    assert sp12["standardized_generators"]["B_std_preserves_J0"] is True

    return {
        "available": True,
        "monster": {
            "class": "3B",
            "centralizer_order": int(cent_3b),
            "centralizer_decomposition": "3^{1+12} · 2Suz",
            "extraspecial_order": int(heisenberg_order),
            "cofactor_2suz_order": int(two_suz_order),
        },
        "heisenberg": {
            "p": 3,
            "n": int(heisenberg_n),
            "irrep_dim": int(heisenberg_irrep_dim),
        },
        "golay": {
            "n_codewords": int(golay_words),
            "n_nonzero": int(golay_nonzero),
        },
        "golay_lagrangian": {
            "systematic_generator": bool(systematic),
            "A_matrix_mod3": A.tolist(),
            "A_symmetric": bool(A_symmetric),
            "symplectic_isotropic_all_pairs": bool(symplectic_isotropic),
            "max_abelian_subgroup_order": int(max_abelian_heisenberg_order),
        },
        "sl27": {
            "hilbert_dim": int(hilbert_dim),
            "operator_basis_dim": int(operator_basis),
            "traceless_dim": int(traceless_basis),
        },
        "2suz_sp12_embedding": {
            "available": True,
            "field_p": int(sp12["field_p"]),
            "dim": int(sp12["dim"]),
            "invariant_form_nullspace_dim": int(sp12["invariant_form"]["nullspace_dim"]),
            "invariant_form_rank": int(sp12["invariant_form"]["rank"]),
            "qutrits_n": int(sp12["interpretation"]["qutrits_n"]),
            "heisenberg_irrep_dim": int(sp12["interpretation"]["heisenberg_irrep_dim"]),
        },
    }


def main() -> None:
    rep = analyze()
    if rep.get("available") is not True:
        raise SystemExit(f"Unavailable: {rep}")

    monster = rep["monster"]
    heis = rep["heisenberg"]
    golay = rep["golay"]
    golay_lag = rep["golay_lagrangian"]
    sl27 = rep["sl27"]
    sp12 = rep["2suz_sp12_embedding"]

    print("=" * 78)
    print("MONSTER 3B <-> Heisenberg <-> Golay s12 <-> sl(27) BRIDGE")
    print("=" * 78)

    print()
    print("§1. Monster prime-order centralizer (ATLAS order snapshot)")
    print("-" * 58)
    print(f"  Class: {monster['class']}")
    print(f"  |C_M(3B)| = {monster['centralizer_order']}")
    print(
        "  Decomposition: |C_M(3B)| = 3^{1+12} · |2Suz| = "
        f"{monster['extraspecial_order']} · {monster['cofactor_2suz_order']}"
    )

    print()
    print("§2. Extraspecial 3^{1+12} ⇒ Heisenberg irrep dimension 3^6")
    print("-" * 58)
    print(f"  p = {heis['p']}")
    print(f"  n = {heis['n']} (since 3^(1+2n) = 3^(1+12))")
    print(f"  dim(Heisenberg irrep) = p^n = {heis['irrep_dim']}")

    print()
    print("§3. Ternary Golay code size ⇒ s12 basis size")
    print("-" * 58)
    print(f"  #Golay codewords = {golay['n_codewords']} = 3^6")
    print(f"  #nonzero codewords = {golay['n_nonzero']} = 3^6-1 = 728")

    print()
    print("§4. Golay code is Lagrangian in symplectic F3^12")
    print("-" * 58)
    print(f"  Systematic generator [I|A]: {bool(golay_lag['systematic_generator'])}")
    print(f"  A symmetric mod 3: {bool(golay_lag['A_symmetric'])}")
    print(
        "  Symplectic isotropic (all codeword pairs): "
        f"{bool(golay_lag['symplectic_isotropic_all_pairs'])}"
    )
    print(
        "  Lifted max-abelian subgroup order in 3^{1+12}: "
        f"{int(golay_lag['max_abelian_subgroup_order'])} (=3^7)"
    )

    print()
    print("§5. sl(27) closure: 27^2-1 = 728")
    print("-" * 58)
    print(f"  Hilbert dim (3 qutrits) = 3^3 = {sl27['hilbert_dim']}")
    print(f"  Operator basis dim = 27^2 = {sl27['operator_basis_dim']}")
    print(f"  traceless dim = 27^2-1 = {sl27['traceless_dim']}")

    print()
    print("Â§6. 2.Suz âŠ‚ Sp(12,3) (6-qutrit Clifford backbone)")
    print("-" * 58)
    print(f"  ATLAS GF(3) dim-12 rep available: {bool(sp12['available'])}")
    print(
        "  invariant alternating form: nullspace dim = "
        f"{int(sp12['invariant_form_nullspace_dim'])} (unique up to scalar), "
        f"rank = {int(sp12['invariant_form_rank'])}"
    )
    print(
        f"  phase space dim = {int(sp12['dim'])} â‡’ qutrits n = {int(sp12['qutrits_n'])}, "
        f"Heisenberg irrep dim = {int(sp12['heisenberg_irrep_dim'])}"
    )

    print()
    print("ALL CHECKS PASSED ✓")


if __name__ == "__main__":
    main()
