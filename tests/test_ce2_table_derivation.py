from __future__ import annotations


def test_derive_simple_family_tables_matches_constants() -> None:
    """Normal-form and delta machinery agree with the live CE2 closed form.

    The older direct-fit proof via raw sign buckets is no longer the active
    theorem. The current exact statement is:
      - the simple-family sign is recovered from the seed plus delta law
      - the returned normal-form tables agree with the delta corrections
      - variable-branch phase is determined by the bilinear invariants
    """
    from scripts.ce2_global_cocycle import (
        _derive_simple_family_tables,
        _simple_family_sign_map,
        _heisenberg_vec_maps,
        _f3_omega,
        _f3_dot,
        _f3_k_of_direction,
        _eval_f3_poly_sw,
        _f3_chi,
        _derive_naive_tables,
        predict_simple_family_phase_closed_form,
        predict_simple_family_sign_closed_form,
        predict_simple_family_sign_from_seed_with_delta,
    )

    e_tables, c0_tables, const_tables = _derive_simple_family_tables()
    sign_map = _simple_family_sign_map()

    # now exercise the new normal-form derivation directly
    from scripts.ce2_global_cocycle import (
        _derive_tables_via_normal_form,
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

    # verify both exact predictors reproduce the committed sign map, and the
    # variable-branch phase is determined by the bilinear invariants.
    phase_by_bucket: dict[tuple[int, tuple[int, int], int, int], int] = {}
    e6id_to_vec, _ = _heisenberg_vec_maps()
    for key, expected in sign_map.items():
        rec = predict_simple_family_sign_from_seed_with_delta(*key)
        assert rec == expected, ("delta prediction mismatch", key, rec, expected)
        assert predict_simple_family_sign_closed_form(*key) == expected

        c_i, match_i, other_i = key
        uc1, uc2, _ = e6id_to_vec[int(c_i)]
        um1, um2, _ = e6id_to_vec[int(match_i)]
        uo1, uo2, _ = e6id_to_vec[int(other_i)]
        t = 1 if (int(um1), int(um2)) == (int(uo1), int(uo2)) else 2
        d = ((int(um1) - int(uc1)) % 3, (int(um2) - int(uc2)) % 3)
        w = int(_f3_omega((uc1, uc2), d))
        s = int(_f3_dot((uc1, uc2), d))
        constant_line = (d[0] != 0) and (w == _f3_k_of_direction(d))
        if constant_line:
            assert int(const_tables[t][d][s]) in (-1, 1)
            continue
        phase = int(predict_simple_family_phase_closed_form(*key))
        bucket = (int(t), d, w, s)
        if bucket in phase_by_bucket:
            assert phase_by_bucket[bucket] == phase
        phase_by_bucket[bucket] = phase

    assert len(phase_by_bucket) > 0
