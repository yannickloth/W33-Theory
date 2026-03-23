import json
import math
import subprocess
from pathlib import Path


def test_soft_syndrome_metric_v36_exact_metrics():
    script = Path("toe_session_20260316_v36") / "toe_session_20260316_v36" / "w33_soft_syndrome_metric_v36.py"
    assert script.exists(), f"Expected v36 solver at {script}"

    subprocess.run(["py", "-3", str(script)], check=True)

    results_path = Path("toe_session_20260316_v36") / "toe_session_20260316_v36" / "w33_soft_syndrome_metric_results_v36.json"
    data = json.loads(results_path.read_text(encoding="utf-8"))

    x = data["x"]
    tau = data["tau"]

    # Verify spectral eigenvalues follow x^weight
    for s in data["syndrome_data"]:
        w = s["weighted_degree"]
        assert abs(s["spectral_eigenvalue"] - (x ** w)) < 1e-12
        assert abs(s["spectral_energy"] - (tau * w)) < 1e-12

        # Verify soft-decoding odds/LLR relationship
        cost = s["neg_log_relative_odds"]
        assert abs(s["relative_odds_to_vacuum"] - math.exp(-cost)) < 1e-12

    # Check that the axis LLRs match the expected formula L = log((1+x^w)/(1-x^w))
    axis_data = data["axis_data"]
    for axis in axis_data:
        w = axis["weight"]
        xw = x ** w
        expected_llr = math.log((1 + xw) / (1 - xw))
        assert abs(axis["llr_weight"] - expected_llr) < 1e-12
