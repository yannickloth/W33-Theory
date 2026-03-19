from __future__ import annotations

from w33_decimal_surface_flag_bridge import build_decimal_surface_flag_summary


def test_decimal_surface_flag_shell_closes_exactly() -> None:
    summary = build_decimal_surface_flag_summary()
    bridge = summary["decimal_surface_dictionary"]
    assert bridge["decimal_generator"] == 10
    assert bridge["decimal_generator_mod_7"] == 3
    assert bridge["decimal_generator_order_mod_7"] == 6
    assert bridge["decimal_square_order_mod_7"] == 3
    assert bridge["genus_denominator"] == 12
    assert bridge["first_toroidal_dual_value"] == 7
    assert bridge["phi6"] == 7
    assert bridge["heawood_vertices"] == 14
    assert bridge["heawood_edges"] == 21
    assert bridge["tetrahedral_fixed_point"] == 4
    assert bridge["shared_six_channel"] == 6
    assert bridge["single_surface_flags"] == 84


def test_decimal_surface_flag_factorizations_hold() -> None:
    summary = build_decimal_surface_flag_summary()
    factors = summary["exact_factorizations"]
    assert factors["decimal_order_equals_shared_six_channel"] is True
    assert factors["first_toroidal_value_equals_phi6"] is True
    assert factors["single_surface_flags_equals_12_times_7"] is True
    assert factors["single_surface_flags_equals_14_times_6"] is True
    assert factors["single_surface_flags_equals_21_times_4"] is True
    assert factors["decimal_order_plus_one_equals_first_toroidal_value"] is True
