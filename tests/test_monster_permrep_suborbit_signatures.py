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

    hn = rep.get("hn_1140000", {})
    assert isinstance(hn, dict)
    hits_hn = hn.get("signature_hits", {})
    assert isinstance(hits_hn, dict)
    assert hits_hn.get("has_80x385") is True
    assert hits_hn.get("has_77x2160") is True
    assert hits_hn.get("has_7x_aut_w33") is True
