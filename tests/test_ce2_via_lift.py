from __future__ import annotations


def test_consistency_of_symplectic_lift() -> None:
    """Ensure that transporting by a lift leaves the CE2 sign unchanged.

    This test exercises ``predict_simple_family_sign_via_lift`` added in the
    previous step.  The existence of such a routine is the precise algebraic
    bridge between CE2 and the symplectic/Heisenberg framework: it shows that
    evaluating the metaplectic-corrected action on the Heisenberg coordinates
    reproduces the same sign as the closed-form rule in the original basis.
    """
    from scripts.ce2_global_cocycle import (
        _simple_family_sign_map,
        predict_simple_family_sign,
        predict_simple_family_sign_via_lift,
    )

    sign_map = _simple_family_sign_map()
    assert len(sign_map) == 864

    for key, s in sign_map.items():
        orig = predict_simple_family_sign(*key)
        lifted = predict_simple_family_sign_via_lift(*key)
        assert orig == lifted
