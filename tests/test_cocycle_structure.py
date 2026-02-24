from __future__ import annotations


def test_golay_phi_normal_form_is_trivial() -> None:
    from scripts.w33_golay_lie_algebra import _phi_normal_form, build_golay_lie_algebra

    alg = build_golay_lie_algebra()
    nf = _phi_normal_form(alg)
    assert nf.get("available") is True
    assert nf.get("phi_is_zero") is True
    assert nf.get("phi_values_distinct") == [0]
    for v in nf.get("phi_const_by_grade_pair", {}).values():
        assert int(v) == 0


def test_golay_fiber_index_addition_holds() -> None:
    from scripts.w33_golay_lie_algebra import _phi_normal_form, build_golay_lie_algebra

    alg = build_golay_lie_algebra()
    nf = _phi_normal_form(alg)
    assert nf.get("available") is True
    assert nf.get("c_addition_holds") is True
