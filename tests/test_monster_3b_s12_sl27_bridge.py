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

    sl27 = rep.get("sl27", {})
    assert isinstance(sl27, dict)
    assert int(sl27.get("hilbert_dim", 0) or 0) == 27
    assert int(sl27.get("operator_basis_dim", 0) or 0) == 729
    assert int(sl27.get("traceless_dim", 0) or 0) == 728

