from __future__ import annotations

from collections import Counter


def test_2m12_order3_jordan_signatures_match_between_suz_and_golay() -> None:
    from scripts.w33_2m12_order3_signature_alignment import analyze

    rep = analyze()
    assert rep.get("available") is True

    expected = Counter({(4, 2): 2640, (3, 1): 1760, (0, 0): 1})

    suz = rep.get("suz", {})
    assert isinstance(suz, dict)
    assert int(suz.get("group_order", 0) or 0) == 190_080
    suz_counts = Counter(suz.get("order3_signature_counts", {}))
    assert suz_counts == expected

    golay = rep.get("golay", {})
    assert isinstance(golay, dict)
    assert int(golay.get("group_order", 0) or 0) == 190_080
    golay_counts = Counter(golay.get("order3_signature_counts", {}))
    assert golay_counts == expected

    assert golay_counts == suz_counts

