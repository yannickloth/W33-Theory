import json
import subprocess
from pathlib import Path


def test_rank28_bridge_v11_normal_form_and_rank_spectrum():
    script = Path("toe_session_20260316_v11") / "w33_rank28_bridge_v11.py"
    assert script.exists(), f"Expected v11 script at {script}"

    proc = subprocess.run(["py", "-3", str(script)], capture_output=True, text=True, check=True)
    results_path = Path("toe_session_20260316_v11") / "w33_rank28_bridge_results_v11.json"
    assert results_path.exists(), "Expected results JSON to be written"
    data = json.loads(results_path.read_text(encoding='utf-8'))

    # ensure reduced rank spectrum matches the proved 6x6 algebra counts
    assert data["rank_spectrum_reduced"] == {"0": 1, "1": 2, "2": 24, "3": 54, "4": 162, "6": 486}

    # ensure the augmented rank-28 count is exactly four (λ, μ ∈ GF(3)^×)
    assert data["rank28_element_count_augmented"] == 4

    # rank 36 must be impossible in the protected augmented algebra
    assert data["rank36_present_in_augmented"] is False

    # the canonical rank-28 should equal 28
    assert data["canonical_rank28"] == 28

    # validate that the famous socle direction is identified
    assert data["socle_rank_162"] == 27
    assert "TU^2" in data["theorem_lines"][0]
