from __future__ import annotations

import json
from pathlib import Path

from w33_spectral_action_q3_selection_bridge import (
    build_spectral_action_q3_selection_summary,
    write_summary,
)


def test_spectral_action_q3_selection_bridge_internal_conditions_collapse() -> None:
    summary = build_spectral_action_q3_selection_summary()
    assert summary["status"] == "ok"
    equations = summary["selection_equations"]
    assert equations["internal_a2_ratio"]["polynomial"] == "3q^2 - 10q + 3"
    assert equations["internal_a4_ratio"]["polynomial"] == "3q^2 - 10q + 3"
    assert equations["higgs_ratio"]["polynomial"] == "3q^2 - 10q + 3"
    assert equations["internal_a2_ratio"]["factorization"] == "(q - 3)(3q - 1)"
    assert equations["internal_a2_ratio"]["unique_positive_integer_solution"] == 3
    assert equations["internal_a4_ratio"]["unique_positive_integer_solution"] == 3
    assert equations["higgs_ratio"]["unique_positive_integer_solution"] == 3


def test_spectral_action_q3_selection_bridge_gravity_condition_matches() -> None:
    summary = build_spectral_action_q3_selection_summary()
    equations = summary["selection_equations"]
    assert equations["gravity_normalization"]["polynomial"] == "q^2 + q - 12"
    assert equations["gravity_normalization"]["factorization"] == "(q - 3)(q + 4)"
    assert equations["gravity_normalization"]["unique_positive_integer_solution"] == 3

    sample_q3 = next(item for item in summary["sample_checks"] if item["q"] == 3)
    assert sample_q3["internal_condition_holds"] is True
    assert sample_q3["gravity_condition_holds"] is True


def test_spectral_action_q3_selection_bridge_writes_summary(tmp_path: Path) -> None:
    out = tmp_path / "summary.json"
    write_summary(out)
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["selection_equations"]["higgs_ratio"]["unique_positive_integer_solution"] == 3
