from __future__ import annotations

from scripts.ce2_global_cocycle import (
    predict_dual_diagonal_fiber_family_uvw,
    predict_dual_g1g2g2_uvw,
    predict_dual_missing_focus_u_family_uvw,
    predict_dual_origin_line_w_family_uvw,
    predict_dual_origin_same_fiber_uv_family_uvw,
    predict_dual_origin_line_v_family_uvw,
    explain_simple_family_sign_closed_form,
    predict_simple_family_sign,
    explain_predict_ce2_uv,
    predict_ce2_uv,
)


def _decode_e6(entries):
    return sorted((int(i) // 27, int(i) % 27, str(v)) for i, v in entries)


def _decode_g1(entries):
    return sorted(((int(i) - 738) // 3, (int(i) - 738) % 3, str(v)) for i, v in entries)


def _decode_sparse(entries):
    out = []
    for i, v in entries:
        idx = int(i)
        if idx < 729:
            out.append(("e6", idx // 27, idx % 27, str(v)))
        elif idx < 738:
            j = idx - 729
            out.append(("sl3", j // 3, j % 3, str(v)))
        elif idx < 819:
            j = idx - 738
            out.append(("g1", j // 3, j % 3, str(v)))
        else:
            j = idx - 819
            out.append(("g2", j // 3, j % 3, str(v)))
    return sorted(out)


def test_simple_family_sign_explanation_matches_predictor() -> None:
    # pick a few representative triples (c,match,other) in the simple family
    samples = [
        (3, 0, 17),
        (5, 2, 8),
        (10, 4, 1),
    ]
    for c, m, o in samples:
        expl = explain_simple_family_sign_closed_form(c, m, o)

        # tag and pattern should be present and well-formed
        tag = expl.get("tag")
        assert isinstance(tag, (list, tuple)) and len(tag) == 3
        pattern = expl.get("pattern")
        assert isinstance(pattern, (list, tuple)) and len(pattern) == 3
        assert all(s in (-1, 1) for s in pattern)

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


def test_simple_family_tag_helper_consistency() -> None:
    from scripts.ce2_global_cocycle import compute_simple_family_tag
    # pick a random sample and ensure tag matches explanation
    c, m, o = 3, 0, 17
    expl = explain_simple_family_sign_closed_form(c, m, o)
    tag1 = tuple(expl.get("tag"))
    tag2 = compute_simple_family_tag(c, m, o)
    assert tag1 == tag2
    # ensure pattern from explanation is one of the 8 allowed
    patt = expl.get("pattern")
    assert patt in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]


def test_predict_dual_diagonal_fiber_family_uvw() -> None:
    uvw = predict_dual_diagonal_fiber_family_uvw((4, 1), (4, 1), (25, 0))
    assert uvw is not None
    assert uvw.U == []
    assert uvw.V == []
    assert sorted((int(i), str(v)) for i, v in uvw.W) == [
        (700, "1/108"),
        (729, "1/108"),
    ]


def test_predict_dual_same_e6id_fiber_family_uvw() -> None:
    uvw = predict_dual_g1g2g2_uvw((4, 1), (4, 2), (25, 1))
    assert uvw is not None
    assert uvw.U == []
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (133, "1/54"),
    ]


def test_predict_dual_missing_focus_u_family_uvw() -> None:
    uvw = predict_dual_missing_focus_u_family_uvw((0, 0), (1, 0), (15, 1))
    assert uvw is not None
    assert uvw.V == []
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (809, "1/54"),
    ]


def test_predict_dual_missing_focus_u_family_sign_flip() -> None:
    uvw = predict_dual_g1g2g2_uvw((0, 0), (1, 0), (15, 2))
    assert uvw is not None
    assert uvw.V == []
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (808, "-1/54"),
    ]


def test_predict_dual_missing_focus_u_family_focus_orientation() -> None:
    uvw = predict_dual_g1g2g2_uvw((0, 2), (9, 2), (4, 0))
    assert uvw is not None
    assert uvw.V == []
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (814, "-1/54"),
    ]


def test_predict_dual_origin_line_w_family_uvw() -> None:
    uvw = predict_dual_origin_line_w_family_uvw((0, 0), (1, 0), (16, 1))
    assert uvw is not None
    assert uvw.U == []
    assert uvw.V == []
    assert sorted((int(i), str(v)) for i, v in uvw.W) == [
        (454, "-1/54"),
    ]


def test_predict_dual_origin_line_w_family_second_lambda() -> None:
    uvw = predict_dual_g1g2g2_uvw((0, 1), (2, 1), (15, 0))
    assert uvw is not None
    assert uvw.U == []
    assert uvw.V == []
    assert sorted((int(i), str(v)) for i, v in uvw.W) == [
        (426, "1/54"),
    ]


def test_predict_dual_origin_line_w_family_mirror_z_order() -> None:
    uvw = predict_dual_g1g2g2_uvw((0, 0), (4, 0), (13, 1))
    assert uvw is not None
    assert uvw.U == []
    assert uvw.V == []
    assert sorted((int(i), str(v)) for i, v in uvw.W) == [
        (373, "1/54"),
    ]


def test_predict_dual_origin_line_v_family_uvw() -> None:
    uvw = predict_dual_origin_line_v_family_uvw((0, 0), (1, 1), (16, 0))
    assert uvw is not None
    assert uvw.U == []
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (49, "-1/54"),
    ]


def test_predict_dual_origin_line_v_family_second_line() -> None:
    uvw = predict_dual_g1g2g2_uvw((0, 0), (2, 2), (15, 0))
    assert uvw is not None
    assert uvw.U == []
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (75, "1/54"),
    ]


def test_predict_dual_origin_line_v_family_mirror_z_order() -> None:
    uvw = predict_dual_g1g2g2_uvw((0, 0), (4, 1), (13, 0))
    assert uvw is not None
    assert uvw.U == []
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (130, "1/54"),
    ]


def test_predict_dual_origin_same_fiber_uv_family_uvw() -> None:
    uvw = predict_dual_origin_same_fiber_uv_family_uvw((0, 0), (1, 1), (15, 0))
    assert uvw is not None
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (809, "-1/108"),
    ]
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (47, "-1/108"),
    ]


def test_predict_dual_origin_same_fiber_uv_family_diagonal() -> None:
    uvw = predict_dual_g1g2g2_uvw((0, 0), (9, 1), (4, 0))
    assert uvw is not None
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (815, "1/108"),
    ]
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (261, "1/108"),
    ]


