from __future__ import annotations

from scripts.ce2_global_cocycle import (
    explain_simple_family_sign_closed_form,
    predict_simple_family_sign,
    explain_predict_ce2_uv,
    predict_ce2_uv,
)


def test_simple_family_sign_explanation_matches_predictor() -> None:
    # pick a few representative triples (c,match,other) in the simple family
    samples = [
        (3, 0, 17),
        (5, 2, 8),
        (10, 4, 1),
    ]
    for c, m, o in samples:
        expl = explain_simple_family_sign_closed_form(c, m, o)
        sign = expl.get("constant_line_rule", {}).get("sign")
        if sign is None:
            sign = expl.get("generic_rule", {}).get("sign")
        assert sign in (-1, 1)
        assert sign == predict_simple_family_sign(c, m, o)


def test_predict_ce2_uv_explanation_consistency() -> None:
    # use the canonical mixed triple from the bridge script
    a = (0, 0)
    b = (17, 1)
    c = (3, 0)

    expl = explain_predict_ce2_uv(a, b, c)
    assert expl.get("available")
    uv = predict_ce2_uv(a, b, c)
    assert uv is not None

    # ensure the ``uv`` lists in the explanation match the actual UV outputs
    def normalize(lst):
        return sorted((int(i), str(v)) for i, v in lst)

    assert normalize(expl["uv"]["U"]) == normalize(uv.U)
    assert normalize(expl["uv"]["V"]) == normalize(uv.V)
