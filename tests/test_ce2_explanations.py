from __future__ import annotations

from scripts.ce2_global_cocycle import (
    predict_dual_a01_line_v_family_uvw,
    predict_dual_a01_line_w_family_uvw,
    predict_dual_a01_b00_reflection_u_family_uvw,
    predict_dual_a01_b0_reflection_uv12_family_uvw,
    predict_dual_a01_sameid_source_color_uv12_family_uvw,
    predict_dual_a01_sameid_source_diag_uv18_family_uvw,
    predict_dual_a01_source1_line_u_family_uvw,
    predict_dual_a01_source1_line_uv12_family_uvw,
    predict_dual_a01_source1_z0_line_u_family_uvw,
    predict_dual_a01_source1_z0_line_uv12_family_uvw,
    predict_dual_a01_overlap_uv_family_uvw,
    predict_dual_a10_line_v_family_uvw,
    predict_dual_a10_line_w_family_uvw,
    predict_dual_a10_overlap_uv_family_uvw,
    predict_dual_a11_line_v_family_uvw,
    predict_dual_a11_line_w_family_uvw,
    predict_dual_a11_overlap_uv_family_uvw,
    predict_dual_a12_line_v_family_uvw,
    predict_dual_a12_line_w_family_uvw,
    predict_dual_a12_overlap_uv_family_uvw,
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
        (((6, 0), (10, 0), (25, 1)), [], [], [(25, 26, "-1/54")]),
        (((6, 0), (10, 1), (25, 0)), [], [(10, 26, "-1/54")], []),
        (((6, 0), (13, 0), (23, 1)), [], [], [(23, 26, "1/54")]),
        (((6, 0), (13, 1), (23, 0)), [], [(13, 26, "1/54")], []),
        (((6, 0), (14, 0), (22, 1)), [], [], [(22, 26, "-1/54")]),
        (((6, 0), (14, 1), (22, 0)), [], [(14, 26, "-1/54")], []),
        (((6, 0), (16, 0), (19, 1)), [], [], [(19, 26, "-1/54")]),
        (((6, 0), (16, 1), (19, 0)), [], [(16, 26, "-1/54")], []),
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
        (((6, 0), (5, 1), (10, 0)), [(24, 2, "1/108")], [(5, 9, "1/108")]),
        (((6, 0), (5, 2), (10, 0)), [(24, 1, "-1/108")], [(5, 9, "1/108")]),
        (((6, 0), (7, 1), (19, 0)), [(12, 2, "-1/108")], [(7, 20, "-1/108")]),
        (((6, 0), (7, 2), (19, 0)), [(12, 1, "1/108")], [(7, 20, "-1/108")]),
        (((6, 0), (8, 1), (13, 0)), [(18, 2, "1/108")], [(8, 15, "1/108")]),
        (((6, 0), (8, 2), (13, 0)), [(18, 1, "-1/108")], [(8, 15, "1/108")]),
        (((6, 0), (14, 1), (17, 0)), [(11, 2, "1/108")], [(14, 21, "-1/108")]),
        (((6, 0), (14, 2), (17, 0)), [(11, 1, "-1/108")], [(14, 21, "-1/108")]),
    ]
    for triple, expected_u, expected_v in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_anchor_122_line_families() -> None:
    samples = [
        (((7, 0), (0, 0), (24, 1)), [], [], [(24, 12, "-1/54")]),
        (((7, 0), (0, 1), (24, 0)), [], [(0, 12, "-1/54")], []),
        (((7, 0), (1, 0), (25, 1)), [], [], [(25, 19, "-1/54")]),
        (((7, 0), (1, 1), (25, 0)), [], [(1, 19, "-1/54")], []),
        (((7, 0), (3, 0), (16, 1)), [], [], [(16, 12, "1/54")]),
        (((7, 0), (3, 1), (16, 0)), [], [(3, 12, "1/54")], []),
        (((7, 0), (4, 0), (15, 1)), [], [], [(15, 12, "-1/54")]),
        (((7, 0), (4, 1), (15, 0)), [], [(4, 12, "-1/54")], []),
        (((7, 0), (5, 0), (22, 1)), [], [], [(22, 19, "1/54")]),
        (((7, 0), (5, 1), (22, 0)), [], [(5, 19, "1/54")], []),
        (((7, 0), (6, 0), (20, 1)), [], [], [(20, 19, "1/54")]),
        (((7, 0), (6, 1), (20, 0)), [], [(6, 19, "1/54")], []),
        (((7, 0), (8, 0), (11, 1)), [], [], [(11, 12, "-1/54")]),
        (((7, 0), (8, 1), (11, 0)), [], [(8, 12, "-1/54")], []),
        (((7, 0), (13, 0), (17, 1)), [], [], [(17, 19, "1/54")]),
        (((7, 0), (13, 1), (17, 0)), [], [(13, 19, "1/54")], []),
    ]
    for triple, expected_u, expected_v, expected_w in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert _decode_e6(uvw.W) == expected_w, triple


def test_predict_dual_anchor_122_overlap_families() -> None:
    samples = [
        (((7, 0), (0, 1), (22, 0)), [(21, 2, "1/108")], [(0, 10, "1/108")]),
        (((7, 0), (0, 2), (22, 0)), [(21, 1, "-1/108")], [(0, 10, "1/108")]),
        (((7, 0), (1, 1), (15, 0)), [(23, 2, "-1/108")], [(1, 9, "-1/108")]),
        (((7, 0), (1, 2), (15, 0)), [(23, 1, "1/108")], [(1, 9, "-1/108")]),
        (((7, 0), (3, 1), (6, 0)), [(26, 2, "1/108")], [(3, 2, "-1/108")]),
        (((7, 0), (3, 2), (6, 0)), [(26, 1, "-1/108")], [(3, 2, "-1/108")]),
        (((7, 0), (4, 1), (25, 0)), [(9, 2, "1/108")], [(4, 23, "1/108")]),
        (((7, 0), (4, 2), (25, 0)), [(9, 1, "-1/108")], [(4, 23, "1/108")]),
        (((7, 0), (5, 1), (24, 0)), [(10, 2, "1/108")], [(5, 21, "1/108")]),
        (((7, 0), (5, 2), (24, 0)), [(10, 1, "-1/108")], [(5, 21, "1/108")]),
        (((7, 0), (8, 1), (13, 0)), [(18, 2, "1/108")], [(8, 14, "1/108")]),
        (((7, 0), (8, 2), (13, 0)), [(18, 1, "-1/108")], [(8, 14, "1/108")]),
        (((7, 0), (11, 1), (17, 0)), [(14, 2, "1/108")], [(11, 18, "1/108")]),
        (((7, 0), (11, 2), (17, 0)), [(14, 1, "-1/108")], [(11, 18, "1/108")]),
        (((7, 0), (16, 1), (20, 0)), [(2, 2, "1/108")], [(16, 26, "-1/108")]),
        (((7, 0), (16, 2), (20, 0)), [(2, 1, "-1/108")], [(16, 26, "-1/108")]),
    ]
    for triple, expected_u, expected_v in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_anchor_111_line_families() -> None:
    samples = [
        (((8, 0), (0, 0), (25, 1)), [], [], [(25, 13, "-1/54")]),
        (((8, 0), (0, 1), (25, 0)), [], [(0, 13, "-1/54")], []),
        (((8, 0), (2, 0), (24, 1)), [], [], [(24, 18, "-1/54")]),
        (((8, 0), (2, 1), (24, 0)), [], [(2, 18, "-1/54")], []),
        (((8, 0), (3, 0), (23, 1)), [], [], [(23, 18, "1/54")]),
        (((8, 0), (3, 1), (23, 0)), [], [(3, 18, "1/54")], []),
        (((8, 0), (4, 0), (21, 1)), [], [], [(21, 18, "1/54")]),
        (((8, 0), (4, 1), (21, 0)), [], [(4, 18, "1/54")], []),
        (((8, 0), (5, 0), (16, 1)), [], [], [(16, 13, "1/54")]),
        (((8, 0), (5, 1), (16, 0)), [], [(5, 13, "1/54")], []),
        (((8, 0), (6, 0), (15, 1)), [], [], [(15, 13, "-1/54")]),
        (((8, 0), (6, 1), (15, 0)), [], [(6, 13, "-1/54")], []),
        (((8, 0), (7, 0), (14, 1)), [], [], [(14, 13, "-1/54")]),
        (((8, 0), (7, 1), (14, 0)), [], [(7, 13, "-1/54")], []),
        (((8, 0), (12, 0), (17, 1)), [], [], [(17, 18, "-1/54")]),
        (((8, 0), (12, 1), (17, 0)), [], [(12, 18, "-1/54")], []),
    ]
    for triple, expected_u, expected_v, expected_w in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert _decode_e6(uvw.W) == expected_w, triple