def test_predict_dual_origin_same_fiber_uv_family_mirror_z_order() -> None:
    uvw = predict_dual_g1g2g2_uvw((0, 0), (4, 1), (9, 0))
    assert uvw is not None
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (815, "1/108"),
    ]
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (126, "1/108"),
    ]


def test_predict_dual_origin_same_fiber_uv_family_x_axis_sign() -> None:
    uvw = predict_dual_g1g2g2_uvw((0, 0), (11, 1), (14, 0))
    assert uvw is not None
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (791, "1/108"),
    ]
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (323, "-1/108"),
    ]


def test_predict_dual_translated_2v_line_w_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((1, 0), (0, 0), (20, 1))
    assert uvw is not None
    assert uvw.U == []
    assert uvw.V == []
    assert sorted((int(i), str(v)) for i, v in uvw.W) == [
        (555, "1/54"),
    ]


def test_predict_dual_translated_2v_line_v_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((1, 0), (0, 1), (20, 0))
    assert uvw is not None
    assert uvw.U == []
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (15, "1/54"),
    ]


def test_predict_dual_translated_2v_overlap_uv_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((1, 0), (0, 1), (22, 0))
    assert uvw is not None
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (803, "1/108"),
    ]
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (16, "1/108"),
    ]


def test_predict_dual_vertical_z2_line_w_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((1, 1), (2, 1), (22, 0))
    assert uvw is not None
    assert uvw.U == []
    assert uvw.V == []
    assert sorted((int(i), str(v)) for i, v in uvw.W) == [
        (617, "-1/54"),
    ]


def test_predict_dual_vertical_z2_line_v_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((1, 2), (2, 0), (22, 2))
    assert uvw is not None
    assert uvw.U == []
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (77, "-1/54"),
    ]


def test_predict_dual_vertical_z2_overlap_uv_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((1, 1), (2, 0), (20, 1))
    assert uvw is not None
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (788, "-1/108"),
    ]
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (75, "1/108"),
    ]


def test_predict_dual_anchored_nonvertical_z2_line_w_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((1, 2), (7, 2), (9, 1))
    assert uvw is not None
    assert uvw.U == []
    assert uvw.V == []
    assert sorted((int(i), str(v)) for i, v in uvw.W) == [
        (258, "1/54"),
    ]


