from exploration.w33_transport_curvature_bridge import (
    build_transport_curvature_summary,
)


def test_transport_triangle_curvature_realizes_all_six_reduced_holonomies():
    summary = build_transport_curvature_summary()
    curvature = summary["transport_triangle_curvature"]

    assert curvature["triangles"] == 5280
    assert curvature["all_six_reduced_holonomy_classes_realized"] is True
    assert curvature["adapted_holonomy_counts"] == {
        "[[1, 0], [0, 1]]": 528,
        "[[1, 0], [0, 2]]": 766,
        "[[1, 1], [0, 1]]": 1317,
        "[[1, 1], [0, 2]]": 670,
        "[[1, 2], [0, 1]]": 1275,
        "[[1, 2], [0, 2]]": 724,
    }


def test_curvature_is_rank_zero_only_on_identity_holonomy_triangles():
    summary = build_transport_curvature_summary()
    curvature = summary["transport_triangle_curvature"]

    assert curvature["curvature_rank_counts"] == {0: 528, 1: 4752}
    assert curvature["curvature_vanishes_exactly_on_identity_holonomy_triangles"] is True


def test_global_curvature_operator_has_rank_42():
    summary = build_transport_curvature_summary()
    operator = summary["global_curvature_operator"]

    assert operator["shape"] == [10560, 90]
    assert operator["rank"] == 42
    assert operator["nullity"] == 48
