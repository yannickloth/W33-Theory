from __future__ import annotations


def test_suz_contains_m12_2_by_atlas_words() -> None:
    from scripts.w33_2suz_m12_2_subgroup import analyze

    rep = analyze(compute_orders=True)
    assert rep.get("available") is True

    orders = rep.get("orders", {})
    assert isinstance(orders, dict)
    # The preimage of M12:2 inside 2.Suz has order 2*|M12:2| = 380,160.
    assert int(orders.get("full_order", 0) or 0) == 380_160
    # The derived subgroup projects to M12, so its preimage should be 2.M12 (order 190,080).
    assert int(orders.get("derived_order", 0) or 0) == 190_080
    assert int(orders.get("projective_order_div2", 0) or 0) == 190_080

    # Canonical polarization: commutant of <y, y^x> has dim 2 with a non-scalar involution
    # splitting F3^12 into two Lagrangians swapped by x (Fourier swap).
    pol = rep.get("polarization", {})
    assert isinstance(pol, dict)
    assert int(pol.get("commutant_dim", 0) or 0) == 2
    assert pol.get("found_involution") is True
    assert pol.get("involution_is_scalar") is False
    assert pol.get("involution_squares_to_I") is True
    assert pol.get("eigenspace_dims") == {"+1": 6, "-1": 6}
    assert pol.get("plus_isotropic") is True
    assert pol.get("minus_isotropic") is True
    assert pol.get("x_conjugates_J_to_minus_J") is True
    swap = pol.get("swap_blocks", {})
    assert isinstance(swap, dict)
    assert swap.get("AB_equals_minus_I") is True
    assert swap.get("BA_equals_minus_I") is True

    # Cross-bridge: the Monster 11A -> Golay monomial lift also yields 2.M12 of order 190,080.
    from scripts.monomial_utils import find_sign_lifts_for_group, monomial_group_order
    from scripts.w33_monster_11a_m12_golay_bridge import analyze as analyze_11a
    from tools.s12_universal_algebra import enumerate_linear_code_f3, ternary_golay_generator_matrix

    rep11 = analyze_11a(compute_monomial_order=False)
    assert rep11.get("available") is True
    golay = rep11.get("golay", {})
    assert isinstance(golay, dict)

    gens = golay.get("m12_generators_in_code_coords", {})
    assert isinstance(gens, dict)
    perms = [
        tuple(int(x) for x in gens["b11_code_perm"]),
        tuple(int(x) for x in gens["b21_code_perm"]),
    ]

    gen = ternary_golay_generator_matrix()
    generator_rows = [tuple(int(x) % 3 for x in row) for row in gen]
    code_set = set(enumerate_linear_code_f3(gen))
    lifts = find_sign_lifts_for_group(perms, generator_rows, code_set)
    assert lifts is not None
    mon_order = monomial_group_order(list(zip(perms, lifts)))
    assert int(mon_order) == int(orders["derived_order"])
