from __future__ import annotations


def test_sporadic_permrep_suborbit_signatures_match_w33_invariants() -> None:
    from scripts.w33_monster_permrep_suborbit_signatures import analyze

    rep = analyze()
    assert rep.get("available") is True

    w33 = rep.get("w33", {})
    assert isinstance(w33, dict)
    assert int(w33.get("n_incidence_objects", 0) or 0) == 80
    assert int(w33.get("aut_group_order", 0) or 0) == 51840

    he = rep.get("he_2058", {})
    assert isinstance(he, dict)
    hits_he = he.get("signature_hits", {})
    assert isinstance(hits_he, dict)
    assert int(hits_he.get("gcd_nontrivial", 0) or 0) == 17
    assert hits_he.get("has_17x80") is True
    assert hits_he.get("has_17x8") is True
    assert hits_he.get("nontrivial_all_multiples_of_17") is True
    assert int(hits_he.get("nontrivial_sum", 0) or 0) == 2057

    he2 = rep.get("he_29155", {})
    assert isinstance(he2, dict)
    hits_he2 = he2.get("signature_hits", {})
    assert isinstance(hits_he2, dict)
    assert hits_he2.get("has_e4_q2") is True
    assert hits_he2.get("has_trace_l1") is True

    m12_220 = rep.get("m12_220", {})
    assert isinstance(m12_220, dict)
    hits_m12_220 = m12_220.get("signature_hits", {})
    assert isinstance(hits_m12_220, dict)
    assert hits_m12_220.get("has_w33_degree_12") is True
    assert hits_m12_220.get("has_e6_fund_27") is True
    assert hits_m12_220.get("has_4x27") is True

    m12_144 = rep.get("m12_144", {})
    assert isinstance(m12_144, dict)
    sub_m12_144 = m12_144.get("suborbit_lengths", [])
    assert isinstance(sub_m12_144, list)
    assert sum(sub_m12_144) == 144
    assert sub_m12_144 == [1, 11, 11, 55, 66]

    m12_495 = rep.get("m12_495", {})
    assert isinstance(m12_495, dict)
    hits_m12_495 = m12_495.get("signature_hits", {})
    assert isinstance(hits_m12_495, dict)
    assert hits_m12_495.get("has_hodge_eigenvalue_16") is True
    assert hits_m12_495.get("has_su5_adjoint_24") is True
    assert hits_m12_495.get("has_2x24") is True
    assert hits_m12_495.get("has_4x24") is True

    hn = rep.get("hn_1140000", {})
    assert isinstance(hn, dict)
    hits_hn = hn.get("signature_hits", {})
    assert isinstance(hits_hn, dict)
    assert hits_hn.get("has_80x385") is True
    assert hits_hn.get("has_77x2160") is True
    assert hits_hn.get("has_7x_aut_w33") is True
    assert hits_hn.get("has_27x385") is True
    assert hits_hn.get("has_10x81x385") is True
