#!/usr/bin/env python3
"""CE2 simple-family sign depends only on F9 / bilinear invariants (algebra report).

This report upgrades the "closed form" CE2 sign law into a more conceptual one:

  - The u-coordinates live in F3^2.  Adjoin i with i^2 = -1 = 2 to get F9.
  - Identify (x, y) ∈ F3^2 with x + i y ∈ F9.
  - For d ∈ F3^2, conjugation is Frobenius: conj(d) = d^3 = x - i y.
  - Then for u ∈ F3^2:
        u * conj(d) = dot(u,d) + i * omega(u,d)
    where:
        dot(u,d)   = u1*d1 + u2*d2
        omega(u,d) = u2*d1 - u1*d2

Empirically (and now verifiably):
  - The CE2 "constant-line" selector depends only on (d, omega(u_c,d)).
  - The remaining c0/eps functions depend only on (d, dot(u_c,d), omega(u_c,d)).

So the cocycle/phase is controlled by the F9 product u_c * conj(d), i.e. by
bilinear pairings with the line-direction d, not by raw coordinates of u_c.

Run:
  & .venv\\Scripts\\python.exe -X utf8 scripts\\w33_ce2_sign_f9_invariants.py
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
for p in (ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from ce2_global_cocycle import (  # noqa: E402
    _SIMPLE_FAMILY_SIGN_C0_TERMS,
    _SIMPLE_FAMILY_SIGN_CONST_P_TERMS,
    _SIMPLE_FAMILY_SIGN_EPS_TERMS,
    _eval_f3_sparse_poly,
    _f3_chi,
    _f3_k_of_direction,
    _f3_omega,
    _heisenberg_vec_maps,
    _simple_family_sign_map,
)


def _dot(u: tuple[int, int], v: tuple[int, int]) -> int:
    return (int(u[0]) * int(v[0]) + int(u[1]) * int(v[1])) % 3


def _f9_mul(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
    """Multiply in F9 represented as (re, im) with i^2 = -1 = 2 (mod 3)."""
    ar, ai = int(a[0]) % 3, int(a[1]) % 3
    br, bi = int(b[0]) % 3, int(b[1]) % 3
    # (ar + ai*i)(br + bi*i) = (ar*br + ai*bi*i^2) + (ar*bi + ai*br)*i
    re = (ar * br + ai * bi * 2) % 3
    im = (ar * bi + ai * br) % 3
    return (int(re), int(im))


def _f9_conj(a: tuple[int, int]) -> tuple[int, int]:
    """Conjugation in F9 (Frobenius for F9/F3): (re,im) -> (re,-im)."""
    return (int(a[0]) % 3, (-int(a[1])) % 3)


def main() -> None:
    print("=" * 78)
    print("CE2 SIGN: F9 / bilinear invariants")
    print("=" * 78)

    sign_map = _simple_family_sign_map()
    e6id_to_vec, _ = _heisenberg_vec_maps()

    def u(e6id: int) -> tuple[int, int]:
        vec = e6id_to_vec[int(e6id)]
        return (int(vec[0]) % 3, int(vec[1]) % 3)

    def z(e6id: int) -> int:
        return int(e6id_to_vec[int(e6id)][2]) % 3

    # ------------------------------------------------------------------
    # §1. Verify the F9 identity: u*conj(d) = dot + i*omega
    # ------------------------------------------------------------------
    print()
    print("§1. F9 identity check")
    print("-" * 50)

    trials = 0
    for c_i, m_i, _o_i in list(sign_map.keys())[:50]:
        uc = u(c_i)
        um = u(m_i)
        d = ((um[0] - uc[0]) % 3, (um[1] - uc[1]) % 3)
        if d == (0, 0):
            continue
        w = _f3_omega(uc, d)
        s = _dot(uc, d)
        prod = _f9_mul(uc, _f9_conj(d))
        assert prod == (s, w)
        trials += 1
    print(f"  Verified on {trials} representative keys.")

    # ------------------------------------------------------------------
    # §2. Determinism: (d, dot, omega) determines c0/eps (variable-case)
    # ------------------------------------------------------------------
    print()
    print("§2. Variable-case invariants")
    print("-" * 50)

    det_c0: dict[tuple[int, int, int, int, int], int] = {}
    det_eps: dict[tuple[int, int, int, int, int], int] = {}
    t_ctr = Counter()
    var_ctr = Counter()

    # Also show the constant-line criterion depends only on (d,omega).
    det_const: dict[tuple[int, int, int, int], int] = {}

    for (c_i, m_i, o_i), sgn in sign_map.items():
        uc = u(c_i)
        um = u(m_i)
        uo = u(o_i)
        t = 1 if um == uo else 2
        t_ctr[int(t)] += 1

        d = ((um[0] - uc[0]) % 3, (um[1] - uc[1]) % 3)
        if d == (0, 0):
            raise AssertionError("unexpected: d == 0 for CE2 simple-family sign key")

        w = _f3_omega(uc, d)
        s = _dot(uc, d)
        d1, d2 = int(d[0]), int(d[1])

        const_line = int(d1 != 0 and w == _f3_k_of_direction(d))
        det_key_const = (int(t), d1, d2, int(w))
        if det_key_const in det_const and det_const[det_key_const] != const_line:
            raise AssertionError("constant-line not determined by (t,d,omega)")
        det_const[det_key_const] = const_line

        if const_line:
            continue

        c0 = _eval_f3_sparse_poly(uc[0], uc[1], d1, d2, _SIMPLE_FAMILY_SIGN_C0_TERMS[t])
        e = _eval_f3_sparse_poly(uc[0], uc[1], d1, d2, _SIMPLE_FAMILY_SIGN_EPS_TERMS[t])
        eps = _f3_chi(e)

        key = (int(t), d1, d2, int(w), int(s))
        if key in det_c0 and det_c0[key] != c0:
            raise AssertionError("c0 not determined by (t,d,omega,dot)")
        if key in det_eps and det_eps[key] != eps:
            raise AssertionError("eps not determined by (t,d,omega,dot)")
        det_c0[key] = int(c0)
        det_eps[key] = int(eps)
        var_ctr[int(t)] += 1

        # sanity: the final sign must still match the committed map
        zsum = (z(m_i) + z(o_i)) % 3
        predicted = int(eps) * _f3_chi((zsum + int(c0)) % 3)
        if int(predicted) != int(sgn):
            raise AssertionError(
                "unexpected mismatch: closed-form pieces do not match sign"
            )

    print(f"  Total keys: {len(sign_map)}  split t={dict(t_ctr)}")
    print(f"  Variable-case keys: {sum(var_ctr.values())}  split t={dict(var_ctr)}")
    print(f"  Unique (t,d,omega,dot)->c0 keys: {len(det_c0)}")
    print(f"  Unique (t,d,omega,dot)->eps keys: {len(det_eps)}")
    print("  OK: c0 and eps only depend on bilinear pairings with direction d.")

    # ------------------------------------------------------------------
    # §3. Determinism on the constant line: (d,dot) determines P/sign
    # ------------------------------------------------------------------
    print()
    print("§3. Constant-line invariants")
    print("-" * 50)

    det_p: dict[tuple[int, int, int, int], int] = {}
    det_sign: dict[tuple[int, int, int, int], int] = {}
    const_ctr = Counter()

    for (c_i, m_i, o_i), sgn in sign_map.items():
        uc = u(c_i)
        um = u(m_i)
        uo = u(o_i)
        t = 1 if um == uo else 2

        d = ((um[0] - uc[0]) % 3, (um[1] - uc[1]) % 3)
        d1, d2 = int(d[0]), int(d[1])
        w = _f3_omega(uc, d)
        s = _dot(uc, d)

        const_line = d1 != 0 and w == _f3_k_of_direction(d)
        if not const_line:
            continue

        P = _eval_f3_sparse_poly(
            uc[0], uc[1], d1, d2, _SIMPLE_FAMILY_SIGN_CONST_P_TERMS[t]
        )
        sP = _f3_chi(P)
        assert int(sP) == int(sgn)
        const_ctr[int(t)] += 1

        key = (int(t), d1, d2, int(s))
        if key in det_p and det_p[key] != P:
            raise AssertionError("P not determined by (t,d,dot) on the constant line")
        if key in det_sign and det_sign[key] != int(sP):
            raise AssertionError(
                "sign not determined by (t,d,dot) on the constant line"
            )
        det_p[key] = int(P)
        det_sign[key] = int(sP)

    print(f"  Constant-line keys: {sum(const_ctr.values())}  split t={dict(const_ctr)}")
    print(f"  Unique (t,d,dot)->P keys: {len(det_p)}")
    print(f"  Unique (t,d,dot)->sign keys: {len(det_sign)}")
    print("  OK: constant-line sign depends only on dot(u_c,d) and the direction d.")

    print()
    print("ALL CHECKS PASSED ✓")


if __name__ == "__main__":
    main()
