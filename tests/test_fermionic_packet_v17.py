import json
import subprocess
from pathlib import Path


def test_fermionic_packet_v17_fermionic_algebra():
    script = Path("toe_session_20260316_v17") / "toe_session_20260316_v17" / "w33_fermionic_packet_v17.py"
    assert script.exists(), f"Expected v17 script at {script}"

    subprocess.run(["py", "-3", str(script)], check=True)

    results_path = Path("toe_session_20260316_v17") / "toe_session_20260316_v17" / "w33_fermionic_packet_results_v17.json"
    data = json.loads(results_path.read_text(encoding="utf-8"))

    checks = data["checks"]
    assert checks["E_nilpotent"]
    assert checks["F_nilpotent"]
    assert checks["CAR"]
    assert checks["sl2_comm_1"]
    assert checks["sl2_comm_2"]
    assert checks["sl2_comm_3"]
    assert checks["chirality_square"]
    assert checks["Qx_square"]
    assert checks["Qy_square"]
    assert checks["anticomm_Qx_Qy"]

    bridge = data["ce2_bridge_normal_form"]
    assert "E \u2297 J2 \u2297 I27" in bridge["rank28_bridge"]
    assert "vacuum selector" in bridge["interpretation"]
