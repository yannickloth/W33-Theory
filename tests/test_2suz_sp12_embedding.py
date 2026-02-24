from __future__ import annotations


def test_2suz_gf3_dim12_embeds_in_sp12() -> None:
    from scripts.w33_2suz_sp12_embedding import analyze

    rep = analyze()
    assert rep.get("available") is True
    assert int(rep.get("field_p", 0) or 0) == 3
    assert int(rep.get("dim", 0) or 0) == 12

    inv = rep.get("invariant_form", {})
    assert isinstance(inv, dict)
    assert tuple(inv.get("linear_system_shape", ())) == (132, 66)
    assert int(inv.get("nullspace_dim", 0) or 0) == 1
    assert int(inv.get("rank", 0) or 0) == 12

    J = inv.get("J_mod3", [])
    assert isinstance(J, list) and len(J) == 12
    assert all(isinstance(r, list) and len(r) == 12 for r in J)
    for i in range(12):
        assert int(J[i][i]) % 3 == 0
        for j in range(12):
            assert (int(J[i][j]) + int(J[j][i])) % 3 == 0  # alternating

    std = rep.get("standardized_generators", {})
    assert isinstance(std, dict)
    assert std.get("A_std_preserves_J0") is True
    assert std.get("B_std_preserves_J0") is True

    sig = rep.get("standard_generator_signature", {})
    assert isinstance(sig, dict)
    assert int(sig.get("ord_A", 0) or 0) == 4
    assert int(sig.get("ord_B", 0) or 0) == 3
    assert int(sig.get("ord_AB", 0) or 0) == 13
    assert sig.get("A_squared_is_minus_I") is True
