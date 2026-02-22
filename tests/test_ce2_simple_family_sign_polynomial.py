from __future__ import annotations


def test_ce2_simple_family_sign_polynomial_matches_compact_map() -> None:
    # Import inside the test so path injections in the module don't affect
    # collection-time behavior.
    from scripts.ce2_global_cocycle import (
        _simple_family_sign_map,
        _simple_family_sign_poly_coeff_mask,
        predict_simple_family_sign,
    )

    coeff_mask = _simple_family_sign_poly_coeff_mask()
    assert coeff_mask is not None, "missing committed GF(2) sign polynomial artifact"

    # The fitted polynomial should be substantially smaller than the 864-entry table.
    assert int(coeff_mask).bit_count() <= 1000

    sign_map = _simple_family_sign_map()
    assert len(sign_map) == 864
    for (c_i, match_i, other_i), s in sign_map.items():
        assert predict_simple_family_sign(c_i, match_i, other_i) == int(s)
