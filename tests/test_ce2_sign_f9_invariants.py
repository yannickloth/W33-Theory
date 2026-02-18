from __future__ import annotations


def test_ce2_sign_depends_only_on_f9_bilinear_invariants() -> None:
    """Regression: the CE2 closed-form pieces depend only on bilinear invariants.

    This is a structural simplification:
      - variable-case: (t, d, omega(u_c,d), dot(u_c,d)) determines (c0, eps)
      - constant-line: (t, d, dot(u_c,d)) determines the sign
    """
    from scripts.ce2_global_cocycle import (
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

    sign_map = _simple_family_sign_map()
    e6id_to_vec, _ = _heisenberg_vec_maps()

    def u(e6id: int) -> tuple[int, int]:
        vec = e6id_to_vec[int(e6id)]
        return (int(vec[0]) % 3, int(vec[1]) % 3)

    def dot(u1: tuple[int, int], u2: tuple[int, int]) -> int:
        return (int(u1[0]) * int(u2[0]) + int(u1[1]) * int(u2[1])) % 3

    var_c0: dict[tuple[int, int, int, int, int], int] = {}
    var_eps: dict[tuple[int, int, int, int, int], int] = {}
    const_sign: dict[tuple[int, int, int, int], int] = {}

    for (c_i, m_i, o_i), sgn in sign_map.items():
        uc = u(c_i)
        um = u(m_i)
        uo = u(o_i)
        t = 1 if um == uo else 2

        d1 = (int(um[0]) - int(uc[0])) % 3
        d2 = (int(um[1]) - int(uc[1])) % 3
        assert (d1, d2) != (0, 0)
        d = (int(d1), int(d2))

        w = int(_f3_omega(uc, d))
        s = int(dot(uc, d))

        const_line = int(d1 != 0 and w == int(_f3_k_of_direction(d)))
        if const_line:
            P = _eval_f3_sparse_poly(
                uc[0], uc[1], d1, d2, _SIMPLE_FAMILY_SIGN_CONST_P_TERMS[t]
            )
            pred = int(_f3_chi(P))
            assert pred == int(sgn)

            key = (int(t), int(d1), int(d2), int(s))
            if key in const_sign:
                assert const_sign[key] == pred
            const_sign[key] = int(pred)
            continue

        c0 = _eval_f3_sparse_poly(uc[0], uc[1], d1, d2, _SIMPLE_FAMILY_SIGN_C0_TERMS[t])
        e = _eval_f3_sparse_poly(uc[0], uc[1], d1, d2, _SIMPLE_FAMILY_SIGN_EPS_TERMS[t])
        eps = int(_f3_chi(e))

        key = (int(t), int(d1), int(d2), int(w), int(s))
        if key in var_c0:
            assert var_c0[key] == int(c0)
        if key in var_eps:
            assert var_eps[key] == int(eps)
        var_c0[key] = int(c0)
        var_eps[key] = int(eps)

    assert len(var_c0) > 0 and len(var_eps) > 0 and len(const_sign) > 0
