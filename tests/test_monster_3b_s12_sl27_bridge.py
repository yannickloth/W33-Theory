from __future__ import annotations


def test_monster_3b_heisenberg_s12_sl27_bridge_identities() -> None:
    from scripts.w33_monster_3b_s12_sl27_bridge import analyze

    rep = analyze()
    assert rep.get("available") is True

    monster = rep.get("monster", {})
    assert isinstance(monster, dict)
    assert monster.get("class") == "3B"
    assert int(monster.get("extraspecial_order", 0) or 0) == 3**13  # 3^{1+12}

    cent = int(monster.get("centralizer_order", 0) or 0)
    cof = int(monster.get("cofactor_2suz_order", 0) or 0)
    assert cent == (3**13) * cof

    heis = rep.get("heisenberg", {})
    assert isinstance(heis, dict)
    assert int(heis.get("p", 0) or 0) == 3
    assert int(heis.get("n", 0) or 0) == 6
    assert int(heis.get("irrep_dim", 0) or 0) == 729

    golay = rep.get("golay", {})
    assert isinstance(golay, dict)
    assert int(golay.get("n_codewords", 0) or 0) == 729
    assert int(golay.get("n_nonzero", 0) or 0) == 728

    golay_lag = rep.get("golay_lagrangian", {})
    assert isinstance(golay_lag, dict)
    assert golay_lag.get("systematic_generator") is True
    assert golay_lag.get("A_symmetric") is True
    assert golay_lag.get("symplectic_isotropic_all_pairs") is True
    assert int(golay_lag.get("max_abelian_subgroup_order", 0) or 0) == 3**7

    A = golay_lag.get("A_matrix_mod3", [])
    assert isinstance(A, list) and len(A) == 6
    assert all(isinstance(r, list) and len(r) == 6 for r in A)
    for i in range(6):
        for j in range(6):
            assert int(A[i][j]) % 3 == int(A[j][i]) % 3

    sl27 = rep.get("sl27", {})
    assert isinstance(sl27, dict)
    assert int(sl27.get("hilbert_dim", 0) or 0) == 27
    assert int(sl27.get("operator_basis_dim", 0) or 0) == 729
    assert int(sl27.get("traceless_dim", 0) or 0) == 728

    sp12 = rep.get("2suz_sp12_embedding", {})
    assert isinstance(sp12, dict)
    assert sp12.get("available") is True
    assert int(sp12.get("field_p", 0) or 0) == 3
    assert int(sp12.get("dim", 0) or 0) == 12
    assert int(sp12.get("invariant_form_nullspace_dim", 0) or 0) == 1
    assert int(sp12.get("invariant_form_rank", 0) or 0) == 12
    assert int(sp12.get("qutrits_n", 0) or 0) == 6
    assert int(sp12.get("heisenberg_irrep_dim", 0) or 0) == 729
