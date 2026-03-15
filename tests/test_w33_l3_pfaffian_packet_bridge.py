from w33_l3_pfaffian_packet_bridge import build_l3_pfaffian_packet_summary


def test_l3_support_and_sign_balance() -> None:
    summary = build_l3_pfaffian_packet_summary()
    l3 = summary["l3_tensor_dictionary"]
    assert l3["support_count"] == 2592
    assert l3["plus_count"] == 1296
    assert l3["minus_count"] == 1296
    assert l3["balanced_signs"] is True
    assert l3["antisymmetric_support_count"] == 2592
    assert l3["all_supported_entries_are_antisymmetric"] is True


def test_all_vector_packets_are_full_rank_skew_packets() -> None:
    summary = build_l3_pfaffian_packet_summary()
    packet = summary["skew_packet_dictionary"]
    assert packet["spinor_dimension"] == 16
    assert packet["vector_directions"] == list(range(17, 27))
    assert packet["all_vector_packets_have_determinant_plus_one"] is True
    assert packet["all_vector_packets_have_full_skew_rank"] is True
    assert packet["all_vector_packets_are_integral_skew_matrices"] is True


def test_three_exact_characteristic_polynomial_archetypes() -> None:
    summary = build_l3_pfaffian_packet_summary()
    archetypes = summary["spectral_archetypes"]
    assert archetypes["archetype_count"] == 3
    assert archetypes["type_a"]["i27_directions"] == [17, 19, 24, 26]
    assert archetypes["type_a"]["characteristic_polynomial"] == "(x**2 + 1)**4*(x**8 + 22*x**6 + 87*x**4 + 26*x**2 + 1)"
    assert archetypes["type_b"]["i27_directions"] == [18, 20, 23, 25]
    assert archetypes["type_b"]["characteristic_polynomial"] == "(x**2 + 1)**4*(x**8 + 22*x**6 + 123*x**4 + 26*x**2 + 1)"
    assert archetypes["democratic_type_c"]["i27_directions"] == [21, 22]
    assert archetypes["democratic_type_c"]["characteristic_polynomial"] == "(x**2 + 1)**8"


def test_democratic_packet_is_exact_higgs_pair() -> None:
    summary = build_l3_pfaffian_packet_summary()
    higgs = summary["higgs_packet_bridge"]
    assert higgs["democratic_directions"] == [21, 22]
    assert higgs["democratic_labels"] == ["H", "Hbar"]
    assert higgs["democratic_characteristic_polynomial"] == "(x**2 + 1)**8"
    assert higgs["democratic_packet_is_exactly_higgs_higgsbar"] is True
    assert higgs["remaining_directions_are_nondemocratic_quartic_packets"] is True
    assert higgs["remaining_direction_labels"] == ["H", "Hbar", "T", "T", "T", "Tbar", "Tbar", "Tbar"]
