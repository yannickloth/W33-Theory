import math

from w33_balanced_triplet_background import (
    build_balanced_triplet_background_summary,
    balanced_triplet_family_member,
)


def test_n3_balanced_triplet_member_has_expected_support_and_triplet_pairs():
    member = balanced_triplet_family_member(3)

    assert member.family_coeffs == (1, -3, -3, 3, 3)
    assert member.heavy_background_rank == 4
    assert member.total_quark_support == 36
    assert member.total_lepton_support == 4
    assert member.up_quark_support == 18
    assert member.down_quark_support == 18
    assert member.up_quark_rank == 2
    assert member.down_quark_rank == 2
    assert member.up_triplet_pairs == (
        (6, 3),
        (6, 4),
        (6, 5),
        (7, 3),
        (7, 4),
        (7, 5),
        (8, 3),
        (8, 4),
        (8, 5),
    )
    assert member.down_triplet_pairs == member.up_triplet_pairs
    assert math.isclose(member.full_quark_residual_total, 5.880336463872578)
    assert math.isclose(member.quark_frobenius_total, 0.6415087558673189)
    assert math.isclose(member.normalized_full_quark_ratio, 9.166416529923074)


def test_balanced_triplet_family_through_n6_improves_normalized_full_screen_ratio():
    summary = build_balanced_triplet_background_summary()

    assert summary.family_line == "S : H_2 : Hbar_2 : T : Tbar = 1 : -n : -n : n : n"
    assert summary.scanned_scales == (1, 2, 3, 4, 5, 6)
    assert summary.baseline_background_coeffs == (3, -3, -2)
    assert summary.baseline_total_quark_support == 32
    assert summary.baseline_total_lepton_support == 4
    assert math.isclose(summary.baseline_normalized_full_quark_ratio, 10.445071779480108)

    ratios = [member.normalized_full_quark_ratio for member in summary.members]
    assert ratios == sorted(ratios, reverse=True)
    assert summary.best_scale_within_scan == 6
    assert summary.best_member.family_coeffs == (1, -6, -6, 6, 6)
    assert summary.best_member.total_quark_support == 36
    assert summary.best_member.total_lepton_support == 4
    assert math.isclose(summary.best_member.normalized_full_quark_ratio, 9.064843074221375)
    assert math.isclose(summary.improvement_factor_over_baseline, 1.1522617318311699)


def test_balanced_triplet_family_does_not_open_a_full_clean_quark_nullspace():
    summary = build_balanced_triplet_background_summary()
    assert summary.full_screen_nullity == 0