def test_predict_dual_anchor_111_overlap_families() -> None:
    samples = [
        (((8, 0), (0, 1), (21, 0)), [(22, 2, "1/108")], [(0, 9, "-1/108")]),
        (((8, 0), (0, 2), (21, 0)), [(22, 1, "-1/108")], [(0, 9, "-1/108")]),
        (((8, 0), (2, 1), (16, 0)), [(20, 2, "1/108")], [(2, 10, "-1/108")]),
        (((8, 0), (2, 2), (16, 0)), [(20, 1, "-1/108")], [(2, 10, "-1/108")]),
        (((8, 0), (3, 1), (6, 0)), [(26, 2, "1/108")], [(3, 1, "1/108")]),
        (((8, 0), (3, 2), (6, 0)), [(26, 1, "-1/108")], [(3, 1, "1/108")]),
        (((8, 0), (4, 1), (25, 0)), [(9, 2, "1/108")], [(4, 22, "-1/108")]),
        (((8, 0), (4, 2), (25, 0)), [(9, 1, "-1/108")], [(4, 22, "-1/108")]),
        (((8, 0), (5, 1), (24, 0)), [(10, 2, "1/108")], [(5, 20, "-1/108")]),
        (((8, 0), (5, 2), (24, 0)), [(10, 1, "-1/108")], [(5, 20, "-1/108")]),
        (((8, 0), (7, 1), (12, 0)), [(19, 2, "-1/108")], [(7, 11, "1/108")]),
        (((8, 0), (7, 2), (12, 0)), [(19, 1, "1/108")], [(7, 11, "1/108")]),
        (((8, 0), (14, 1), (17, 0)), [(11, 2, "1/108")], [(14, 19, "-1/108")]),
        (((8, 0), (14, 2), (17, 0)), [(11, 1, "-1/108")], [(14, 19, "-1/108")]),
        (((8, 0), (15, 1), (23, 0)), [(1, 2, "-1/108")], [(15, 26, "-1/108")]),
        (((8, 0), (15, 2), (23, 0)), [(1, 1, "1/108")], [(15, 26, "-1/108")]),
    ]
    for triple, expected_u, expected_v in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_anchor_222_line_families() -> None:
    samples = [
        (((9, 0), (1, 0), (12, 1)), [], [], [(12, 4, "1/54")]),
        (((9, 0), (1, 1), (12, 0)), [], [(1, 4, "1/54")], []),
        (((9, 0), (2, 0), (11, 1)), [], [], [(11, 4, "-1/54")]),
        (((9, 0), (2, 1), (11, 0)), [], [(2, 4, "-1/54")], []),
        (((9, 0), (3, 0), (10, 1)), [], [], [(10, 4, "-1/54")]),
        (((9, 0), (3, 1), (10, 0)), [], [(3, 4, "-1/54")], []),
        (((9, 0), (5, 0), (26, 1)), [], [], [(26, 25, "-1/54")]),
        (((9, 0), (5, 1), (26, 0)), [], [(5, 25, "-1/54")], []),
        (((9, 0), (13, 0), (21, 1)), [], [], [(21, 25, "1/54")]),
        (((9, 0), (13, 1), (21, 0)), [], [(13, 25, "1/54")], []),
        (((9, 0), (14, 0), (20, 1)), [], [], [(20, 25, "-1/54")]),
        (((9, 0), (14, 1), (20, 0)), [], [(14, 25, "-1/54")], []),
        (((9, 0), (15, 0), (19, 1)), [], [], [(19, 25, "1/54")]),
        (((9, 0), (15, 1), (19, 0)), [], [(15, 25, "1/54")], []),
    ]
    for triple, expected_u, expected_v, expected_w in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert _decode_e6(uvw.W) == expected_w, triple


def test_predict_dual_anchor_222_overlap_families() -> None:
    samples = [
        (((9, 0), (0, 1), (21, 0)), [(22, 2, "1/108")], [(0, 8, "-1/108")]),
        (((9, 0), (0, 2), (21, 0)), [(22, 1, "-1/108")], [(0, 8, "-1/108")]),
        (((9, 0), (1, 1), (15, 0)), [(23, 2, "-1/108")], [(1, 7, "-1/108")]),
        (((9, 0), (1, 2), (15, 0)), [(23, 1, "1/108")], [(1, 7, "-1/108")]),
        (((9, 0), (2, 1), (20, 0)), [(16, 2, "1/108")], [(2, 17, "1/108")]),
        (((9, 0), (2, 2), (20, 0)), [(16, 1, "-1/108")], [(2, 17, "1/108")]),
        (((9, 0), (3, 1), (26, 0)), [(6, 2, "1/108")], [(3, 24, "1/108")]),
        (((9, 0), (3, 2), (26, 0)), [(6, 1, "-1/108")], [(3, 24, "1/108")]),
        (((9, 0), (5, 1), (10, 0)), [(24, 2, "1/108")], [(5, 6, "1/108")]),
        (((9, 0), (5, 2), (10, 0)), [(24, 1, "-1/108")], [(5, 6, "1/108")]),
        (((9, 0), (11, 1), (14, 0)), [(17, 2, "1/108")], [(11, 16, "1/108")]),
        (((9, 0), (11, 2), (14, 0)), [(17, 1, "-1/108")], [(11, 16, "1/108")]),
        (((9, 0), (12, 1), (19, 0)), [(7, 2, "-1/108")], [(12, 23, "-1/108")]),
        (((9, 0), (12, 2), (19, 0)), [(7, 1, "1/108")], [(12, 23, "-1/108")]),
        (((9, 0), (13, 1), (18, 0)), [(8, 2, "1/108")], [(13, 22, "-1/108")]),
        (((9, 0), (13, 2), (18, 0)), [(8, 1, "-1/108")], [(13, 22, "-1/108")]),
    ]
    for triple, expected_u, expected_v in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_anchor_211_line_families() -> None:
    samples = [
        (((10, 0), (0, 0), (19, 1)), [], [], [(19, 5, "1/54")]),
        (((10, 0), (0, 1), (19, 0)), [], [(0, 5, "1/54")], []),
        (((10, 0), (1, 0), (14, 1)), [], [], [(14, 5, "1/54")]),
        (((10, 0), (1, 1), (14, 0)), [], [(1, 5, "1/54")], []),
        (((10, 0), (2, 0), (13, 1)), [], [], [(13, 5, "-1/54")]),
        (((10, 0), (2, 1), (13, 0)), [], [(2, 5, "-1/54")], []),
        (((10, 0), (4, 0), (26, 1)), [], [], [(26, 24, "-1/54")]),
        (((10, 0), (4, 1), (26, 0)), [], [(4, 24, "-1/54")], []),
        (((10, 0), (6, 0), (9, 1)), [], [], [(9, 5, "-1/54")]),
        (((10, 0), (6, 1), (9, 0)), [], [(6, 5, "-1/54")], []),
        (((10, 0), (11, 0), (23, 1)), [], [], [(23, 24, "1/54")]),
        (((10, 0), (11, 1), (23, 0)), [], [(11, 24, "1/54")], []),
        (((10, 0), (12, 0), (22, 1)), [], [], [(22, 24, "-1/54")]),
        (((10, 0), (12, 1), (22, 0)), [], [(12, 24, "-1/54")], []),
        (((10, 0), (16, 0), (18, 1)), [], [], [(18, 24, "1/54")]),
        (((10, 0), (16, 1), (18, 0)), [], [(16, 24, "1/54")], []),
    ]
    for triple, expected_u, expected_v, expected_w in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert _decode_e6(uvw.W) == expected_w, triple


def test_predict_dual_anchor_211_overlap_families() -> None:
    samples = [
        (((10, 0), (0, 1), (22, 0)), [(21, 2, "1/108")], [(0, 7, "1/108")]),
        (((10, 0), (0, 2), (22, 0)), [(21, 1, "-1/108")], [(0, 7, "1/108")]),
        (((10, 0), (1, 1), (23, 0)), [(15, 2, "-1/108")], [(1, 17, "1/108")]),
        (((10, 0), (1, 2), (23, 0)), [(15, 1, "1/108")], [(1, 17, "1/108")]),
        (((10, 0), (2, 1), (16, 0)), [(20, 2, "1/108")], [(2, 8, "-1/108")]),
        (((10, 0), (2, 2), (16, 0)), [(20, 1, "-1/108")], [(2, 8, "-1/108")]),
        (((10, 0), (4, 1), (9, 0)), [(25, 2, "1/108")], [(4, 3, "1/108")]),
        (((10, 0), (4, 2), (9, 0)), [(25, 1, "-1/108")], [(4, 3, "1/108")]),
        (((10, 0), (6, 1), (26, 0)), [(3, 2, "1/108")], [(6, 25, "1/108")]),
        (((10, 0), (6, 2), (26, 0)), [(3, 1, "-1/108")], [(6, 25, "1/108")]),
        (((10, 0), (11, 1), (14, 0)), [(17, 2, "1/108")], [(11, 15, "-1/108")]),
        (((10, 0), (11, 2), (14, 0)), [(17, 1, "-1/108")], [(11, 15, "-1/108")]),
        (((10, 0), (12, 1), (19, 0)), [(7, 2, "-1/108")], [(12, 21, "-1/108")]),
        (((10, 0), (12, 2), (19, 0)), [(7, 1, "1/108")], [(12, 21, "-1/108")]),
        (((10, 0), (13, 1), (18, 0)), [(8, 2, "1/108")], [(13, 20, "-1/108")]),
        (((10, 0), (13, 2), (18, 0)), [(8, 1, "-1/108")], [(13, 20, "-1/108")]),
    ]
    for triple, expected_u, expected_v in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_anchor_102_line_families() -> None:
    samples = [
        (((11, 0), (1, 0), (24, 1)), [], [], [(24, 17, "1/54")]),
        (((11, 0), (1, 0), (24, 2)), [], [], [(24, 17, "1/54")]),
        (((11, 0), (1, 1), (24, 0)), [], [(1, 17, "1/54")], []),
        (((11, 0), (1, 2), (24, 0)), [], [(1, 17, "1/54")], []),
        (((11, 0), (3, 0), (22, 1)), [], [], [(22, 17, "-1/54")]),
        (((11, 0), (3, 0), (22, 2)), [], [], [(22, 17, "-1/54")]),
        (((11, 0), (3, 1), (22, 0)), [], [(3, 17, "-1/54")], []),
        (((11, 0), (3, 2), (22, 0)), [], [(3, 17, "-1/54")], []),
        (((11, 0), (4, 0), (20, 1)), [], [], [(20, 17, "-1/54")]),
        (((11, 0), (4, 0), (20, 2)), [], [], [(20, 17, "-1/54")]),
        (((11, 0), (4, 1), (20, 0)), [], [(4, 17, "-1/54")], []),
        (((11, 0), (4, 2), (20, 0)), [], [(4, 17, "-1/54")], []),
        (((11, 0), (7, 0), (18, 1)), [], [], [(18, 17, "-1/54")]),
        (((11, 0), (7, 0), (18, 2)), [], [], [(18, 17, "-1/54")]),
        (((11, 0), (7, 1), (18, 0)), [], [(7, 17, "-1/54")], []),
        (((11, 0), (7, 2), (18, 0)), [], [(7, 17, "-1/54")], []),
        (((11, 0), (9, 0), (16, 1)), [], [], [(16, 14, "-1/54")]),
        (((11, 0), (9, 0), (16, 2)), [], [], [(16, 14, "-1/54")]),
        (((11, 0), (9, 1), (16, 0)), [], [(9, 14, "-1/54")], []),
        (((11, 0), (9, 2), (16, 0)), [], [(9, 14, "-1/54")], []),
        (((11, 0), (10, 0), (15, 1)), [], [], [(15, 14, "1/54")]),
        (((11, 0), (10, 0), (15, 2)), [], [], [(15, 14, "1/54")]),
        (((11, 0), (10, 1), (15, 0)), [], [(10, 14, "1/54")], []),
        (((11, 0), (10, 2), (15, 0)), [], [(10, 14, "1/54")], []),
        (((11, 0), (12, 0), (13, 1)), [], [], [(13, 14, "-1/54")]),
        (((11, 0), (12, 0), (13, 2)), [], [], [(13, 14, "-1/54")]),
        (((11, 0), (12, 1), (13, 0)), [], [(12, 14, "-1/54")], []),
        (((11, 0), (12, 2), (13, 0)), [], [(12, 14, "-1/54")], []),
    ]
    for triple, expected_u, expected_v, expected_w in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert _decode_e6(uvw.W) == expected_w, triple


