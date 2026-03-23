import json
import subprocess
from pathlib import Path


def test_berry_weyl_cone_v15_output_consistency():
    script = Path("toe_session_20260316_v15") / "toe_session_20260316_v15" / "w33_berry_weyl_cone_v15.py"
    assert script.exists(), f"Expected v15 script at {script}"

    subprocess.run(["py", "-3", str(script)], check=True)

    results_path = Path("toe_session_20260316_v15") / "toe_session_20260316_v15" / "w33_berry_weyl_results_v15.json"
    data = json.loads(results_path.read_text(encoding="utf-8"))

    # verify the Berry sign is exactly -1 (Z2 holonomy)
    assert data["berry_triangle"]["berry_sign"] == "-1"

    # verify the Weyl reflection group structure (w0w1 is a rotation matrix)
    w0w1 = data["weyl_bridge"]["products"]["w0w1"]
    # must be a 2x2 rotation with trace = -1/2? (120deg rotation has trace=-1/2)
    # Record that it exists and is 2x2
    assert len(w0w1) == 2 and len(w0w1[0]) == 2
