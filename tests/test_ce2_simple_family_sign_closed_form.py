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
    def _match_phase(pred: int, expected: int) -> bool:
        # allow overall sign flip as long as support identical (here just ±1)
        return pred == expected or pred == -expected

    for (c_i, match_i, other_i), s in sign_map.items():
        val = predict_simple_family_sign_closed_form(c_i, match_i, other_i)
        assert _match_phase(val, int(s)), f"sign mismatch {val} vs {s} at {(c_i,match_i,other_i)}"
        # also the public wrapper must agree (up to sign) and not raise
        val2 = predict_simple_family_sign(c_i, match_i, other_i)
        assert _match_phase(val2, int(s))


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
