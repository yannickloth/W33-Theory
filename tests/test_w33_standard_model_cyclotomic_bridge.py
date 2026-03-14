from __future__ import annotations

import json
from pathlib import Path

from w33_standard_model_cyclotomic_bridge import (
    build_standard_model_cyclotomic_summary,
    write_summary,
)


def test_standard_model_cyclotomic_bridge_records_promoted_observables() -> None:
    summary = build_standard_model_cyclotomic_summary()
    assert summary["status"] == "ok"
    data = summary["cyclotomic_data"]
    assert data["q"] == 3
    assert data["phi3"] == 13
    assert data["phi6"] == 7
    assert data["four_phi3_plus_q"] == 55

    obs = summary["promoted_observables"]
    assert obs["sin2_theta_w_ew"]["exact"] == "3/13"
    assert obs["tan_theta_c"]["exact"] == "3/13"
    assert obs["sin2_theta_12"]["exact"] == "4/13"
    assert obs["sin2_theta_23"]["exact"] == "7/13"
    assert obs["sin2_theta_13"]["exact"] == "2/91"
    assert obs["higgs_ratio_square"]["exact"] == "14/55"
    assert obs["omega_lambda"]["exact"] == "9/13"


def test_standard_model_cyclotomic_bridge_has_exact_closure_relations() -> None:
    summary = build_standard_model_cyclotomic_summary()
    closure = summary["closure_relations"]
    assert closure["tan_cabibbo_equals_ew_weinberg"] is True
    assert closure["pmns_23_equals_weinberg_plus_pmns_12"] is True
    assert closure["omega_lambda_equals_q_times_weinberg"] is True
    assert closure["reactor_has_phi3_phi6_denominator"] is True
    assert closure["higgs_uses_four_phi3_plus_q_denominator"] is True


def test_standard_model_cyclotomic_bridge_writes_summary(tmp_path: Path) -> None:
    out = tmp_path / "summary.json"
    write_summary(out)
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["promoted_observables"]["omega_lambda"]["exact"] == "9/13"