def test_predict_dual_anchor_102_overlap_families() -> None:
    samples = [
        (((11, 0), (0, 1), (22, 0)), [(21, 2, "1/108")], [(0, 6, "-1/108")]),
        (((11, 0), (0, 2), (22, 0)), [(21, 1, "-1/108")], [(0, 6, "-1/108")]),
        (((11, 0), (1, 1), (15, 0)), [(23, 2, "-1/108")], [(1, 5, "1/108")]),
        (((11, 0), (1, 2), (15, 0)), [(23, 1, "1/108")], [(1, 5, "1/108")]),
        (((11, 0), (3, 1), (26, 0)), [(6, 2, "1/108")], [(3, 21, "-1/108")]),
        (((11, 0), (3, 2), (26, 0)), [(6, 1, "-1/108")], [(3, 21, "-1/108")]),
        (((11, 0), (4, 1), (9, 0)), [(25, 2, "1/108")], [(4, 2, "1/108")]),
        (((11, 0), (4, 2), (9, 0)), [(25, 1, "-1/108")], [(4, 2, "1/108")]),
        (((11, 0), (7, 1), (12, 0)), [(19, 2, "-1/108")], [(7, 8, "1/108")]),
        (((11, 0), (7, 2), (12, 0)), [(19, 1, "1/108")], [(7, 8, "1/108")]),
        (((11, 0), (10, 1), (24, 0)), [(5, 2, "1/108")], [(10, 23, "-1/108")]),
        (((11, 0), (10, 2), (24, 0)), [(5, 1, "-1/108")], [(10, 23, "-1/108")]),
        (((11, 0), (13, 1), (18, 0)), [(8, 2, "1/108")], [(13, 19, "-1/108")]),
        (((11, 0), (13, 2), (18, 0)), [(8, 1, "-1/108")], [(13, 19, "-1/108")]),
        (((11, 0), (16, 1), (20, 0)), [(2, 2, "1/108")], [(16, 25, "1/108")]),
        (((11, 0), (16, 2), (20, 0)), [(2, 1, "-1/108")], [(16, 25, "1/108")]),
    ]
    for triple, expected_u, expected_v in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_anchor_121_line_families() -> None:
    samples = [
        (((12, 0), (0, 0), (24, 1)), [], [], [(24, 7, "-1/54")]),
        (((12, 0), (0, 0), (24, 2)), [], [], [(24, 7, "-1/54")]),
        (((12, 0), (0, 1), (24, 0)), [], [(0, 7, "-1/54")], []),
        (((12, 0), (0, 2), (24, 0)), [], [(0, 7, "-1/54")], []),
        (((12, 0), (2, 0), (26, 1)), [], [], [(26, 19, "-1/54")]),
        (((12, 0), (2, 0), (26, 2)), [], [], [(26, 19, "-1/54")]),
        (((12, 0), (2, 1), (26, 0)), [], [(2, 19, "-1/54")], []),
        (((12, 0), (2, 2), (26, 0)), [], [(2, 19, "-1/54")], []),
        (((12, 0), (3, 0), (16, 1)), [], [], [(16, 7, "1/54")]),
        (((12, 0), (3, 0), (16, 2)), [], [], [(16, 7, "1/54")]),
        (((12, 0), (3, 1), (16, 0)), [], [(3, 7, "1/54")], []),
        (((12, 0), (3, 2), (16, 0)), [], [(3, 7, "1/54")], []),
        (((12, 0), (4, 0), (15, 1)), [], [], [(15, 7, "-1/54")]),
        (((12, 0), (4, 0), (15, 2)), [], [], [(15, 7, "-1/54")]),
        (((12, 0), (4, 1), (15, 0)), [], [(4, 7, "-1/54")], []),
        (((12, 0), (4, 2), (15, 0)), [], [(4, 7, "-1/54")], []),
        (((12, 0), (8, 0), (11, 1)), [], [], [(11, 7, "-1/54")]),
        (((12, 0), (8, 0), (11, 2)), [], [], [(11, 7, "-1/54")]),
        (((12, 0), (8, 1), (11, 0)), [], [(8, 7, "-1/54")], []),
        (((12, 0), (8, 2), (11, 0)), [], [(8, 7, "-1/54")], []),
        (((12, 0), (9, 0), (23, 1)), [], [], [(23, 19, "1/54")]),
        (((12, 0), (9, 0), (23, 2)), [], [], [(23, 19, "1/54")]),
        (((12, 0), (9, 1), (23, 0)), [], [(9, 19, "1/54")], []),
        (((12, 0), (9, 2), (23, 0)), [], [(9, 19, "1/54")], []),
        (((12, 0), (10, 0), (21, 1)), [], [], [(21, 19, "1/54")]),
        (((12, 0), (10, 0), (21, 2)), [], [], [(21, 19, "1/54")]),
        (((12, 0), (10, 1), (21, 0)), [], [(10, 19, "1/54")], []),
        (((12, 0), (10, 2), (21, 0)), [], [(10, 19, "1/54")], []),
        (((12, 0), (14, 0), (18, 1)), [], [], [(18, 19, "1/54")]),
        (((12, 0), (14, 0), (18, 2)), [], [], [(18, 19, "1/54")]),
        (((12, 0), (14, 1), (18, 0)), [], [(14, 19, "1/54")], []),
        (((12, 0), (14, 2), (18, 0)), [], [(14, 19, "1/54")], []),
    ]
    for triple, expected_u, expected_v, expected_w in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert _decode_e6(uvw.W) == expected_w, triple


