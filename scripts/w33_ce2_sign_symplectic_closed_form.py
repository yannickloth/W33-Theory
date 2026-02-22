#!/usr/bin/env python3
"""CE2 simple-family sign: symplectic delta + exact constant-line selection rule.

This is *not* a new pillar; it is a compact algebra report that makes the
Heisenberg/metaplectic backbone behind the CE2 mixed-sector phase explicit.

Starting point (committed artifacts):
  - committed_artifacts/ce2_simple_family_sign_map.json  (864 keys)
  - artifacts/e6_cubic_affine_heisenberg_model.json      (E6 27 -> (u,z) in F3^2×F3)

Exact structural laws verified here:
  1) **u-line collinearity**:
       Let u(x) be the u-projection (F3^2). For every (c,m,o) in the sign-map,
       the triple (u_c,u_m,u_o) is collinear with
         t=1  if u_m == u_o
         t=2  if u_o - u_c == -(u_m - u_c)
       The map splits evenly: 432 keys in each regime.

  2) **Symplectic delta law (t=2 only)**:
       Write d = u_m - u_c in F3^2 and define the alternating form
         ω((x,y),(a,b)) = y·a - x·b   (mod 3).
       Then the central labels satisfy the exact identity:
         z_o - z_m == ω(u_c, d)   (mod 3).

  3) **Exact constant-line rule (t=1 and t=2, SAME set)**:
       For fixed (u_c,d) (with d ≠ 0), the sign as a function of the z-data is
       either constant or a 1D “metaplectic” character in z.

       The (u_c,d) pairs where the sign is constant are **exactly** those with:
         d1 != 0   and   ω(u_c, d) == k(d)   (mod 3),
       where (d1,d2)=d and
         k(d) = -d1  if d2 == 0
                d1   otherwise.

Interpretation:
  - ω is the same symplectic pairing that supplies the missing 2-cocycle phase
    in the s12 -> Weyl–Heisenberg closure, and the same “phase bridge” used by
    the E8 Z3 / L∞ firewall CE2 predictor.

Run:
  & .venv\\Scripts\\python.exe -X utf8 scripts\\w33_ce2_sign_symplectic_closed_form.py
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, Tuple

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
for p in (ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from ce2_global_cocycle import (  # noqa: E402
    _heisenberg_vec_maps,
    _simple_family_sign_map,
)

U2 = Tuple[int, int]


def _u(e6id: int, e6id_to_vec: dict[int, tuple[int, int, int]]) -> U2:
    v = e6id_to_vec[int(e6id)]
    return (int(v[0]) % 3, int(v[1]) % 3)


def _z(e6id: int, e6id_to_vec: dict[int, tuple[int, int, int]]) -> int:
    return int(e6id_to_vec[int(e6id)][2]) % 3


def _u2_sub(a: U2, b: U2) -> U2:
    return ((a[0] - b[0]) % 3, (a[1] - b[1]) % 3)


def omega(u: U2, v: U2) -> int:
    """Alternating form ω((x,y),(a,b)) = y·a - x·b (mod 3)."""
    x, y = int(u[0]) % 3, int(u[1]) % 3
    a, b = int(v[0]) % 3, int(v[1]) % 3
    return (y * a - x * b) % 3


def k_of_direction(d: U2) -> int | None:
    """k(d) used in the exact constant-line condition (returns None for d1==0)."""
    d1, d2 = int(d[0]) % 3, int(d[1]) % 3
    if d1 == 0:
        return None
    if d2 == 0:
        return (-d1) % 3
    return d1


def chi(t: int) -> int:
    """F3 -> {±1} with chi(0)=chi(1)=+1, chi(2)=-1."""
    return 1 if int(t) % 3 in (0, 1) else -1


def _iter_dirs() -> Iterable[U2]:
    for a in range(3):
        for b in range(3):
            if a == 0 and b == 0:
                continue
            yield (a, b)


def _fit_eps_c0_for_sum(points: list[tuple[int, int, int]]) -> tuple[int, int] | None:
    """Fit sign = eps*chi((zm+zo+c0) mod 3) on a set of (zm,zo,sign) points."""
    for eps in (1, -1):
        for c0 in (0, 1, 2):
            ok = True
            for zm, zo, sgn in points:
                if eps * chi((zm + zo + c0) % 3) != int(sgn):
                    ok = False
                    break
            if ok:
                return (eps, c0)
    return None


def main() -> Dict[str, object]:
    sign_map = _simple_family_sign_map()
    e6id_to_vec, _vec_to_e6id = _heisenberg_vec_maps()

    # ------------------------------------------------------------------
    # SECTION 1: u-line geometry split (t=1 vs t=2)
    # ------------------------------------------------------------------
    t_ctr: Counter[int] = Counter()
    for c_i, m_i, o_i in sign_map.keys():
        uc, um, uo = _u(c_i, e6id_to_vec), _u(m_i, e6id_to_vec), _u(o_i, e6id_to_vec)
        t_ctr[1 if um == uo else 2] += 1

    assert len(sign_map) == 864
    assert t_ctr[1] == 432 and t_ctr[2] == 432

    # ------------------------------------------------------------------
    # SECTION 2: symplectic delta law (t=2)
    # ------------------------------------------------------------------
    for (c_i, m_i, o_i), sgn in sign_map.items():
        uc, um, uo = _u(c_i, e6id_to_vec), _u(m_i, e6id_to_vec), _u(o_i, e6id_to_vec)
        if um == uo:
            continue
        d = _u2_sub(um, uc)
        # collinearity: uo == uc - d
        assert uo == ((uc[0] - d[0]) % 3, (uc[1] - d[1]) % 3)
        dz = (_z(o_i, e6id_to_vec) - _z(m_i, e6id_to_vec)) % 3
        assert dz == omega(uc, d)
        _ = int(sgn)  # keep loop symmetric; sign not used in this law

    # ------------------------------------------------------------------
    # SECTION 3: constant-line selection rule (same set for t=1 and t=2)
    # ------------------------------------------------------------------
    # Build per-(uc,d) tables from committed sign-map.
    # t=1: u_m == u_o -> 6 ordered (zm,zo) points (zm != zo always)
    t1_table: dict[tuple[U2, U2], list[tuple[int, int, int]]] = defaultdict(list)
    # t=2: u_m != u_o -> 3 zm values; keep one representative zo per zm (zc varies)
    t2_table_by_zm: dict[tuple[U2, U2], dict[int, tuple[int, int]]] = defaultdict(dict)

    for (c_i, m_i, o_i), sgn in sign_map.items():
        uc, um, uo = _u(c_i, e6id_to_vec), _u(m_i, e6id_to_vec), _u(o_i, e6id_to_vec)
        zm, zo = _z(m_i, e6id_to_vec), _z(o_i, e6id_to_vec)
        if um == uo:
            d = _u2_sub(um, uc)
            t1_table[(uc, d)].append((zm, zo, int(sgn)))
        else:
            d = _u2_sub(um, uc)
            prev = t2_table_by_zm[(uc, d)].get(zm)
            if prev is not None:
                # zc variations should not change (zo,sign) at fixed zm
                assert prev == (zo, int(sgn))
            t2_table_by_zm[(uc, d)][zm] = (zo, int(sgn))

    assert len(t1_table) == 72
    assert len(t2_table_by_zm) == 72
    assert all(len(v) == 6 for v in t1_table.values())
    assert all(len(v) == 3 for v in t2_table_by_zm.values())

    # Determine which (uc,d) are constant from data, separately for t=1 and t=2.
    const_t1: set[tuple[U2, U2]] = set()
    for key, pts in t1_table.items():
        signs = {int(s) for _zm, _zo, s in pts}
        if len(signs) == 1:
            const_t1.add(key)

    const_t2: set[tuple[U2, U2]] = set()
    for key, by_zm in t2_table_by_zm.items():
        signs = {int(s) for _zo, s in by_zm.values()}
        if len(signs) == 1:
            const_t2.add(key)

    assert const_t1 == const_t2
    const_set = const_t1
    assert len(const_set) == 18

    # Closed-form prediction of the constant set via ω(u_c,d)==k(d).
    pred_const: set[tuple[U2, U2]] = set()
    for uc in [(i, j) for i in range(3) for j in range(3)]:
        for d in _iter_dirs():
            kd = k_of_direction(d)
            if kd is None:
                continue
            if omega(uc, d) == kd:
                pred_const.add((uc, d))
    assert pred_const == const_set

    # Fit eps,c0 parameters for the variable cases (separately for t=1 and t=2).
    var_t1_params: Counter[tuple[int, int]] = Counter()
    var_t2_params: Counter[tuple[int, int]] = Counter()
    for key, pts in t1_table.items():
        if key in const_set:
            continue
        fit = _fit_eps_c0_for_sum(pts)
        assert fit is not None
        var_t1_params[fit] += 1

    for key, by_zm in t2_table_by_zm.items():
        if key in const_set:
            continue
        pts = [(zm, zo, sgn) for zm, (zo, sgn) in by_zm.items()]
        fit = _fit_eps_c0_for_sum(pts)
        assert fit is not None
        var_t2_params[fit] += 1

    # ------------------------------------------------------------------
    # Print report
    # ------------------------------------------------------------------
    print("=" * 78)
    print("CE2 SIGN: symplectic delta + constant-line closed form (report)")
    print("=" * 78)
    print()
    print("SECTION 1: u-line split")
    print("-" * 50)
    print("  sign-map keys:", len(sign_map))
    print("  t=1 (u_m==u_o):", int(t_ctr[1]))
    print("  t=2 (3 distinct):", int(t_ctr[2]))
    print("  ✓ balanced split 432/432")

    print()
    print("SECTION 2: symplectic delta law (t=2)")
    print("-" * 50)
    print("  ✓ verified for all t=2 keys: (z_o - z_m) == ω(u_c, u_m - u_c) mod 3")

    print()
    print("SECTION 3: constant-line selection rule")
    print("-" * 50)
    print("  constant (u_c,d) pairs:", len(const_set))
    print("  rule: d1!=0 and ω(u_c,d)==k(d), k(d)=(-d1 if d2==0 else d1)")
    print("  ✓ predicted set equals data-derived set")

    print()
    print("SECTION 4: variable-case χ parametrizations (z_m+z_o)")
    print("-" * 50)
    print("  t=1 variable-case param counts (eps,c0):", dict(var_t1_params))
    print("  t=2 variable-case param counts (eps,c0):", dict(var_t2_params))
    print("  ✓ every non-constant case fits eps*chi(zm+zo+c0)")

    print()
    print("SUMMARY")
    print("-" * 50)
    print("  1) z-delta is symplectic (exact).")
    print("  2) constant-line cases are ω==k(d) (exact).")
    print("  3) remaining cases are 1D χ-characters in z_m+z_o.")

    return {
        "n_keys": len(sign_map),
        "t_counts": dict(t_ctr),
        "constant_pairs": len(const_set),
        "var_params_t1": dict(var_t1_params),
        "var_params_t2": dict(var_t2_params),
    }


if __name__ == "__main__":
    main()