def test_predict_dual_anchored_nonvertical_z2_line_v_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((1, 1), (3, 0), (13, 1))
    assert uvw is not None
    assert uvw.U == []
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (96, "-1/54"),
    ]


def test_predict_dual_anchored_nonvertical_z2_overlap_uv_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((1, 2), (5, 0), (10, 2))
    assert uvw is not None
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (811, "1/108"),
    ]
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (149, "-1/108"),
    ]


def test_predict_dual_anchored_z1_to_z0_line_w_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((1, 0), (4, 0), (19, 1))
    assert uvw is not None
    assert uvw.U == []
    assert uvw.V == []
    assert sorted((int(i), str(v)) for i, v in uvw.W) == [
        (536, "-1/54"),
    ]


def test_predict_dual_anchored_z1_to_z0_line_v_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((1, 0), (4, 1), (19, 0))
    assert uvw is not None
    assert uvw.U == []
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (131, "-1/54"),
    ]


def test_predict_dual_anchored_z1_to_z0_overlap_uv_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((1, 0), (4, 1), (9, 0))
    assert uvw is not None
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (815, "1/108"),
    ]
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (120, "-1/108"),
    ]


def test_predict_dual_anchored_nonvertical_z2_complement_uv_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((1, 0), (7, 1), (19, 0))
    assert uvw is not None
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (776, "-1/108"),
    ]
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (214, "1/108"),
    ]


def test_predict_dual_anchored_nonvertical_z2_complement_uv_family_negative_v_sign() -> None:
    uvw = predict_dual_g1g2g2_uvw((1, 0), (11, 1), (17, 0))
    assert uvw is not None
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (782, "1/108"),
    ]
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (321, "-1/108"),
    ]


def test_predict_dual_anchor_01_origin_line_w_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((2, 0), (0, 0), (23, 1))
    assert uvw is not None
    assert uvw.U == []
    assert uvw.V == []
    assert sorted((int(i), str(v)) for i, v in uvw.W) == [
        (637, "-1/54"),
    ]


def test_predict_dual_anchor_01_origin_overlap_uv_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((2, 0), (0, 1), (21, 0))
    assert uvw is not None
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (806, "1/108"),
    ]
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (15, "-1/108"),
    ]


def test_predict_dual_anchor_01_samefiber_z2_line_w_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((2, 1), (1, 1), (21, 0))
    assert uvw is not None
    assert uvw.U == []
    assert uvw.V == []
    assert sorted((int(i), str(v)) for i, v in uvw.W) == [
        (587, "-1/54"),
    ]


def test_predict_dual_anchor_01_samefiber_z2_overlap_uv_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((2, 0), (1, 2), (23, 0))
    assert uvw is not None
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (784, "1/108"),
    ]
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (49, "1/108"),
    ]


def test_predict_dual_anchor_01_affine_z2_line_w_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((2, 0), (5, 0), (18, 1))
    assert uvw is not None
    assert uvw.U == []
    assert uvw.V == []
    assert sorted((int(i), str(v)) for i, v in uvw.W) == [
        (506, "1/54"),
    ]


def test_predict_dual_anchor_01_affine_z2_overlap_uv_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((2, 0), (3, 1), (6, 0))
    assert uvw is not None
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (818, "1/108"),
    ]
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (88, "-1/108"),
    ]


def test_predict_dual_anchor_01_affine_z1_line_v_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((2, 2), (8, 0), (10, 2))
    assert uvw is not None
    assert uvw.U == []
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (232, "1/54"),
    ]


def test_predict_dual_anchor_01_affine_z1_overlap_uv_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((2, 0), (6, 1), (3, 0))
    assert uvw is not None
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (818, "1/108"),
    ]
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (169, "-1/108"),
    ]


def test_predict_dual_anchor_01_affine_z1_complement_uv_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((2, 0), (8, 1), (18, 0))
    assert uvw is not None
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (779, "1/108"),
    ]
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (240, "1/108"),
    ]


def test_predict_dual_anchor_01_affine_z1_complement_uv_family_sign_flip() -> None:
    uvw = predict_dual_g1g2g2_uvw((2, 0), (12, 1), (19, 0))
    assert uvw is not None
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (761, "-1/108"),
    ]
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (350, "1/108"),
    ]