def test_predict_dual_anchor_121_overlap_families() -> None:
    samples = [
        (((12, 0), (0, 1), (21, 0)), [(22, 2, "1/108")], [(0, 5, "1/108")]),
        (((12, 0), (0, 2), (21, 0)), [(22, 1, "-1/108")], [(0, 5, "1/108")]),
        (((12, 0), (2, 1), (16, 0)), [(20, 2, "1/108")], [(2, 6, "1/108")]),
        (((12, 0), (2, 2), (16, 0)), [(20, 1, "-1/108")], [(2, 6, "1/108")]),
        (((12, 0), (3, 1), (26, 0)), [(6, 2, "1/108")], [(3, 20, "1/108")]),
        (((12, 0), (3, 2), (26, 0)), [(6, 1, "-1/108")], [(3, 20, "1/108")]),
        (((12, 0), (4, 1), (9, 0)), [(25, 2, "1/108")], [(4, 1, "-1/108")]),
        (((12, 0), (4, 2), (9, 0)), [(25, 1, "-1/108")], [(4, 1, "-1/108")]),
        (((12, 0), (8, 1), (18, 0)), [(13, 2, "1/108")], [(8, 17, "1/108")]),
        (((12, 0), (8, 2), (18, 0)), [(13, 1, "-1/108")], [(8, 17, "1/108")]),
        (((12, 0), (10, 1), (24, 0)), [(5, 2, "1/108")], [(10, 22, "1/108")]),
        (((12, 0), (10, 2), (24, 0)), [(5, 1, "-1/108")], [(10, 22, "1/108")]),
        (((12, 0), (11, 1), (14, 0)), [(17, 2, "1/108")], [(11, 13, "1/108")]),
        (((12, 0), (11, 2), (14, 0)), [(17, 1, "-1/108")], [(11, 13, "1/108")]),
        (((12, 0), (15, 1), (23, 0)), [(1, 2, "-1/108")], [(15, 25, "1/108")]),
        (((12, 0), (15, 2), (23, 0)), [(1, 1, "1/108")], [(15, 25, "1/108")]),
    ]
    for triple, expected_u, expected_v in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_anchor_112_line_families() -> None:
    samples = [
        (((13, 0), (1, 0), (26, 1)), [], [], [(26, 18, "-1/54")]),
        (((13, 0), (1, 0), (26, 2)), [], [], [(26, 18, "-1/54")]),
        (((13, 0), (1, 1), (26, 0)), [], [(1, 18, "-1/54")], []),
        (((13, 0), (1, 2), (26, 0)), [], [(1, 18, "-1/54")], []),
        (((13, 0), (5, 0), (16, 1)), [], [], [(16, 8, "1/54")]),
        (((13, 0), (5, 0), (16, 2)), [], [], [(16, 8, "1/54")]),
        (((13, 0), (5, 1), (16, 0)), [], [(5, 8, "1/54")], []),
        (((13, 0), (5, 2), (16, 0)), [], [(5, 8, "1/54")], []),
        (((13, 0), (6, 0), (15, 1)), [], [], [(15, 8, "-1/54")]),
        (((13, 0), (6, 0), (15, 2)), [], [], [(15, 8, "-1/54")]),
        (((13, 0), (6, 1), (15, 0)), [], [(6, 8, "-1/54")], []),
        (((13, 0), (6, 2), (15, 0)), [], [(6, 8, "-1/54")], []),
        (((13, 0), (7, 0), (14, 1)), [], [], [(14, 8, "-1/54")]),
        (((13, 0), (7, 0), (14, 2)), [], [], [(14, 8, "-1/54")]),
        (((13, 0), (7, 1), (14, 0)), [], [(7, 8, "-1/54")], []),
        (((13, 0), (7, 2), (14, 0)), [], [(7, 8, "-1/54")], []),
        (((13, 0), (9, 0), (22, 1)), [], [], [(22, 18, "1/54")]),
        (((13, 0), (9, 0), (22, 2)), [], [], [(22, 18, "1/54")]),
        (((13, 0), (9, 1), (22, 0)), [], [(9, 18, "1/54")], []),
        (((13, 0), (9, 2), (22, 0)), [], [(9, 18, "1/54")], []),
        (((13, 0), (10, 0), (20, 1)), [], [], [(20, 18, "1/54")]),
        (((13, 0), (10, 0), (20, 2)), [], [], [(20, 18, "1/54")]),
        (((13, 0), (10, 1), (20, 0)), [], [(10, 18, "1/54")], []),
        (((13, 0), (10, 2), (20, 0)), [], [(10, 18, "1/54")], []),
        (((13, 0), (11, 0), (19, 1)), [], [], [(19, 18, "1/54")]),
        (((13, 0), (11, 0), (19, 2)), [], [], [(19, 18, "1/54")]),
        (((13, 0), (11, 1), (19, 0)), [], [(11, 18, "1/54")], []),
        (((13, 0), (11, 2), (19, 0)), [], [(11, 18, "1/54")], []),
    ]
    for triple, expected_u, expected_v, expected_w in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert _decode_e6(uvw.W) == expected_w, triple


def test_predict_dual_anchor_112_overlap_families() -> None:
    samples = [
        (((13, 0), (0, 1), (22, 0)), [(21, 2, "1/108")], [(0, 4, "-1/108")]),
        (((13, 0), (0, 2), (22, 0)), [(21, 1, "-1/108")], [(0, 4, "-1/108")]),
        (((13, 0), (1, 1), (15, 0)), [(23, 2, "-1/108")], [(1, 3, "1/108")]),
        (((13, 0), (1, 2), (15, 0)), [(23, 1, "1/108")], [(1, 3, "1/108")]),
        (((13, 0), (5, 1), (10, 0)), [(24, 2, "1/108")], [(5, 2, "1/108")]),
        (((13, 0), (5, 2), (10, 0)), [(24, 1, "-1/108")], [(5, 2, "1/108")]),
        (((13, 0), (6, 1), (26, 0)), [(3, 2, "1/108")], [(6, 23, "-1/108")]),
        (((13, 0), (6, 2), (26, 0)), [(3, 1, "-1/108")], [(6, 23, "-1/108")]),
        (((13, 0), (7, 1), (19, 0)), [(12, 2, "-1/108")], [(7, 17, "-1/108")]),
        (((13, 0), (7, 2), (19, 0)), [(12, 1, "1/108")], [(7, 17, "-1/108")]),
        (((13, 0), (9, 1), (25, 0)), [(4, 2, "1/108")], [(9, 21, "-1/108")]),
        (((13, 0), (9, 2), (25, 0)), [(4, 1, "-1/108")], [(9, 21, "-1/108")]),
        (((13, 0), (11, 1), (14, 0)), [(17, 2, "1/108")], [(11, 12, "1/108")]),
        (((13, 0), (11, 2), (14, 0)), [(17, 1, "-1/108")], [(11, 12, "1/108")]),
        (((13, 0), (16, 1), (20, 0)), [(2, 2, "1/108")], [(16, 24, "1/108")]),
        (((13, 0), (16, 2), (20, 0)), [(2, 1, "-1/108")], [(16, 24, "1/108")]),
    ]
    for triple, expected_u, expected_v in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_anchor_101_line_families() -> None:
    samples = [
        (((14, 0), (0, 0), (26, 1)), [], [], [(26, 11, "1/54")]),
        (((14, 0), (0, 0), (26, 2)), [], [], [(26, 11, "1/54")]),
        (((14, 0), (0, 1), (26, 0)), [], [(0, 11, "1/54")], []),
        (((14, 0), (0, 2), (26, 0)), [], [(0, 11, "1/54")], []),
        (((14, 0), (2, 0), (25, 1)), [], [], [(25, 17, "-1/54")]),
        (((14, 0), (2, 0), (25, 2)), [], [], [(25, 17, "-1/54")]),
        (((14, 0), (2, 1), (25, 0)), [], [(2, 17, "-1/54")], []),
        (((14, 0), (2, 2), (25, 0)), [], [(2, 17, "-1/54")], []),
        (((14, 0), (5, 0), (23, 1)), [], [], [(23, 17, "1/54")]),
        (((14, 0), (5, 0), (23, 2)), [], [], [(23, 17, "1/54")]),
        (((14, 0), (5, 1), (23, 0)), [], [(5, 17, "1/54")], []),
        (((14, 0), (5, 2), (23, 0)), [], [(5, 17, "1/54")], []),
        (((14, 0), (6, 0), (21, 1)), [], [], [(21, 17, "1/54")]),
        (((14, 0), (6, 0), (21, 2)), [], [], [(21, 17, "1/54")]),
        (((14, 0), (6, 1), (21, 0)), [], [(6, 17, "1/54")], []),
        (((14, 0), (6, 2), (21, 0)), [], [(6, 17, "1/54")], []),
        (((14, 0), (8, 0), (19, 1)), [], [], [(19, 17, "1/54")]),
        (((14, 0), (8, 0), (19, 2)), [], [], [(19, 17, "1/54")]),
        (((14, 0), (8, 1), (19, 0)), [], [(8, 17, "1/54")], []),
        (((14, 0), (8, 2), (19, 0)), [], [(8, 17, "1/54")], []),
        (((14, 0), (9, 0), (16, 1)), [], [], [(16, 11, "-1/54")]),
        (((14, 0), (9, 0), (16, 2)), [], [], [(16, 11, "-1/54")]),
        (((14, 0), (9, 1), (16, 0)), [], [(9, 11, "-1/54")], []),
        (((14, 0), (9, 2), (16, 0)), [], [(9, 11, "-1/54")], []),
        (((14, 0), (10, 0), (15, 1)), [], [], [(15, 11, "1/54")]),
        (((14, 0), (10, 0), (15, 2)), [], [], [(15, 11, "1/54")]),
        (((14, 0), (10, 1), (15, 0)), [], [(10, 11, "1/54")], []),
        (((14, 0), (10, 2), (15, 0)), [], [(10, 11, "1/54")], []),
        (((14, 0), (12, 0), (13, 1)), [], [], [(13, 11, "-1/54")]),
        (((14, 0), (12, 0), (13, 2)), [], [], [(13, 11, "-1/54")]),
        (((14, 0), (12, 1), (13, 0)), [], [(12, 11, "-1/54")], []),
        (((14, 0), (12, 2), (13, 0)), [], [(12, 11, "-1/54")], []),
    ]
    for triple, expected_u, expected_v, expected_w in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert _decode_e6(uvw.W) == expected_w, triple


