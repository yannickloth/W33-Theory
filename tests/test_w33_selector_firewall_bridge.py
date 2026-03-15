from exploration.w33_selector_firewall_bridge import build_selector_firewall_summary


def test_selector_firewall_records_nonuniqueness_boundary() -> None:
    data = build_selector_firewall_summary()
    master = data["master_equation"]

    assert master["identity"] == "A^2 + 2A - 8I = 4J"
    assert master["srg_parameters"] == [40, 12, 2, 4]
    assert master["identity_holds_for_canonical_w33"] is True
    assert master["classification_count_for_srg_40_12_2_4"] == 28
    assert master["master_equation_alone_does_not_force_unique_graph"] is True


def test_selector_firewall_records_canonical_selector_package() -> None:
    data = build_selector_firewall_summary()
    selector = data["selector_package"]

    assert selector["canonical_realization"] == "symplectic W(3,3) on PG(3,3)"
    assert selector["gf3_rank_of_adjacency"] == 39
    assert selector["gf3_rank_selector_matches_v_minus_1"] is True
    assert selector["all_neighborhoods_decompose_as_4K3"] is True
    assert selector["neighborhood_component_sizes"] == [3, 3, 3, 3]
    assert selector["symplectic_group_order"] == 51840
    assert selector["symplectic_group_order_exact"] == 51840
