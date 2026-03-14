from fractions import Fraction

from exploration.w33_weinberg_generator_bridge import build_weinberg_generator_summary


def test_generator_is_exact_weinberg_angle() -> None:
    summary = build_weinberg_generator_summary()
    generator = summary["generator"]
    assert generator["symbol"] == "x"
    assert generator["meaning"] == "sin^2(theta_W)"
    assert generator["exact"]["exact"] == "3/13"
    assert generator["q"] == 3


def test_sm_observables_are_generated_by_x() -> None:
    summary = build_weinberg_generator_summary()
    observables = summary["generated_observables"]
    assert observables["tan_theta_c"]["exact"]["exact"] == "3/13"
    assert observables["sin2_theta_12"]["exact"]["exact"] == "4/13"
    assert observables["sin2_theta_23"]["exact"]["exact"] == "7/13"
    assert observables["sin2_theta_13"]["exact"]["exact"] == "2/91"
    assert observables["omega_lambda"]["exact"]["exact"] == "9/13"
    assert observables["higgs_ratio_square"]["exact"]["exact"] == "14/55"
    for key in (
        "tan_theta_c",
        "sin2_theta_12",
        "sin2_theta_23",
        "sin2_theta_13",
        "omega_lambda",
        "higgs_ratio_square",
    ):
        assert observables[key]["matches_formula"] is True


def test_spectral_and_gravity_observables_are_generated_by_x() -> None:
    summary = build_weinberg_generator_summary()
    observables = summary["generated_observables"]
    assert observables["a2_over_a0"]["exact"]["exact"] == "14/3"
    assert observables["a4_over_a0"]["exact"]["exact"] == "110/3"
    assert observables["discrete_6_mode_over_a0"]["exact"]["exact"] == "26"
    assert observables["discrete_to_continuum_ratio"]["exact"]["exact"] == "39"
    for key in (
        "a2_over_a0",
        "a4_over_a0",
        "discrete_6_mode_over_a0",
        "discrete_to_continuum_ratio",
    ):
        assert observables[key]["matches_formula"] is True


def test_generator_relations_hold_exactly() -> None:
    summary = build_weinberg_generator_summary()
    relations = summary["derived_relations"]
    assert relations["sin2_theta_23_plus_2weinberg_equals_1"] is True
    assert relations["sin2_theta_12_equals_four_thirds_weinberg"] is True
    assert relations["omega_lambda_equals_3weinberg"] is True
    assert relations["cabibbo_equals_weinberg"] is True
    assert relations["gravity_ratio_equals_9_over_weinberg"] is True


def test_reactor_formula_is_rational_in_x() -> None:
    summary = build_weinberg_generator_summary()
    x = Fraction(summary["generator"]["exact"]["exact"])
    reactor = Fraction(summary["generated_observables"]["sin2_theta_13"]["exact"]["exact"])
    assert reactor == Fraction(2, 9) * x * x / (1 - 2 * x)