def test_predict_dual_anchor_101_overlap_families() -> None:
    samples = [
        (((14, 0), (0, 1), (21, 0)), [(22, 2, "1/108")], [(0, 3, "1/108")]),
        (((14, 0), (0, 2), (21, 0)), [(22, 1, "-1/108")], [(0, 3, "1/108")]),
        (((14, 0), (2, 1), (16, 0)), [(20, 2, "1/108")], [(2, 4, "1/108")]),
        (((14, 0), (2, 2), (16, 0)), [(20, 1, "-1/108")], [(2, 4, "1/108")]),
        (((14, 0), (5, 1), (10, 0)), [(24, 2, "1/108")], [(5, 1, "-1/108")]),
        (((14, 0), (5, 2), (10, 0)), [(24, 1, "-1/108")], [(5, 1, "-1/108")]),
        (((14, 0), (6, 1), (26, 0)), [(3, 2, "1/108")], [(6, 22, "1/108")]),
        (((14, 0), (6, 2), (26, 0)), [(3, 1, "-1/108")], [(6, 22, "1/108")]),
        (((14, 0), (8, 1), (13, 0)), [(18, 2, "1/108")], [(8, 7, "1/108")]),
        (((14, 0), (8, 2), (13, 0)), [(18, 1, "-1/108")], [(8, 7, "1/108")]),
        (((14, 0), (9, 1), (25, 0)), [(4, 2, "1/108")], [(9, 20, "1/108")]),
        (((14, 0), (9, 2), (25, 0)), [(4, 1, "-1/108")], [(9, 20, "1/108")]),
        (((14, 0), (12, 1), (19, 0)), [(7, 2, "-1/108")], [(12, 18, "-1/108")]),
        (((14, 0), (12, 2), (19, 0)), [(7, 1, "1/108")], [(12, 18, "-1/108")]),
        (((14, 0), (15, 1), (23, 0)), [(1, 2, "-1/108")], [(15, 24, "1/108")]),
        (((14, 0), (15, 2), (23, 0)), [(1, 1, "1/108")], [(15, 24, "1/108")]),
    ]
    for triple, expected_u, expected_v in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_anchor_021_line_families() -> None:
    samples = [
        (((15, 0), (0, 0), (20, 1)), [], [], [(20, 1, "1/54")]),
        (((15, 0), (0, 0), (20, 2)), [], [], [(20, 1, "1/54")]),
        (((15, 0), (0, 1), (20, 0)), [], [(0, 1, "1/54")], []),
        (((15, 0), (0, 2), (20, 0)), [], [(0, 1, "1/54")], []),
        (((15, 0), (3, 0), (13, 1)), [], [], [(13, 1, "-1/54")]),
        (((15, 0), (3, 0), (13, 2)), [], [], [(13, 1, "-1/54")]),
        (((15, 0), (3, 1), (13, 0)), [], [(3, 1, "-1/54")], []),
        (((15, 0), (3, 2), (13, 0)), [], [(3, 1, "-1/54")], []),
        (((15, 0), (5, 0), (11, 1)), [], [], [(11, 1, "-1/54")]),
        (((15, 0), (5, 0), (11, 2)), [], [], [(11, 1, "-1/54")]),
        (((15, 0), (5, 1), (11, 0)), [], [(5, 1, "-1/54")], []),
        (((15, 0), (5, 2), (11, 0)), [], [(5, 1, "-1/54")], []),
        (((15, 0), (7, 0), (9, 1)), [], [], [(9, 1, "1/54")]),
        (((15, 0), (7, 0), (9, 2)), [], [], [(9, 1, "1/54")]),
        (((15, 0), (7, 1), (9, 0)), [], [(7, 1, "1/54")], []),
        (((15, 0), (7, 2), (9, 0)), [], [(7, 1, "1/54")], []),
        (((15, 0), (8, 0), (26, 1)), [], [], [(26, 23, "1/54")]),
        (((15, 0), (8, 0), (26, 2)), [], [], [(26, 23, "1/54")]),
        (((15, 0), (8, 1), (26, 0)), [], [(8, 23, "1/54")], []),
        (((15, 0), (8, 2), (26, 0)), [], [(8, 23, "1/54")], []),
        (((15, 0), (12, 0), (25, 1)), [], [], [(25, 23, "-1/54")]),
        (((15, 0), (12, 0), (25, 2)), [], [], [(25, 23, "-1/54")]),
        (((15, 0), (12, 1), (25, 0)), [], [(12, 23, "-1/54")], []),
        (((15, 0), (12, 2), (25, 0)), [], [(12, 23, "-1/54")], []),
        (((15, 0), (14, 0), (24, 1)), [], [], [(24, 23, "-1/54")]),
        (((15, 0), (14, 0), (24, 2)), [], [], [(24, 23, "-1/54")]),
        (((15, 0), (14, 1), (24, 0)), [], [(14, 23, "-1/54")], []),
        (((15, 0), (14, 2), (24, 0)), [], [(14, 23, "-1/54")], []),
        (((15, 0), (16, 0), (21, 1)), [], [], [(21, 23, "1/54")]),
        (((15, 0), (16, 0), (21, 2)), [], [], [(21, 23, "1/54")]),
        (((15, 0), (16, 1), (21, 0)), [], [(16, 23, "1/54")], []),
        (((15, 0), (16, 2), (21, 0)), [], [(16, 23, "1/54")], []),
    ]
    for triple, expected_u, expected_v, expected_w in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert _decode_e6(uvw.W) == expected_w, triple


def test_predict_dual_anchor_021_overlap_families() -> None:
    samples = [
        (((15, 0), (0, 1), (21, 0)), [(22, 2, "1/108")], [(0, 2, "-1/108")]),
        (((15, 0), (0, 2), (21, 0)), [(22, 1, "-1/108")], [(0, 2, "-1/108")]),
        (((15, 0), (3, 1), (26, 0)), [(6, 2, "1/108")], [(3, 18, "1/108")]),
        (((15, 0), (3, 2), (26, 0)), [(6, 1, "-1/108")], [(3, 18, "1/108")]),
        (((15, 0), (5, 1), (24, 0)), [(10, 2, "1/108")], [(5, 17, "-1/108")]),
        (((15, 0), (5, 2), (24, 0)), [(10, 1, "-1/108")], [(5, 17, "-1/108")]),
        (((15, 0), (7, 1), (12, 0)), [(19, 2, "-1/108")], [(7, 4, "1/108")]),
        (((15, 0), (7, 2), (12, 0)), [(19, 1, "1/108")], [(7, 4, "1/108")]),
        (((15, 0), (8, 1), (13, 0)), [(18, 2, "1/108")], [(8, 6, "1/108")]),
        (((15, 0), (8, 2), (13, 0)), [(18, 1, "-1/108")], [(8, 6, "1/108")]),
        (((15, 0), (9, 1), (25, 0)), [(4, 2, "1/108")], [(9, 19, "-1/108")]),
        (((15, 0), (9, 2), (25, 0)), [(4, 1, "-1/108")], [(9, 19, "-1/108")]),
        (((15, 0), (11, 1), (14, 0)), [(17, 2, "1/108")], [(11, 10, "-1/108")]),
        (((15, 0), (11, 2), (14, 0)), [(17, 1, "-1/108")], [(11, 10, "-1/108")]),
        (((15, 0), (16, 1), (20, 0)), [(2, 2, "1/108")], [(16, 22, "-1/108")]),
        (((15, 0), (16, 2), (20, 0)), [(2, 1, "-1/108")], [(16, 22, "-1/108")]),
    ]
    for triple, expected_u, expected_v in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_anchor_011_line_families() -> None:
    samples = [
        (((16, 0), (0, 0), (23, 1)), [], [], [(23, 2, "-1/54")]),
        (((16, 0), (0, 0), (23, 2)), [], [], [(23, 2, "-1/54")]),
        (((16, 0), (0, 1), (23, 0)), [], [(0, 2, "-1/54")], []),
        (((16, 0), (0, 2), (23, 0)), [], [(0, 2, "-1/54")], []),
        (((16, 0), (4, 0), (14, 1)), [], [], [(14, 2, "-1/54")]),
        (((16, 0), (4, 0), (14, 2)), [], [], [(14, 2, "-1/54")]),
        (((16, 0), (4, 1), (14, 0)), [], [(4, 2, "-1/54")], []),
        (((16, 0), (4, 2), (14, 0)), [], [(4, 2, "-1/54")], []),
        (((16, 0), (6, 0), (12, 1)), [], [], [(12, 2, "-1/54")]),
        (((16, 0), (6, 0), (12, 2)), [], [], [(12, 2, "-1/54")]),
        (((16, 0), (6, 1), (12, 0)), [], [(6, 2, "-1/54")], []),
        (((16, 0), (6, 2), (12, 0)), [], [(6, 2, "-1/54")], []),
        (((16, 0), (7, 0), (26, 1)), [], [], [(26, 20, "1/54")]),
        (((16, 0), (7, 0), (26, 2)), [], [], [(26, 20, "1/54")]),
        (((16, 0), (7, 1), (26, 0)), [], [(7, 20, "1/54")], []),
        (((16, 0), (7, 2), (26, 0)), [], [(7, 20, "1/54")], []),
        (((16, 0), (8, 0), (10, 1)), [], [], [(10, 2, "1/54")]),
        (((16, 0), (8, 0), (10, 2)), [], [], [(10, 2, "1/54")]),
        (((16, 0), (8, 1), (10, 0)), [], [(8, 2, "1/54")], []),
        (((16, 0), (8, 2), (10, 0)), [], [(8, 2, "1/54")], []),
        (((16, 0), (11, 0), (25, 1)), [], [], [(25, 20, "-1/54")]),
        (((16, 0), (11, 0), (25, 2)), [], [], [(25, 20, "-1/54")]),
        (((16, 0), (11, 1), (25, 0)), [], [(11, 20, "-1/54")], []),
        (((16, 0), (11, 2), (25, 0)), [], [(11, 20, "-1/54")], []),
        (((16, 0), (13, 0), (24, 1)), [], [], [(24, 20, "-1/54")]),
        (((16, 0), (13, 0), (24, 2)), [], [], [(24, 20, "-1/54")]),
        (((16, 0), (13, 1), (24, 0)), [], [(13, 20, "-1/54")], []),
        (((16, 0), (13, 2), (24, 0)), [], [(13, 20, "-1/54")], []),
        (((16, 0), (15, 0), (22, 1)), [], [], [(22, 20, "1/54")]),
        (((16, 0), (15, 0), (22, 2)), [], [], [(22, 20, "1/54")]),
        (((16, 0), (15, 1), (22, 0)), [], [(15, 20, "1/54")], []),
        (((16, 0), (15, 2), (22, 0)), [], [(15, 20, "1/54")], []),
    ]
    for triple, expected_u, expected_v, expected_w in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert _decode_e6(uvw.W) == expected_w, triple


