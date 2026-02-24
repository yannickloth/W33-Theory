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

    cartan = rep["cartan_like"]
    assert cartan["dim"] == 6
    assert cartan["centralizer_dim"] == 6
    assert cartan["self_centralizing"] is True

