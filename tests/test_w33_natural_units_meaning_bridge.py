from __future__ import annotations

import pytest

from w33_natural_units_meaning_bridge import build_natural_units_meaning_summary


def test_heaviside_lorentz_natural_unit_dictionary_closes() -> None:
    summary = build_natural_units_meaning_summary()
    bridge = summary["heaviside_lorentz_natural_units"]

    assert bridge["convention"] == "hbar = c = epsilon0 = mu0 = Z0 = Y0 = 1"
    assert bridge["alpha_formula"] == "e_HL^2 / (4 pi)"
    assert bridge["electric_charge_squared_symbolic"] == "4 pi alpha"
    assert bridge["von_klitzing_symbolic"] == "1 / (2 alpha)"
    assert bridge["conductance_quantum_symbolic"] == "4 alpha"
    assert bridge["josephson_symbolic"] == "2 sqrt(alpha / pi)"
    assert bridge["flux_quantum_symbolic"] == "1 / (2 sqrt(alpha / pi))"
    assert bridge["vacuum_unity_becomes_unit_element"] is True
    assert bridge["z0_equals_2alpha_rk_becomes_unit_identity"] is True
    assert bridge["alpha_equals_g0_over_4"] is True
    assert bridge["rk_times_g0_equals_2"] is True
    assert bridge["phi0_times_kj_equals_1"] is True


def test_heaviside_lorentz_natural_values_match_expected_numbers() -> None:
    summary = build_natural_units_meaning_summary()
    bridge = summary["heaviside_lorentz_natural_units"]

    assert bridge["electric_charge_squared"] == pytest.approx(0.09170123386702556)
    assert bridge["electric_charge"] == pytest.approx(0.30282211588162705)
    assert bridge["von_klitzing_constant"] == pytest.approx(68.51800180018002)
    assert bridge["conductance_quantum"] == pytest.approx(0.029189409315126078)
    assert bridge["josephson_constant"] == pytest.approx(0.09639127324021538)
    assert bridge["flux_quantum"] == pytest.approx(10.374383140555823)


def test_gaussian_crosscheck_and_dimensionless_graph_dictionary() -> None:
    summary = build_natural_units_meaning_summary()
    gaussian = summary["gaussian_crosscheck"]
    graph = summary["dimensionless_graph_observables"]

    assert gaussian["alpha_formula"] == "e_G^2"
    assert gaussian["electric_charge_squared"] == pytest.approx(0.0072973523287815195)
    assert gaussian["electric_charge"] == pytest.approx(0.08542454172415279)
    assert gaussian["heaviside_equals_4pi_gaussian"] is True

    assert graph["alpha_inverse"]["exact"] == "152247/1111"
    assert graph["alpha"]["exact"] == "1111/152247"
    assert graph["weinberg_x"] == "3/13"
    assert graph["theta12"] == "4/13"
    assert graph["theta23"] == "7/13"
    assert graph["theta13"] == "2/91"
    assert graph["higgs_ratio_square"] == "14/55"
    assert graph["omega_lambda"] == "9/13"
    assert graph["a2_over_a0"] == "14/3"
    assert graph["a4_over_a0"] == "110/3"
    assert graph["discrete_to_continuum_ratio"] == "39"
    assert graph["topological_over_continuum"] == "7"
    assert graph["si_vacuum_is_reexpression_of_dimensionless_package"] is True
    assert graph["graphs_mean_couplings_and_mode_weights_in_natural_units"] is True
    assert graph["quantum_vacuum_standards_bridge_is_compatible"] is True