def test_predict_dual_anchor_011_overlap_families() -> None:
    samples = [
        (((16, 0), (0, 1), (22, 0)), [(21, 2, "1/108")], [(0, 1, "1/108")]),
        (((16, 0), (0, 2), (22, 0)), [(21, 1, "-1/108")], [(0, 1, "1/108")]),
        (((16, 0), (4, 1), (25, 0)), [(9, 2, "1/108")], [(4, 17, "1/108")]),
        (((16, 0), (4, 2), (25, 0)), [(9, 1, "-1/108")], [(4, 17, "1/108")]),
        (((16, 0), (6, 1), (26, 0)), [(3, 2, "1/108")], [(6, 19, "1/108")]),
        (((16, 0), (6, 2), (26, 0)), [(3, 1, "-1/108")], [(6, 19, "1/108")]),
        (((16, 0), (7, 1), (12, 0)), [(19, 2, "-1/108")], [(7, 3, "-1/108")]),
        (((16, 0), (7, 2), (12, 0)), [(19, 1, "1/108")], [(7, 3, "-1/108")]),
        (((16, 0), (8, 1), (13, 0)), [(18, 2, "1/108")], [(8, 5, "-1/108")]),
        (((16, 0), (8, 2), (13, 0)), [(18, 1, "-1/108")], [(8, 5, "-1/108")]),
        (((16, 0), (10, 1), (24, 0)), [(5, 2, "1/108")], [(10, 18, "-1/108")]),
        (((16, 0), (10, 2), (24, 0)), [(5, 1, "-1/108")], [(10, 18, "-1/108")]),
        (((16, 0), (11, 1), (14, 0)), [(17, 2, "1/108")], [(11, 9, "1/108")]),
        (((16, 0), (11, 2), (14, 0)), [(17, 1, "-1/108")], [(11, 9, "1/108")]),
        (((16, 0), (15, 1), (23, 0)), [(1, 2, "-1/108")], [(15, 21, "-1/108")]),
        (((16, 0), (15, 2), (23, 0)), [(1, 1, "1/108")], [(15, 21, "-1/108")]),
    ]
    for triple, expected_u, expected_v in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_anchor_100_line_families() -> None:
    samples = [
        (((17, 0), (1, 0), (24, 1)), [], [], [(24, 11, "1/54")]),
        (((17, 0), (1, 0), (24, 2)), [], [], [(24, 11, "1/54")]),
        (((17, 0), (1, 1), (24, 0)), [], [(1, 11, "1/54")], []),
        (((17, 0), (1, 2), (24, 0)), [], [(1, 11, "1/54")], []),
        (((17, 0), (2, 0), (25, 1)), [], [], [(25, 14, "-1/54")]),
        (((17, 0), (2, 0), (25, 2)), [], [], [(25, 14, "-1/54")]),
        (((17, 0), (2, 1), (25, 0)), [], [(2, 14, "-1/54")], []),
        (((17, 0), (2, 2), (25, 0)), [], [(2, 14, "-1/54")], []),
        (((17, 0), (3, 0), (22, 1)), [], [], [(22, 11, "-1/54")]),
        (((17, 0), (3, 0), (22, 2)), [], [], [(22, 11, "-1/54")]),
        (((17, 0), (3, 1), (22, 0)), [], [(3, 11, "-1/54")], []),
        (((17, 0), (3, 2), (22, 0)), [], [(3, 11, "-1/54")], []),
        (((17, 0), (4, 0), (20, 1)), [], [], [(20, 11, "-1/54")]),
        (((17, 0), (4, 0), (20, 2)), [], [], [(20, 11, "-1/54")]),
        (((17, 0), (4, 1), (20, 0)), [], [(4, 11, "-1/54")], []),
        (((17, 0), (4, 2), (20, 0)), [], [(4, 11, "-1/54")], []),
        (((17, 0), (5, 0), (23, 1)), [], [], [(23, 14, "1/54")]),
        (((17, 0), (5, 0), (23, 2)), [], [], [(23, 14, "1/54")]),
        (((17, 0), (5, 1), (23, 0)), [], [(5, 14, "1/54")], []),
        (((17, 0), (5, 2), (23, 0)), [], [(5, 14, "1/54")], []),
        (((17, 0), (6, 0), (21, 1)), [], [], [(21, 14, "1/54")]),
        (((17, 0), (6, 0), (21, 2)), [], [], [(21, 14, "1/54")]),
        (((17, 0), (6, 1), (21, 0)), [], [(6, 14, "1/54")], []),
        (((17, 0), (6, 2), (21, 0)), [], [(6, 14, "1/54")], []),
        (((17, 0), (7, 0), (18, 1)), [], [], [(18, 11, "-1/54")]),
        (((17, 0), (7, 0), (18, 2)), [], [], [(18, 11, "-1/54")]),
        (((17, 0), (7, 1), (18, 0)), [], [(7, 11, "-1/54")], []),
        (((17, 0), (7, 2), (18, 0)), [], [(7, 11, "-1/54")], []),
        (((17, 0), (8, 0), (19, 1)), [], [], [(19, 14, "1/54")]),
        (((17, 0), (8, 0), (19, 2)), [], [], [(19, 14, "1/54")]),
        (((17, 0), (8, 1), (19, 0)), [], [(8, 14, "1/54")], []),
        (((17, 0), (8, 2), (19, 0)), [], [(8, 14, "1/54")], []),
    ]
    for triple, expected_u, expected_v, expected_w in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert _decode_e6(uvw.W) == expected_w, triple