def test_predict_dual_anchor_20_origin_overlap_uv_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((3, 0), (0, 1), (21, 0))
    assert uvw is not None
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (806, "1/108"),
    ]
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (14, "1/108"),
    ]


def test_predict_dual_anchor_20_samefiber_z2_line_w_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((3, 0), (11, 0), (21, 1))
    assert uvw is not None
    assert uvw.U == []
    assert uvw.V == []
    assert sorted((int(i), str(v)) for i, v in uvw.W) == [
        (593, "1/54"),
    ]


def test_predict_dual_anchor_20_samefiber_z2_overlap_uv_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((3, 0), (11, 1), (17, 0))
    assert uvw is not None
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (782, "1/108"),
    ]
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (319, "1/108"),
    ]


def test_predict_dual_anchor_20_zero2_z2_line_w_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((3, 0), (1, 0), (8, 1))
    assert uvw is not None
    assert uvw.U == []
    assert uvw.V == []
    assert sorted((int(i), str(v)) for i, v in uvw.W) == [
        (222, "-1/54"),
    ]


def test_predict_dual_anchor_20_zero2_z2_overlap_uv_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((3, 0), (1, 1), (15, 0))
    assert uvw is not None
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (809, "-1/108"),
    ]
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (40, "1/108"),
    ]


def test_predict_dual_anchor_20_zero1_z2_line_w_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((3, 0), (2, 0), (7, 1))
    assert uvw is not None
    assert uvw.U == []
    assert uvw.V == []
    assert sorted((int(i), str(v)) for i, v in uvw.W) == [
        (195, "1/54"),
    ]


def test_predict_dual_anchor_20_zero1_z2_overlap_uv_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((3, 0), (2, 1), (20, 0))
    assert uvw is not None
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (788, "1/108"),
    ]
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (73, "1/108"),
    ]


def test_predict_dual_anchor_20_two2_z1_line_w_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((3, 0), (4, 0), (5, 1))
    assert uvw is not None
    assert uvw.U == []
    assert uvw.V == []
    assert sorted((int(i), str(v)) for i, v in uvw.W) == [
        (141, "-1/54"),
    ]


def test_predict_dual_anchor_20_two2_z1_overlap_uv_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((3, 0), (4, 1), (9, 0))
    assert uvw is not None
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (815, "1/108"),
    ]
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (118, "1/108"),
    ]


def test_predict_dual_anchor_20_two1_z2_complement_uv_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((3, 0), (5, 1), (24, 0))
    assert uvw is not None
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (770, "1/108"),
    ]
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (160, "1/108"),
    ]


def test_predict_dual_anchor_20_one2_z2_complement_uv_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((3, 0), (7, 1), (12, 0))
    assert uvw is not None
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (797, "-1/108"),
    ]
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (205, "-1/108"),
    ]


def test_predict_dual_anchor_20_one1_z1_complement_uv_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((3, 0), (8, 1), (18, 0))
    assert uvw is not None
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (779, "1/108"),
    ]
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (239, "-1/108"),
    ]


def test_predict_dual_anchor_20_two2_z2_line_w_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((3, 0), (9, 0), (24, 1))
    assert uvw is not None
    assert uvw.U == []
    assert uvw.V == []
    assert sorted((int(i), str(v)) for i, v in uvw.W) == [
        (674, "-1/54"),
    ]


def test_predict_dual_anchor_20_one2_z1_line_w_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((3, 0), (12, 0), (20, 1))
    assert uvw is not None
    assert uvw.U == []
    assert uvw.V == []
    assert sorted((int(i), str(v)) for i, v in uvw.W) == [
        (566, "-1/54"),
    ]


def test_predict_dual_anchor_20_one2_z1_overlap_uv_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((3, 0), (12, 1), (7, 0))
    assert uvw is not None
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (797, "-1/108"),
    ]
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (340, "-1/108"),
    ]


def test_predict_dual_anchor_20_zero2_z1_line_w_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((3, 0), (15, 0), (18, 1))
    assert uvw is not None
    assert uvw.U == []
    assert uvw.V == []
    assert sorted((int(i), str(v)) for i, v in uvw.W) == [
        (512, "-1/54"),
    ]


