import json
import subprocess
from pathlib import Path


def test_one_defect_ckm_lift_v27_stitch_precision():
    script = Path("toe_session_20260316_v27") / "toe_session_20260316_v27" / "w33_one_defect_ckm_lift_v27.py"
    assert script.exists(), f"Expected v27 script at {script}"

    subprocess.run(["py", "-3", str(script)], check=True)

    results_path = Path("toe_session_20260316_v27") / "toe_session_20260316_v27" / "w33_one_defect_ckm_results_v27.json"
    data = json.loads(results_path.read_text(encoding="utf-8"))

    exactish = data["exactish"]
    stitch_factor = exactish["s12_stitch_over_lambda_dressed"]
    stitch_deviation = exactish["stitch_factor_minus_1"]

    # Stitch deviation should be very small (~7e-6)
    assert abs(stitch_deviation) < 1e-5

    # Ensure the stitched CKM reproduces the exact |V_us| target
    comparisons = data["comparisons"]
    assert abs(comparisons["stitched_Vus_minus_target"]) < 1e-12

    # The dressed one-defect variant should be close to the stitched one (Frobenius norm small)
    assert comparisons["dressed_to_stitched_frobenius_absV"] < 1e-4
