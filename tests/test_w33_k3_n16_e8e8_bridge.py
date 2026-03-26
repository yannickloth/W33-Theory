from __future__ import annotations

from w33_k3_n16_e8e8_bridge import build_k3_n16_e8e8_bridge_summary


def test_k3_n16_e8e8_bridge_identifies_the_rank16_complement() -> None:
    summary = build_k3_n16_e8e8_bridge_summary()
    theorem = summary["n16_classification_theorem"]

    assert summary["status"] == "ok"
    assert summary["root_representative_count"] == 240
    assert summary["total_root_count"] == 480
    assert summary["root_span_rank"] == 16
    assert summary["root_span_index"] == 1
    assert theorem["n16_has_480_roots"] is True
    assert theorem["root_span_has_full_rank_16"] is True
    assert theorem["root_span_index_is_1"] is True
    assert theorem["root_span_equals_the_full_lattice"] is True
    assert theorem["explicit_n16_is_not_d16_plus"] is True
    assert theorem["explicit_n16_is_e8_plus_e8_by_rank16_even_unimodular_classification"] is True


def test_k3_n16_e8e8_bridge_records_expected_smith_data() -> None:
    summary = build_k3_n16_e8e8_bridge_summary()

    assert summary["root_span_smith_diagonal"] == [1] * 16
    assert summary["sample_root_representatives"][0] == [
        0,
        0,
        2,
        -3,
        -3,
        0,
        -2,
        3,
        -1,
        -3,
        1,
        -2,
        -2,
        0,
        1,
        -2,
    ]