def test_predict_dual_anchor_20_zero2_z1_overlap_uv_family() -> None:
    uvw = predict_dual_g1g2g2_uvw((3, 0), (15, 1), (1, 0))
    assert uvw is not None
    assert uvw.W == []
    assert sorted((int(i), str(v)) for i, v in uvw.U) == [
        (809, "-1/108"),
    ]
    assert sorted((int(i), str(v)) for i, v in uvw.V) == [
        (418, "1/108"),
    ]


def test_predict_dual_anchor_22_line_families() -> None:
    samples = [
        (((4, 0), (0, 0), (18, 1)), [], [], [(18, 9, "-1/54")]),
        (((4, 0), (1, 1), (12, 0)), [], [(1, 9, "1/54")], []),
        (((4, 0), (2, 0), (11, 1)), [], [], [(11, 9, "-1/54")]),
        (((4, 0), (3, 1), (10, 0)), [], [(3, 9, "-1/54")], []),
        (((4, 0), (6, 0), (24, 1)), [], [], [(24, 25, "-1/54")]),
        (((4, 0), (7, 1), (23, 0)), [], [(7, 25, "-1/54")], []),
        (((4, 0), (8, 0), (22, 1)), [], [], [(22, 25, "1/54")]),
        (((4, 0), (16, 1), (17, 0)), [], [(16, 25, "-1/54")], []),
    ]
    for triple, expected_u, expected_v, expected_w in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert _decode_e6(uvw.W) == expected_w, triple


def test_predict_dual_anchor_22_overlap_families() -> None:
    samples = [
        (((4, 0), (0, 1), (22, 0)), [(21, 2, "1/108")], [(0, 13, "-1/108")]),
        (((4, 0), (1, 1), (23, 0)), [(15, 2, "-1/108")], [(1, 19, "1/108")]),
        (((4, 0), (2, 1), (16, 0)), [(20, 2, "1/108")], [(2, 14, "1/108")]),
        (((4, 0), (3, 1), (6, 0)), [(26, 2, "1/108")], [(3, 5, "1/108")]),
        (((4, 0), (7, 1), (12, 0)), [(19, 2, "-1/108")], [(7, 15, "1/108")]),
        (((4, 0), (8, 1), (18, 0)), [(13, 2, "1/108")], [(8, 21, "-1/108")]),
        (((4, 0), (10, 1), (24, 0)), [(5, 2, "1/108")], [(10, 26, "1/108")]),
        (((4, 0), (11, 1), (17, 0)), [(14, 2, "1/108")], [(11, 20, "1/108")]),
    ]
    for triple, expected_u, expected_v in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_anchor_22_overlap_sign_flips() -> None:
    samples = [
        (((4, 0), (0, 2), (22, 0)), [(21, 1, "-1/108")], [(0, 13, "-1/108")]),
        (((4, 0), (1, 2), (23, 0)), [(15, 1, "1/108")], [(1, 19, "1/108")]),
        (((4, 0), (7, 2), (12, 0)), [(19, 1, "1/108")], [(7, 15, "1/108")]),
        (((4, 0), (8, 2), (18, 0)), [(13, 1, "-1/108")], [(8, 21, "-1/108")]),
    ]
    for triple, expected_u, expected_v in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_anchor_21_line_families() -> None:
    samples = [
        (((5, 0), (1, 0), (14, 1)), [], [], [(14, 10, "1/54")]),
        (((5, 0), (2, 1), (13, 0)), [], [(2, 10, "-1/54")], []),
        (((5, 0), (3, 0), (25, 1)), [], [], [(25, 24, "-1/54")]),
        (((5, 0), (6, 1), (9, 0)), [], [(6, 10, "-1/54")], []),
        (((5, 0), (7, 0), (21, 1)), [], [], [(21, 24, "-1/54")]),
        (((5, 0), (8, 1), (20, 0)), [], [(8, 24, "1/54")], []),
        (((5, 0), (15, 0), (17, 1)), [], [], [(17, 24, "1/54")]),
    ]
    for triple, expected_u, expected_v, expected_w in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert _decode_e6(uvw.W) == expected_w, triple


