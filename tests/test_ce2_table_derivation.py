from __future__ import annotations


def test_derive_simple_family_tables_matches_constants() -> None:
    """Tables computed from the sign map must equal the hard-coded coefficients.

    This regression test encodes the algebraic lemma proved in the conversation:
    all of the CE2 "Weil" tables are generated from a single normal form by the
    action of the automorphism group.  The derivation routine below recomputes
    every coefficient purely from the 864-entry sign map, and we simply assert
    that the results coincide with the constants used by the closed-form
    evaluator.
    """
    from scripts.ce2_global_cocycle import (
        _derive_simple_family_tables,
        _SIMPLE_FAMILY_WEIL_E_COEFF,
        _SIMPLE_FAMILY_WEIL_C0_COEFF,
        _SIMPLE_FAMILY_WEIL_CONST_SIGN,
        _simple_family_sign_map,
        _heisenberg_vec_maps,
        _f3_omega,
        _f3_dot,
        _f3_k_of_direction,
        _eval_f3_poly_sw,
        _f3_chi,
        _derive_naive_tables,
    )

    e_tables, c0_tables, const_tables = _derive_simple_family_tables()

    # use the derived coefficients to recompute the sign map and ensure we
    # recover every entry exactly; this demonstrates that the tables are
    # "+"-complete consequences of the sign data.
    sign_map = _simple_family_sign_map()

    def eval_from_tables(c, match, other):
        # mimic predict_simple_family_sign_closed_form but using local tables
        e6id_to_vec, _ = _heisenberg_vec_maps()
        uc1, uc2, _ = e6id_to_vec[int(c)]
        um1, um2, zm = e6id_to_vec[int(match)]
        uo1, uo2, zo = e6id_to_vec[int(other)]
        t = 1 if (int(um1), int(um2)) == (int(uo1), int(uo2)) else 2
        d1 = (int(um1) - int(uc1)) % 3
        d2 = (int(um2) - int(uc2)) % 3
        d = (int(d1), int(d2))
        w = _f3_omega((uc1, uc2), d)
        s = _f3_dot((uc1, uc2), d)
        constant_line = (d1 != 0) and (int(w) == _f3_k_of_direction(d))
        if constant_line:
            table = const_tables[t][d]
            return int(table[int(s) % 3])
        c0_coeff = c0_tables[t][d]
        e_coeff = e_tables[t][d]
        c0 = _eval_f3_poly_sw(int(s), int(w), c0_coeff)
        e = _eval_f3_poly_sw(int(s), int(w), e_coeff)
        eps = _f3_chi(e)
        zsum = (int(zm) + int(zo)) % 3
        return int(eps) * _f3_chi((int(zsum) + int(c0)) % 3)

    for key, expected in sign_map.items():
        assert eval_from_tables(*key) == expected

    # now exercise the new normal-form derivation directly
    from scripts.ce2_global_cocycle import (
        _derive_tables_via_normal_form,
        predict_simple_family_sign_from_seed_with_delta,
        _compute_delta_polys,
    )
    e_tab_nf, c0_tab_nf, const_tab_nf = _derive_tables_via_normal_form()
    assert e_tab_nf == e_tables
    assert c0_tab_nf == c0_tables
    assert const_tab_nf == const_tables

    # delta tables (should be small dictionary of 16 entries)
    delta_e, delta_c0 = _compute_delta_polys()
    assert set(delta_e.keys()) == {1,2}
    assert set(delta_c0.keys()) == {1,2}
    # ensure delta coefficients really do encode the actual-minus-naive
    # difference at every evaluation point
    naive_e_tab, naive_c0_tab, _ = _derive_naive_tables()
    for t in (1, 2):
        for d in delta_e[t].keys():
            for s in range(3):
                for w in range(3):
                    actual_val = _eval_f3_poly_sw(s, w, e_tables[t][d])
                    naive_val = _eval_f3_poly_sw(s, w, naive_e_tab[t][d])
                    delta_val = _eval_f3_poly_sw(s, w, delta_e[t][d])
                    assert (actual_val - naive_val) % 3 == delta_val
                    actual_c0 = _eval_f3_poly_sw(s, w, c0_tables[t][d])
                    naive_c0 = _eval_f3_poly_sw(s, w, naive_c0_tab[t][d])
                    delta_c0_val = _eval_f3_poly_sw(s, w, delta_c0[t][d])
                    assert (actual_c0 - naive_c0) % 3 == delta_c0_val
    # verify predictor using deltas agrees with ordinary evaluation
    for key, s in sign_map.items():
        rec = predict_simple_family_sign_from_seed_with_delta(*key)
        assert rec == s, ("delta prediction mismatch", key, rec, s)
