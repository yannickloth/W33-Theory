#!/usr/bin/env python3
"""CE2 simple-family sign as a Heisenberg quadratic refinement (geometry report).

This script is *not* a new pillar; it is a consolidation report to make the
algebraic breakthrough legible:

We now have an explicit GF(2) degree-≤4 phase polynomial for the CE2
simple-family sign(c,match,other) ∈ {±1}. This replaces the last remaining
table-driven ingredient in the global CE2 predictor used by the L∞ firewall.

Key geometric takeaways (verified here):
  1) The (u_c,u_m,u_o) triples (u ∈ F3^2) are always collinear; equivalently
       u_o - u_c ∈ {u_m - u_c, -(u_m - u_c)}.
  2) The observed support set couples u-line geometry to central z labels in a
     structured way (two regimes depending on whether u_m == u_o).
  3) The sign is representable by a *low-degree* GF(2) polynomial only when the
     full Heisenberg coordinate (u,z) for the c-point is included. If you
     project away z_c and try to fit a degree-≤4 polynomial in the remaining
     variables, the system becomes inconsistent.

Interpretation:
  - This is exactly the behavior of a **central extension / quadratic
    refinement**: the "extra" central coordinate z plays the role of an
    auxiliary variable that lowers algebraic degree, analogous to how the
    Weyl–Heisenberg phase (symplectic cocycle) resolves the s12 grade-only
    Jacobi obstruction by upgrading coefficients to an honest associative
    algebra (commutator bracket).

Run:
  & .venv\\Scripts\\python.exe -X utf8 scripts\\w33_ce2_sign_quadratic_refinement.py
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
for p in (ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from ce2_global_cocycle import (  # noqa: E402
    _heisenberg_vec_maps,
    _simple_family_sign_map,
)


def _vec2_add(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
    return ((a[0] + b[0]) % 3, (a[1] + b[1]) % 3)


def _vec2_sub(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
    return ((a[0] - b[0]) % 3, (a[1] - b[1]) % 3)


def _encode_trit_pair_bits(trit: int) -> tuple[int, int]:
    """Encode a trit in {0,1,2} into two GF(2) bits (is1,is2)."""
    t = int(trit) % 3
    if t == 0:
        return (0, 0)
    if t == 1:
        return (1, 0)
    return (0, 1)


def _rref_solve_gf2(rows_aug: list[int], n_vars: int) -> tuple[bool, int, int]:
    """Return (consistent?, rank, solution_weight) for A x = b over GF(2)."""
    rows = [int(r) for r in rows_aug]
    m = len(rows)
    pivot_row = 0
    pivots: list[int] = []
    for col in range(n_vars):
        pivot = None
        for r in range(pivot_row, m):
            if (rows[r] >> col) & 1:
                pivot = r
                break
        if pivot is None:
            continue
        if pivot != pivot_row:
            rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        prow = rows[pivot_row]
        for r in range(m):
            if r != pivot_row and ((rows[r] >> col) & 1):
                rows[r] ^= prow
        pivots.append(col)
        pivot_row += 1
        if pivot_row >= m:
            break

    rhs_bit = 1 << n_vars
    var_mask = rhs_bit - 1
    for r in rows:
        if (r & var_mask) == 0 and (r & rhs_bit):
            return (False, len(pivots), 0)

    x = 0
    for i, col in enumerate(pivots):
        if rows[i] & rhs_bit:
            x |= 1 << col
    return (True, len(pivots), int(x).bit_count())


def main() -> None:
    print("=" * 78)
    print("CE2 SIGN GEOMETRY: Heisenberg quadratic refinement report")
    print("=" * 78)

    sign_map = _simple_family_sign_map()
    e6id_to_vec, _vec_to_e6id = _heisenberg_vec_maps()

    def u(e6id: int) -> tuple[int, int]:
        return e6id_to_vec[int(e6id)][:2]

    def z(e6id: int) -> int:
        return int(e6id_to_vec[int(e6id)][2])

    # ---------------------------------------------------------------------
    # 1) Collinearity in u ∈ F3^2 (all triples lie on an affine line)
    # ---------------------------------------------------------------------
    t_ctr = Counter()
    for c_i, m_i, o_i in sign_map.keys():
        uc, um, uo = u(c_i), u(m_i), u(o_i)
        du = _vec2_sub(um, uc)
        dv = _vec2_sub(uo, uc)
        if dv == du:
            t = 1
        elif dv == ((-du[0]) % 3, (-du[1]) % 3):
            t = 2
        else:
            raise AssertionError("unexpected u-triple: not collinear as expected")
        t_ctr[t] += 1

    print()
    print("SECTION 1: u-line geometry (F3^2)")
    print("-" * 50)
    print("  unique sign keys:", len(sign_map), "(expected 864)")
    print(
        "  collinearity parameter t counts:",
        dict(t_ctr),
        "(t=1: u_m=u_o, t=2: 3 distinct)",
    )
    assert len(sign_map) == 864
    assert sum(t_ctr.values()) == 864

    # ---------------------------------------------------------------------
    # 2) Structured coupling to central labels z ∈ F3
    # ---------------------------------------------------------------------
    z_case = Counter()
    for c_i, m_i, o_i in sign_map.keys():
        uc, um, uo = u(c_i), u(m_i), u(o_i)
        t = 1 if um == uo else 2
        zc, zm, zo = z(c_i), z(m_i), z(o_i)
        if zm == zo:
            rel = "zm==zo"
        elif zc == zm:
            rel = "zc==zm"
        elif zc == zo:
            rel = "zc==zo"
        else:
            rel = "zc==third"
        z_case[(t, rel)] += 1

    print()
    print("SECTION 2: z-structure by u-regime")
    print("-" * 50)
    for k in sorted(z_case):
        print(f"  {k}: {z_case[k]}")
    # Empirical structure (observed on the CE2 support set):
    # - if u_m == u_o (t=1), then zm!=zo always and zc can be any of {zm,zo,third}
    # - if u_m != u_o (t=2), then zc is never the third when zm!=zo; equality zm==zo occurs.
    assert z_case[(1, "zm==zo")] == 0
    assert z_case[(2, "zc==third")] == 0

    # ---------------------------------------------------------------------
    # 3) Polynomial representation and "quadratic refinement" effect
    # ---------------------------------------------------------------------
    poly_path = (
        ROOT / "committed_artifacts" / "ce2_simple_family_sign_poly_gf2_deg4.json"
    )
    poly = json.loads(poly_path.read_text(encoding="utf-8"))
    idxs = poly.get("coeff_feature_indices", [])
    if not isinstance(idxs, list):
        raise ValueError("unexpected polynomial artifact format")
    weight = len(idxs)

    print()
    print("SECTION 3: committed GF(2) sign polynomial")
    print("-" * 50)
    print(f"  coeff weight: {weight}")
    print(f"  declared rank: {poly.get('rank')}, nullity: {poly.get('nullity')}")
    print(f"  degree histogram: {poly.get('coeff_degree_hist')}")
    assert int(poly.get("max_degree")) == 4

    # Demonstrate the refinement effect:
    # Attempt to fit a degree-≤4 polynomial using only the *reduced* variable
    # set (drop z_c, keep uc,um,uo,zm,zo). This corresponds to 8 trits => 16 bits.
    #
    # With the standard 2-bit indicator encoding, the degree-≤4 system is inconsistent.
    n_bits = 16
    monomials: list[int] = [0]
    for d in range(1, 5):
        for combo in combinations(range(n_bits), d):
            m = 0
            for b in combo:
                m |= 1 << b
            monomials.append(m)
    mask_to_idx = {m: i for i, m in enumerate(monomials)}
    assert len(monomials) == 2517
    assert len(mask_to_idx) == 2517

    rows_aug: list[int] = []
    for (c_i, m_i, o_i), sgn in sign_map.items():
        uc = u(c_i)
        um = u(m_i)
        uo = u(o_i)
        zm = z(m_i)
        zo = z(o_i)
        trits = (uc[0], uc[1], um[0], um[1], zm, uo[0], uo[1], zo)

        inp = 0
        for i, t in enumerate(trits):
            b0, b1 = _encode_trit_pair_bits(t)
            if b0:
                inp |= 1 << (2 * i + 0)
            if b1:
                inp |= 1 << (2 * i + 1)

        ones = [i for i in range(n_bits) if ((inp >> i) & 1)]
        feat_mask = 1 << mask_to_idx[0]
        for d in range(1, min(4, len(ones)) + 1):
            for combo in combinations(ones, d):
                mm = 0
                for b in combo:
                    mm |= 1 << b
                feat_mask |= 1 << mask_to_idx[mm]

        rhs = 0 if int(sgn) == 1 else 1
        rows_aug.append(feat_mask | (rhs << len(monomials)))

    consistent, rank, _sol_weight = _rref_solve_gf2(rows_aug, len(monomials))

    print()
    print("SECTION 4: refinement check (drop z_c, fit deg≤4)")
    print("-" * 50)
    print(f"  reduced vars (deg≤4 monomials): {len(monomials)}")
    print(f"  rank in reduced system: {rank}")
    print(f"  consistent?: {consistent}  (expected False)")
    assert consistent is False

    print()
    print("SUMMARY")
    print("-" * 50)
    print(
        "  - The CE2 sign is a low-degree GF(2) phase only on the *extended* (u,z) space."
    )
    print("  - Projecting away the central z breaks low-degree representability.")
    print("  => Central coordinate acts as a quadratic refinement / cocycle witness.")


if __name__ == "__main__":
    main()