def test_predict_dual_anchor_21_overlap_families() -> None:
    samples = [
        (((5, 0), (0, 1), (21, 0)), [(22, 2, "1/108")], [(0, 12, "1/108")]),
        (((5, 0), (1, 1), (15, 0)), [(23, 2, "-1/108")], [(1, 11, "1/108")]),
        (((5, 0), (2, 1), (20, 0)), [(16, 2, "1/108")], [(2, 18, "-1/108")]),
        (((5, 0), (3, 1), (6, 0)), [(26, 2, "1/108")], [(3, 4, "1/108")]),
        (((5, 0), (7, 1), (19, 0)), [(12, 2, "-1/108")], [(7, 22, "-1/108")]),
        (((5, 0), (8, 1), (13, 0)), [(18, 2, "1/108")], [(8, 16, "-1/108")]),
        (((5, 0), (9, 1), (25, 0)), [(4, 2, "1/108")], [(9, 26, "1/108")]),
        (((5, 0), (14, 1), (17, 0)), [(11, 2, "1/108")], [(14, 23, "-1/108")]),
    ]
    for triple, expected_u, expected_v in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_anchor_21_overlap_sign_flips() -> None:
    samples = [
        (((5, 0), (0, 2), (21, 0)), [(22, 1, "-1/108")], [(0, 12, "1/108")]),
        (((5, 0), (1, 2), (15, 0)), [(23, 1, "1/108")], [(1, 11, "1/108")]),
        (((5, 0), (7, 2), (19, 0)), [(12, 1, "1/108")], [(7, 22, "-1/108")]),
        (((5, 0), (8, 2), (13, 0)), [(18, 1, "-1/108")], [(8, 16, "-1/108")]),
    ]
    for triple, expected_u, expected_v in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_anchor_201_line_families() -> None:
    samples = [
        (((6, 0), (0, 0), (17, 1)), [], [], [(17, 3, "1/54")]),
        (((6, 0), (0, 1), (17, 0)), [], [(0, 3, "1/54")], []),
        (((6, 0), (1, 0), (8, 1)), [], [], [(8, 3, "-1/54")]),
        (((6, 0), (1, 1), (8, 0)), [], [(1, 3, "-1/54")], []),
        (((6, 0), (2, 0), (7, 1)), [], [], [(7, 3, "1/54")]),
        (((6, 0), (2, 1), (7, 0)), [], [(2, 3, "1/54")], []),
        (((6, 0), (4, 0), (5, 1)), [], [], [(5, 3, "-1/54")]),
        (((6, 0), (4, 1), (5, 0)), [], [(4, 3, "-1/54")], []),
    ]
    for triple, expected_u, expected_v, expected_w in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert _decode_e6(uvw.W) == expected_w, triple


def test_predict_dual_anchor_201_overlap_families() -> None:
    samples = [
        (((6, 0), (0, 1), (22, 0)), [(21, 2, "1/108")], [(0, 11, "-1/108")]),
        (((6, 0), (0, 2), (22, 0)), [(21, 1, "-1/108")], [(0, 11, "-1/108")]),
        (((6, 0), (1, 1), (23, 0)), [(15, 2, "-1/108")], [(1, 18, "-1/108")]),
        (((6, 0), (1, 2), (23, 0)), [(15, 1, "1/108")], [(1, 18, "-1/108")]),
        (((6, 0), (2, 1), (16, 0)), [(20, 2, "1/108")], [(2, 12, "1/108")]),
        (((6, 0), (2, 2), (16, 0)), [(20, 1, "-1/108")], [(2, 12, "1/108")]),
        (((6, 0), (4, 1), (25, 0)), [(9, 2, "1/108")], [(4, 24, "1/108")]),
        (((6, 0), (4, 2), (25, 0)), [(9, 1, "-1/108")], [(4, 24, "1/108")]),
    ]
    for triple, expected_u, expected_v in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_anchor_201_samefiber_v_family() -> None:
    samples = [
        (((6, 0), (3, 0), (6, 1)), [], [("sl3", 0, 1, "-1/54")], []),
        (((6, 0), (3, 0), (6, 2)), [], [("sl3", 0, 2, "-1/54")], []),
        (((6, 0), (3, 1), (6, 0)), [], [("e6", 3, 3, "1/108"), ("sl3", 1, 1, "1/108")], []),
        (((6, 0), (3, 2), (6, 0)), [], [("e6", 3, 3, "1/108"), ("sl3", 2, 2, "1/108")], []),
    ]
    for triple, expected_u, expected_v, expected_w in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_sparse(uvw.V) == expected_v, triple
        assert _decode_e6(uvw.W) == expected_w, triple
