from pathlib import Path

import pytest

from tools.vet_candidates_and_apply import (
    apply_candidates_from_csv,
    generate_vetting_csv,
)

MISSING_JSON = Path(
    "analysis/minimal_commutator_cycles/w33_uv_parser_det1_missing_edges_candidates.json"
)
VET_CSV = Path(
    "analysis/minimal_commutator_cycles/w33_uv_parser_det1_missing_edges_candidates_vetting.csv"
)
COMBINED_MAP = Path("artifacts/edge_to_e8_root_combined.json")


def test_generate_vetting_csv_and_dry_apply():
    # skip if candidates file not present
    if not MISSING_JSON.exists():
        pytest.skip("Candidates JSON not present; skipping")
    # generate
    gen = generate_vetting_csv(MISSING_JSON, VET_CSV)
    assert VET_CSV.exists()
    assert gen["rows"] > 0
    # skip if combined map artifact not present
    if not COMBINED_MAP.exists():
        pytest.skip("Missing artifacts/edge_to_e8_root_combined.json (integration-only)")
    # try dry-run apply
    res = apply_candidates_from_csv(
        VET_CSV, combined_map_path=COMBINED_MAP, dry_run=True
    )
    # If no candidates are suggested for apply, the function returns a reason message; otherwise a dry_run summary
    assert ("dry_run" in res and res["dry_run"] is True) or (
        res.get("reason") == "no candidates marked for apply"
    )