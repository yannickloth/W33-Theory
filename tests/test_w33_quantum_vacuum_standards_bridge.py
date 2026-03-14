from __future__ import annotations

from w33_quantum_vacuum_standards_bridge import build_quantum_vacuum_standards_summary


def test_quantum_standards_close_exactly() -> None:
    summary = build_quantum_vacuum_standards_summary()
    standards = summary["exact_quantum_standards"]

    assert standards["von_klitzing_constant"]["formula"] == "h / e^2"
    assert standards["josephson_constant"]["formula"] == "2 e / h"
    assert standards["conductance_quantum"]["formula"] == "2 e^2 / h"
    assert standards["flux_quantum"]["formula"] == "h / (2 e)"
    assert standards["phi0_times_kj"]["exact"] == "1"
    assert standards["rk_times_g0"]["exact"] == "2"
    assert standards["kj_squared_rk_h"]["exact"] == "4"
    assert standards["flux_quantum_inverse_is_josephson"] is True
    assert standards["conductance_quantum_is_two_over_rk"] is True
    assert standards["josephson_von_klitzing_triangle_closes"] is True


def test_vacuum_transport_dictionary_is_exact() -> None:
    summary = build_quantum_vacuum_standards_summary()
    bridge = summary["vacuum_transport_dictionary"]

    assert bridge["z0_equals_2_alpha_rk"] is True
    assert bridge["mu0_equals_2_alpha_rk_over_c"] is True
    assert bridge["epsilon0_equals_one_over_2_alpha_rk_c"] is True
    assert bridge["y0_equals_g0_over_4alpha"] is True
    assert bridge["alpha_from_z0_over_2rk"]["exact"] == "1111/152247"
    assert bridge["alpha_from_z0_g0_over_4"]["exact"] == "1111/152247"
    assert bridge["z0_times_g0"]["exact"] == "4444/152247"
    assert bridge["z0_times_g0_equals_4alpha"] is True
    assert bridge["rk_over_z0"]["exact"] == "152247/2222"
    assert bridge["rk_over_z0_equals_one_over_2alpha"] is True
    assert bridge["vacuum_unity"]["exact"] == "1"


def test_quantum_standard_values_have_expected_si_prefixes() -> None:
    summary = build_quantum_vacuum_standards_summary()
    standards = summary["exact_quantum_standards"]

    assert standards["von_klitzing_constant"]["scientific"].startswith("2.58128074593045066600455")
    assert standards["josephson_constant"]["scientific"].startswith("4.83597848416983632447658")
    assert standards["conductance_quantum"]["scientific"].startswith("7.74809172986365064668082")
    assert standards["flux_quantum"]["scientific"].startswith("2.06783384846192932308111")
