import json
import subprocess
from pathlib import Path


def test_exterior_defect_cube_v32_subset_sum_weights():
    script = Path("toe_session_20260316_v32") / "w33_exterior_defect_cube_v32.py"
    assert script.exists(), f"Expected v32 solver at {script}"

    subprocess.run(["py", "-3", str(script)], check=True)

    results_path = Path("toe_session_20260316_v32") / "w33_exterior_defect_cube_results_v32.json"
    data = json.loads(results_path.read_text(encoding="utf-8"))

    x = data["x"]
    states = data["states"]

    # Check subset-sum weight structure (weights are subset sums of [1,2,4])
    valid_weights = {0, 1, 2, 3, 4, 5, 6, 7}
    assert set(s["weight"] for s in states) == valid_weights

    # Check defect_factor is x^weight within rounding tolerance
    for s in states:
        weight = s["weight"]
        expected = x**weight
        assert abs(s["defect_factor"] - expected) < 1e-12

    # Check channel_map weights align with the expected state weights
    channel_map = data["channel_map"]
    for entry in channel_map:
        weight = entry["weight"]
        assert weight in valid_weights
        assert abs(entry["factor"] - (x ** weight)) < 1e-12
