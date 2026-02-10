from src.toe_protocol import (
    TheoryCandidate,
    toe_readiness_score,
    toe_status_label,
    weakest_link,
)


def test_score_is_weighted_and_clamped():
    c = TheoryCandidate(
        name="test",
        reproduces_gravity=1.2,
        reproduces_standard_model=0.8,
        dark_sector_explanatory_power=-0.2,
        quantitative_predictions=0.5,
        consistency_and_uv_completion=0.25,
    )

    # clamped score:
    # 0.20*1.0 + 0.25*0.8 + 0.15*0.0 + 0.20*0.5 + 0.20*0.25 = 0.55
    assert toe_readiness_score(c) == 0.55


def test_status_label_thresholds():
    assert toe_status_label(0.95) == "candidate_toe"
    assert toe_status_label(0.75) == "promising_unification"
    assert toe_status_label(0.5) == "partial_framework"
    assert toe_status_label(0.2) == "early_stage"


def test_weakest_link_identification():
    c = TheoryCandidate(
        name="w33-program",
        reproduces_gravity=0.6,
        reproduces_standard_model=0.7,
        dark_sector_explanatory_power=0.4,
        quantitative_predictions=0.3,
        consistency_and_uv_completion=0.9,
    )
    assert weakest_link(c) == ("quantitative_predictions", 0.3)
