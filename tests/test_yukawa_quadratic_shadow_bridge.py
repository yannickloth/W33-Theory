from exploration.w33_yukawa_quadratic_shadow_bridge import (
    build_yukawa_quadratic_shadow_summary,
)


def test_yukawa_quadratic_shadow_summary():
    summary = build_yukawa_quadratic_shadow_summary()
    theorem = summary["quadratic_shadow_theorem"]

    assert theorem["active_plus_squares_to_central_shadow"] is True
    assert theorem["active_minus_squares_to_central_shadow"] is True
    assert theorem["central_shadow_is_simple_root_commutator"] is True
    assert theorem["universal_nilpotents_are_active_minus_central_shadow"] is True
    assert theorem["central_shadow_equals_common_square_from_family_normal_form"] is True
    assert theorem["first_nonlinear_family_packet_is_quadratic_shadow_of_active_packet"] is True

    packet = summary["normal_form_packet"]
    assert packet["active_plus"] == [[0, 1, 0], [0, 0, 2], [0, 0, 0]]
    assert packet["active_minus"] == [[0, -1, 0], [0, 0, -2], [0, 0, 0]]
    assert packet["central_shadow"] == [[0, 0, 2], [0, 0, 0], [0, 0, 0]]