def test_predict_dual_anchor_100_overlap_families() -> None:
    samples = [
        (((17, 0), (1, 1), (23, 0)), [(15, 2, "-1/108")], [(1, 10, "1/108")]),
        (((17, 0), (1, 2), (23, 0)), [(15, 1, "1/108")], [(1, 10, "1/108")]),
        (((17, 0), (2, 1), (20, 0)), [(16, 2, "1/108")], [(2, 9, "1/108")]),
        (((17, 0), (2, 2), (20, 0)), [(16, 1, "-1/108")], [(2, 9, "1/108")]),
        (((17, 0), (3, 1), (6, 0)), [(26, 2, "1/108")], [(3, 0, "-1/108")]),
        (((17, 0), (3, 2), (6, 0)), [(26, 1, "-1/108")], [(3, 0, "-1/108")]),
        (((17, 0), (4, 1), (25, 0)), [(9, 2, "1/108")], [(4, 16, "1/108")]),
        (((17, 0), (4, 2), (25, 0)), [(9, 1, "-1/108")], [(4, 16, "1/108")]),
        (((17, 0), (5, 1), (24, 0)), [(10, 2, "1/108")], [(5, 15, "-1/108")]),
        (((17, 0), (5, 2), (24, 0)), [(10, 1, "-1/108")], [(5, 15, "-1/108")]),
        (((17, 0), (7, 1), (19, 0)), [(12, 2, "-1/108")], [(7, 13, "-1/108")]),
        (((17, 0), (7, 2), (19, 0)), [(12, 1, "1/108")], [(7, 13, "-1/108")]),
        (((17, 0), (8, 1), (18, 0)), [(13, 2, "1/108")], [(8, 12, "1/108")]),
        (((17, 0), (8, 2), (18, 0)), [(13, 1, "-1/108")], [(8, 12, "1/108")]),
        (((17, 0), (21, 1), (22, 0)), [(0, 2, "1/108")], [(21, 26, "-1/108")]),
        (((17, 0), (21, 2), (22, 0)), [(0, 1, "-1/108")], [(21, 26, "-1/108")]),
    ]
    for triple, expected_u, expected_v in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_a10_polynomial_line_family_direct() -> None:
    w_samples = [
        (((17, 0), (1, 0), (24, 1)), [(24, 11, "1/54")]),
        (((14, 0), (0, 0), (26, 1)), [(26, 11, "1/54")]),
        (((11, 0), (10, 0), (15, 1)), [(15, 14, "1/54")]),
    ]
    for triple, expected_w in w_samples:
        uvw = predict_dual_a10_line_w_family_uvw(*triple)
        assert uvw is not None, triple
        assert uvw.U == [], triple
        assert uvw.V == [], triple
        assert _decode_e6(uvw.W) == expected_w, triple

    v_samples = [
        (((17, 0), (1, 1), (24, 0)), [(1, 11, "1/54")]),
        (((14, 0), (9, 1), (16, 0)), [(9, 11, "-1/54")]),
        (((11, 0), (10, 1), (15, 0)), [(10, 14, "1/54")]),
    ]
    for triple, expected_v in v_samples:
        uvw = predict_dual_a10_line_v_family_uvw(*triple)
        assert uvw is not None, triple
        assert uvw.U == [], triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_a10_polynomial_overlap_family_direct() -> None:
    samples = [
        (((17, 0), (1, 1), (23, 0)), [(15, 2, "-1/108")], [(1, 10, "1/108")]),
        (((14, 0), (5, 1), (10, 0)), [(24, 2, "1/108")], [(5, 1, "-1/108")]),
        (((11, 0), (16, 1), (20, 0)), [(2, 2, "1/108")], [(16, 25, "1/108")]),
    ]
    for triple, expected_u, expected_v in samples:
        uvw = predict_dual_a10_overlap_uv_family_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_a10_polynomial_family_lifts_to_other_g1_colors() -> None:
    w_samples = [
        (((17, 1), (1, 1), (24, 0)), [(24, 11, "1/54")]),
        (((17, 1), (1, 1), (24, 2)), [(24, 11, "1/54")]),
    ]
    for triple, expected_w in w_samples:
        uvw = predict_dual_a10_line_w_family_uvw(*triple)
        assert uvw is not None, triple
        assert uvw.U == [], triple
        assert uvw.V == [], triple
        assert _decode_e6(uvw.W) == expected_w, triple

    v_samples = [
        (((17, 1), (1, 0), (24, 1)), [(1, 11, "1/54")]),
        (((17, 1), (1, 2), (24, 1)), [(1, 11, "1/54")]),
    ]
    for triple, expected_v in v_samples:
        uvw = predict_dual_a10_line_v_family_uvw(*triple)
        assert uvw is not None, triple
        assert uvw.U == [], triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_a11_polynomial_line_family_direct() -> None:
    w_samples = [
        (((18, 0), (1, 0), (26, 1)), [(26, 13, "-1/54")]),
        (((8, 0), (0, 0), (25, 1)), [(25, 13, "-1/54")]),
        (((13, 0), (10, 0), (20, 1)), [(20, 18, "1/54")]),
    ]
    for triple, expected_w in w_samples:
        uvw = predict_dual_a11_line_w_family_uvw(*triple)
        assert uvw is not None, triple
        assert uvw.U == [], triple
        assert uvw.V == [], triple
        assert _decode_e6(uvw.W) == expected_w, triple

    v_samples = [
        (((18, 0), (1, 1), (26, 0)), [(1, 13, "-1/54")]),
        (((8, 0), (3, 1), (23, 0)), [(3, 18, "1/54")]),
        (((13, 0), (11, 1), (19, 0)), [(11, 18, "1/54")]),
    ]
    for triple, expected_v in v_samples:
        uvw = predict_dual_a11_line_v_family_uvw(*triple)
        assert uvw is not None, triple
        assert uvw.U == [], triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_a11_polynomial_overlap_family_direct() -> None:
    samples = [
        (((18, 0), (1, 1), (23, 0)), [(15, 2, "-1/108")], [(1, 6, "-1/108")]),
        (((8, 0), (4, 1), (25, 0)), [(9, 2, "1/108")], [(4, 22, "-1/108")]),
        (((13, 0), (11, 1), (14, 0)), [(17, 2, "1/108")], [(11, 12, "1/108")]),
    ]
    for triple, expected_u, expected_v in samples:
        uvw = predict_dual_a11_overlap_uv_family_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_a11_polynomial_family_lifts_to_other_g1_colors() -> None:
    w_samples = [
        (((18, 1), (1, 1), (26, 0)), [(26, 13, "-1/54")]),
        (((18, 1), (1, 1), (26, 2)), [(26, 13, "-1/54")]),
    ]
    for triple, expected_w in w_samples:
        uvw = predict_dual_a11_line_w_family_uvw(*triple)
        assert uvw is not None, triple
        assert uvw.U == [], triple
        assert uvw.V == [], triple
        assert _decode_e6(uvw.W) == expected_w, triple

    v_samples = [
        (((18, 1), (1, 0), (26, 1)), [(1, 13, "-1/54")]),
        (((18, 1), (1, 2), (26, 1)), [(1, 13, "-1/54")]),
    ]
    for triple, expected_v in v_samples:
        uvw = predict_dual_a11_line_v_family_uvw(*triple)
        assert uvw is not None, triple
        assert uvw.U == [], triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple

    overlap_samples = [
        (((18, 1), (1, 0), (23, 1)), [(15, 2, "1/108")], [(1, 6, "-1/108")]),
        (((18, 1), (1, 2), (23, 1)), [(15, 0, "-1/108")], [(1, 6, "-1/108")]),
    ]
    for triple, expected_u, expected_v in overlap_samples:
        uvw = predict_dual_a11_overlap_uv_family_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_a12_polynomial_line_family_direct() -> None:
    w_samples = [
        (((19, 0), (1, 0), (25, 1)), [(25, 7, "-1/54")]),
        (((12, 0), (10, 0), (21, 1)), [(21, 19, "1/54")]),
        (((7, 0), (5, 0), (22, 1)), [(22, 19, "1/54")]),
    ]
    for triple, expected_w in w_samples:
        uvw = predict_dual_a12_line_w_family_uvw(*triple)
        assert uvw is not None, triple
        assert uvw.U == [], triple
        assert uvw.V == [], triple
        assert _decode_e6(uvw.W) == expected_w, triple

    v_samples = [
        (((19, 0), (1, 1), (25, 0)), [(1, 7, "-1/54")]),
        (((12, 0), (10, 1), (21, 0)), [(10, 19, "1/54")]),
        (((7, 0), (5, 1), (22, 0)), [(5, 19, "1/54")]),
    ]
    for triple, expected_v in v_samples:
        uvw = predict_dual_a12_line_v_family_uvw(*triple)
        assert uvw is not None, triple
        assert uvw.U == [], triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_a12_polynomial_overlap_family_direct() -> None:
    samples = [
        (((19, 0), (1, 1), (23, 0)), [(15, 2, "-1/108")], [(1, 4, "1/108")]),
        (((12, 0), (10, 1), (24, 0)), [(5, 2, "1/108")], [(10, 22, "1/108")]),
        (((7, 0), (11, 1), (17, 0)), [(14, 2, "1/108")], [(11, 18, "1/108")]),
    ]
    for triple, expected_u, expected_v in samples:
        uvw = predict_dual_a12_overlap_uv_family_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_a12_polynomial_family_lifts_to_other_g1_colors() -> None:
    w_samples = [
        (((19, 1), (1, 1), (25, 0)), [(25, 7, "-1/54")]),
        (((19, 1), (1, 1), (25, 2)), [(25, 7, "-1/54")]),
    ]
    for triple, expected_w in w_samples:
        uvw = predict_dual_a12_line_w_family_uvw(*triple)
        assert uvw is not None, triple
        assert uvw.U == [], triple
        assert uvw.V == [], triple
        assert _decode_e6(uvw.W) == expected_w, triple

    v_samples = [
        (((19, 1), (1, 0), (25, 1)), [(1, 7, "-1/54")]),
        (((19, 1), (1, 2), (25, 1)), [(1, 7, "-1/54")]),
    ]
    for triple, expected_v in v_samples:
        uvw = predict_dual_a12_line_v_family_uvw(*triple)
        assert uvw is not None, triple
        assert uvw.U == [], triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple

    overlap_samples = [
        (((19, 1), (1, 0), (23, 1)), [(15, 2, "1/108")], [(1, 4, "1/108")]),
        (((19, 1), (1, 2), (23, 1)), [(15, 0, "-1/108")], [(1, 4, "1/108")]),
    ]
    for triple, expected_u, expected_v in overlap_samples:
        uvw = predict_dual_a12_overlap_uv_family_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_a01_polynomial_line_family_direct() -> None:
    w_samples = [
        (((20, 0), (1, 0), (21, 1)), [(21, 2, "-1/54")]),
        (((16, 0), (8, 0), (10, 1)), [(10, 2, "1/54")]),
        (((2, 0), (5, 0), (18, 1)), [(18, 20, "1/54")]),
    ]
    for triple, expected_w in w_samples:
        uvw = predict_dual_a01_line_w_family_uvw(*triple)
        assert uvw is not None, triple
        assert uvw.U == [], triple
        assert uvw.V == [], triple
        assert _decode_e6(uvw.W) == expected_w, triple

    v_samples = [
        (((20, 0), (1, 1), (21, 0)), [(1, 2, "-1/54")]),
        (((16, 0), (8, 1), (10, 0)), [(8, 2, "1/54")]),
        (((2, 0), (5, 1), (18, 0)), [(5, 20, "1/54")]),
    ]
    for triple, expected_v in v_samples:
        uvw = predict_dual_a01_line_v_family_uvw(*triple)
        assert uvw is not None, triple
        assert uvw.U == [], triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_a01_polynomial_overlap_family_direct() -> None:
    samples = [
        (((16, 0), (10, 1), (24, 0)), [(5, 2, "1/108")], [(10, 18, "-1/108")]),
        (((2, 0), (5, 1), (10, 0)), [(24, 2, "1/108")], [(5, 13, "1/108")]),
    ]
    for triple, expected_u, expected_v in samples:
        uvw = predict_dual_a01_overlap_uv_family_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_a01_polynomial_family_lifts_on_az0_line_branch() -> None:
    w_samples = [
        (((20, 1), (1, 1), (21, 0)), [(21, 2, "-1/54")]),
        (((20, 2), (1, 2), (21, 0)), [(21, 2, "-1/54")]),
    ]
    for triple, expected_w in w_samples:
        uvw = predict_dual_a01_line_w_family_uvw(*triple)
        assert uvw is not None, triple
        assert uvw.U == [], triple
        assert uvw.V == [], triple
        assert _decode_e6(uvw.W) == expected_w, triple

    v_samples = [
        (((20, 1), (1, 0), (21, 1)), [(1, 2, "-1/54")]),
        (((20, 2), (1, 0), (21, 2)), [(1, 2, "-1/54")]),
    ]
    for triple, expected_v in v_samples:
        uvw = predict_dual_a01_line_v_family_uvw(*triple)
        assert uvw is not None, triple
        assert uvw.U == [], triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_a01_polynomial_family_leaves_inactive_shadow_cases_unclaimed() -> None:
    samples = [
        (((20, 0), (0, 1), (21, 0)), predict_dual_a01_overlap_uv_family_uvw),
        (((20, 1), (0, 0), (21, 1)), predict_dual_a01_overlap_uv_family_uvw),
        (((20, 1), (0, 1), (23, 0)), predict_dual_a01_line_w_family_uvw),
        (((20, 1), (0, 0), (23, 1)), predict_dual_a01_line_v_family_uvw),
        (((20, 1), (1, 2), (21, 0)), predict_dual_a01_line_w_family_uvw),
        (((2, 0), (0, 1), (22, 0)), predict_dual_g1g2g2_uvw),
        (((2, 1), (0, 0), (22, 1)), predict_dual_g1g2g2_uvw),
    ]
    for triple, fn in samples:
        assert fn(*triple) is None, triple


