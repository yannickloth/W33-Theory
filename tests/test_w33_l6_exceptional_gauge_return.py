from w33_l6_exceptional_gauge_return import (
    build_l6_exceptional_gauge_return_certificate,
)


def test_corrected_l6_support_matches_exceptional_dictionary():
    certificate = build_l6_exceptional_gauge_return_certificate()

    assert certificate.total_entry_count == 2457864
    assert certificate.single_entry_count == 2389824
    assert certificate.multi_entry_count == 68040
    assert certificate.full_support_size == 86
    assert certificate.e6_root_support_size == 72
    assert certificate.a2_root_support_size == 6
    assert certificate.cartan_support_size == 8
    assert certificate.e6_uniform_term_count == 29844
    assert certificate.a2_uniform_term_count == 40176
    assert certificate.sorted_cartan_term_counts == (
        44496,
        58752,
        60192,
        60588,
        62032,
        62140,
        63150,
        63504,
    )


def test_corrected_l6_generation_patterns_split_democratic_e6_plus_h_from_asymmetric_a2():
    certificate = build_l6_exceptional_gauge_return_certificate()
    democratic = certificate.democratic_summary
    asymmetric = certificate.asymmetric_summaries

    assert certificate.democratic_pattern == (0, 0, 1, 1, 2, 2)
    assert democratic.entry_count == 2216808
    assert democratic.e6_term_count == 2148768
    assert democratic.a2_term_count == 0
    assert democratic.cartan_term_count == 474854

    assert len(asymmetric) == 6
    assert {summary.pattern for summary in asymmetric} == {
        (0, 0, 0, 1, 1, 2),
        (0, 0, 0, 1, 2, 2),
        (0, 0, 1, 1, 1, 2),
        (0, 0, 1, 2, 2, 2),
        (0, 1, 1, 1, 2, 2),
        (0, 1, 1, 2, 2, 2),
    }
    for summary in asymmetric:
        assert summary.entry_count == 40176
        assert summary.e6_term_count == 0
        assert summary.a2_term_count == 40176
        assert summary.cartan_term_count == 0


def test_corrected_l6_operator_action_splits_into_generation_preserving_e6_h_and_mixing_a2():
    certificate = build_l6_exceptional_gauge_return_certificate()

    assert certificate.e6_generation_preserving is True
    assert certificate.a2_generation_mixing_only is True
    assert certificate.cartan_generation_preserving is True
    assert certificate.full_matter_action_ranks == (72, 6, 8)
    assert certificate.spinor_action_ranks == (40, 6, 8)
    assert certificate.full_matter_total_rank == 86
    assert certificate.spinor_total_rank == 54
    assert "democratic sextuple sector" in certificate.route_interpretation
    assert "six A2 roots" in certificate.route_interpretation
