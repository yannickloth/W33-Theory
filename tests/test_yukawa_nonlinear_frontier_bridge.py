from exploration.w33_yukawa_nonlinear_frontier_bridge import (
    build_yukawa_nonlinear_frontier_summary,
)


def test_yukawa_nonlinear_frontier_summary():
    summary = build_yukawa_nonlinear_frontier_summary()

    theorem = summary["nonlinear_frontier_theorem"]
    assert theorem["diagonal_l6_bottleneck_is_9_to_10"] is True
    assert theorem["native_mixed_seed_lift_reaches_11_to_12"] is True
    assert theorem["remaining_base_packet_is_two_radical_pairs_plus_scalar_channels"] is True
    assert theorem["remaining_active_packet_is_finite_algebraic_shell"] is True

    rank_lift = summary["native_nonlinear_rank_lift"]
    assert rank_lift["minimal_rank_lift_seed_size"] == 2
    assert rank_lift["minimal_rank_lift_seed_modes"] == [
        [8, 246],
        [8, 247],
        [9, 246],
        [9, 247],
    ]
    assert rank_lift["minimal_full_a2_activation_seed_modes"] == [[8, 9], [246, 247]]
    assert rank_lift["max_response_rank"] == 11
    assert rank_lift["max_augmented_rank"] == 12

    packet = summary["finite_algebraic_packet"]
    assert packet["gram_denominator"] == 57600
    assert packet["exact_scalar_channel_numerators"] == {
        "shared_phi3_mode": 169,
        "h2_plus_minus_companion": 275,
        "hbar2_minus_plus_scalar": 323,
    }
    assert packet["residual_blocks"]["h2_minus_plus"]["discriminant"] == 48964
    assert packet["residual_blocks"]["hbar2_plus_minus"]["discriminant"] == 415396