def test_predict_dual_a01_b00_reflection_u_family() -> None:
    samples = [
        (((16, 0), (0, 0), (24, 1)), [(19, 2, "-1/6")]),
        (((16, 0), (0, 0), (25, 2)), [(18, 1, "-1/6")]),
        (((2, 0), (0, 0), (17, 1)), [(26, 2, "-1/6")]),
        (((2, 0), (0, 0), (18, 2)), [(25, 1, "-1/6")]),
        (((16, 1), (0, 1), (24, 0)), [(19, 2, "1/6")]),
        (((2, 1), (0, 1), (17, 0)), [(26, 2, "1/6")]),
    ]
    for triple, expected_u in samples:
        uvw = predict_dual_a01_b00_reflection_u_family_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert uvw.V == [], triple
        assert uvw.W == [], triple


def test_predict_dual_a01_b0_reflection_uv12_family() -> None:
    samples = [
        (((16, 0), (0, 1), (24, 0)), [(19, 2, "1/12")], [(0, 3, "1/12")]),
        (((16, 0), (0, 2), (25, 0)), [(18, 1, "1/12")], [(0, 5, "1/12")]),
        (((2, 0), (0, 1), (17, 0)), [(26, 2, "1/12")], [(0, 7, "-1/12")]),
        (((2, 1), (0, 2), (17, 1)), [(26, 0, "1/12")], [(0, 7, "-1/12")]),
    ]
    for triple, expected_u, expected_v in samples:
        uvw = predict_dual_a01_b0_reflection_uv12_family_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple

    overlap_samples = [
        (((19, 1), (1, 0), (23, 1)), [(15, 2, "1/108")], [(1, 4, "1/108")]),
        (((19, 1), (1, 2), (23, 1)), [(15, 0, "-1/108")], [(1, 4, "1/108")]),
    ]
    for triple, expected_u, expected_v in overlap_samples:
        uvw = predict_dual_a12_overlap_uv_family_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple

    overlap_samples = [
        (((17, 1), (1, 0), (23, 1)), [(15, 2, "1/108")], [(1, 10, "1/108")]),
        (((17, 1), (1, 2), (23, 1)), [(15, 0, "-1/108")], [(1, 10, "1/108")]),
    ]
    for triple, expected_u, expected_v in overlap_samples:
        uvw = predict_dual_a10_overlap_uv_family_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_a01_source1_line_u_family() -> None:
    samples = [
        (((2, 0), (1, 0), (8, 1)), [(26, 2, "1/6")]),
        (((2, 0), (1, 0), (12, 1)), [(25, 2, "-1/6")]),
        (((2, 1), (1, 1), (8, 0)), [(26, 2, "-1/6")]),
        (((2, 2), (1, 2), (14, 0)), [(24, 1, "-1/6")]),
    ]
    for triple, expected_u in samples:
        uvw = predict_dual_a01_source1_line_u_family_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert uvw.V == [], triple
        assert uvw.W == [], triple


def test_predict_dual_a01_source1_line_uv12_family() -> None:
    samples = [
        (((2, 0), (1, 1), (8, 0)), [(26, 2, "-1/12")], [(1, 7, "1/12")]),
        (((2, 0), (1, 2), (12, 0)), [(25, 1, "-1/12")], [(1, 11, "1/12")]),
        (((2, 1), (1, 0), (8, 1)), [(26, 2, "1/12")], [(1, 7, "1/12")]),
        (((2, 2), (1, 1), (14, 2)), [(24, 0, "-1/12")], [(1, 13, "1/12")]),
    ]
    for triple, expected_u, expected_v in samples:
        uvw = predict_dual_a01_source1_line_uv12_family_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_a01_source1_z0_line_u_family() -> None:
    samples = [
        (((20, 0), (1, 0), (24, 1)), [(14, 2, "-1/6")]),
        (((20, 0), (1, 0), (25, 1)), [(12, 2, "-1/6")]),
        (((20, 1), (1, 1), (24, 2)), [(14, 0, "-1/6")]),
        (((20, 2), (1, 2), (26, 0)), [(8, 1, "1/6")]),
    ]
    for triple, expected_u in samples:
        uvw = predict_dual_a01_source1_z0_line_u_family_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert uvw.V == [], triple
        assert uvw.W == [], triple


def test_predict_dual_a01_source1_z0_line_uv12_family() -> None:
    samples = [
        (((20, 0), (1, 1), (24, 0)), [(14, 2, "1/12")], [(1, 4, "1/12")]),
        (((20, 0), (1, 2), (26, 0)), [(8, 1, "1/12")], [(1, 10, "1/12")]),
        (((20, 1), (1, 0), (24, 1)), [(14, 2, "-1/12")], [(1, 4, "1/12")]),
        (((20, 2), (1, 1), (25, 2)), [(12, 0, "-1/12")], [(1, 6, "1/12")]),
    ]
    for triple, expected_u, expected_v in samples:
        uvw = predict_dual_a01_source1_z0_line_uv12_family_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_e6(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_a01_sameid_source_color_uv12_family() -> None:
    samples = [
        (((20, 0), (0, 0), (20, 1)), [(23, 2, "1/12")], [("sl3", 0, 1, "1/12")]),
        (((20, 0), (0, 0), (20, 2)), [(23, 1, "-1/12")], [("sl3", 0, 2, "1/12")]),
        (((16, 0), (1, 0), (16, 1)), [(21, 2, "1/12")], [("sl3", 0, 1, "1/12")]),
        (((16, 1), (1, 1), (16, 0)), [(21, 2, "-1/12")], [("sl3", 1, 0, "1/12")]),
    ]
    for triple, expected_u, expected_v in samples:
        uvw = predict_dual_a01_sameid_source_color_uv12_family_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_sparse(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_a01_sameid_source_diag_uv18_family() -> None:
    samples = [
        (
            ((20, 0), (0, 1), (20, 0)),
            [(23, 2, "-1/18")],
            [("e6", 0, 0, "-1/18"), ("sl3", 1, 1, "-1/18")],
        ),
        (
            ((20, 0), (0, 2), (20, 0)),
            [(23, 1, "1/18")],
            [("e6", 0, 0, "-1/18"), ("sl3", 2, 2, "-1/18")],
        ),
        (
            ((16, 0), (1, 1), (16, 0)),
            [(21, 2, "-1/18")],
            [("e6", 1, 1, "-1/18"), ("sl3", 1, 1, "-1/18")],
        ),
        (
            ((16, 2), (1, 0), (16, 2)),
            [(21, 1, "-1/18")],
            [("e6", 1, 1, "-1/18"), ("sl3", 0, 0, "-1/18")],
        ),
    ]
    for triple, expected_u, expected_v in samples:
        uvw = predict_dual_a01_sameid_source_diag_uv18_family_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_sparse(uvw.V) == expected_v, triple
        assert uvw.W == [], triple


def test_predict_dual_samefiber_partner_v_family() -> None:
    samples = [
        (((6, 0), (3, 0), (6, 1)), [], [("sl3", 0, 1, "-1/54")], []),
        (((6, 0), (3, 1), (6, 0)), [], [("e6", 3, 3, "1/108"), ("sl3", 1, 1, "1/108")], []),
        (((9, 0), (4, 0), (9, 1)), [], [("sl3", 0, 1, "-1/54")], []),
        (((9, 0), (4, 1), (9, 0)), [], [("e6", 4, 4, "1/108"), ("sl3", 1, 1, "1/108")], []),
    ]
    for triple, expected_u, expected_v, expected_w in samples:
        uvw = predict_dual_g1g2g2_uvw(*triple)
        assert uvw is not None, triple
        assert _decode_g1(uvw.U) == expected_u, triple
        assert _decode_sparse(uvw.V) == expected_v, triple
        assert _decode_e6(uvw.W) == expected_w, triple


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
