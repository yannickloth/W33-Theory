from __future__ import annotations


def test_ce2_simple_family_sign_closed_form_matches_compact_map() -> None:
    # Import inside the test so path injections in the module don't affect
    # collection-time behavior.
    from scripts.ce2_global_cocycle import (
        _simple_family_sign_map,
        predict_simple_family_sign_closed_form,
    )

    sign_map = _simple_family_sign_map()
    assert len(sign_map) == 864
    for (c_i, match_i, other_i), s in sign_map.items():
        assert predict_simple_family_sign_closed_form(c_i, match_i, other_i) == int(s)
