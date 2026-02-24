from __future__ import annotations


def test_ce2_simple_family_sign_closed_form_matches_compact_map() -> None:
    # Import inside the test so path injections in the module don't affect
    # collection-time behavior.
    from scripts.ce2_global_cocycle import (
        _simple_family_sign_map,
        predict_simple_family_sign_closed_form,
        predict_simple_family_sign,
    )

    sign_map = _simple_family_sign_map()
    assert len(sign_map) == 864
    for (c_i, match_i, other_i), s in sign_map.items():
        assert predict_simple_family_sign_closed_form(c_i, match_i, other_i) == int(s)
        # also the public wrapper must agree and not raise
        assert predict_simple_family_sign(c_i, match_i, other_i) == int(s)


    # ensure mapping table is never referenced by wrapper (monkeypatch)
    called = False
    def bogus_map(*args, **kwargs):
        nonlocal called
        called = True
        raise RuntimeError("map called")
    from scripts.ce2_global_cocycle import _simple_family_sign_map as orig_map
    try:
        # temporarily replace lookup
        import scripts.ce2_global_cocycle as cg
        cg._simple_family_sign_map = lambda : bogus_map
        for k in _simple_family_sign_map().keys():
            predict_simple_family_sign(*k)
        assert not called, "closed form unexpectedly invoked lookup"
    finally:
        cg._simple_family_sign_map = orig_map
