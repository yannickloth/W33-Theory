from scripts.w33_golay_lie_algebra import analyze


def test_golay_lie_algebra_core_invariants():
    rep = analyze(compute_derivations=True)
    assert rep.get("available") is True
    assert rep["field_p"] == 3
    assert rep["dim"] == 24

    assert rep["bracket"]["nonzero_pairs"] == 432

    lie = rep["lie"]
    assert lie["jacobi_holds"] is True
    assert lie["perfect"] is True
    assert lie["center_dim"] == 0
    assert lie["killing_form_rank_mod3"] == 0

    deriv = rep["derivations"]
    assert deriv is not None
    assert deriv["dim_derivations"] == 33
    assert deriv["dim_inner"] == 24
    assert deriv["dim_outer"] == 9

    normal_form = rep["normal_form"]
    assert normal_form["available"] is True
    assert normal_form["phi_is_zero"] is True
    assert normal_form["c_addition_holds"] is True

    tensor = rep["tensor_decomposition"]
    l0 = tensor["l0_slice"]
    assert l0["available"] is True
    assert l0["dim"] == 8
    assert l0["lie"]["center_dim"] == 0
    assert l0["lie"]["killing_form_rank_mod3"] == 0
    assert l0["derivations"]["dim_derivations"] == 10
    assert l0["derivations"]["dim_inner"] == 8
    assert l0["derivations"]["dim_outer"] == 2

    fiber = tensor["fiber_algebra"]
    assert fiber["available"] is True
    assert fiber["dim"] == 3
    assert fiber["dim_derivations"] == 3

    deriv_decomp = tensor["derivation_decomposition"]
    assert deriv_decomp["available"] is True
    assert deriv_decomp["constructed_outer_dim"] == 9
    assert deriv_decomp["constructed_outer_components"]["outer_l0_tensor_A"] == 6
    assert deriv_decomp["constructed_outer_components"]["centroid_l0_tensor_derA"] == 3
    assert deriv_decomp["span_is_all_derivations"] is True

    cartan = rep["cartan_like"]
    assert cartan["dim"] == 6
    assert cartan["centralizer_dim"] == 6
    assert cartan["self_centralizing"] is True

    # Strengthen: the c=0 slice L0 is exactly the "Pauli commutator" algebra on
    # the 8 nonzero grades g∈F3^2\{0} with bracket [e_g,e_h]=omega(g,h)e_{g+h}.
    from scripts.w33_golay_lie_algebra import build_golay_lie_algebra, omega

    alg = build_golay_lie_algebra()
    l0_slice = [3 * i for i in range(8)]
    grade_to_slice = {tuple(alg.grades[i]): int(i) for i in l0_slice}
    assert len(grade_to_slice) == 8

    def add(g, h):
        return ((int(g[0]) + int(h[0])) % 3, (int(g[1]) + int(h[1])) % 3)

    for i in l0_slice:
        gi = tuple(alg.grades[i])
        for j in l0_slice:
            gj = tuple(alg.grades[j])
            c_exp = int(omega(gi, gj)) % 3
            if c_exp == 0:
                assert int(alg.bracket_c[i, j]) == 0
                continue
            gsum = add(gi, gj)
            assert gsum != (0, 0)
            assert int(alg.bracket_c[i, j]) % 3 == c_exp
            assert int(alg.bracket_k[i, j]) == grade_to_slice[gsum]
