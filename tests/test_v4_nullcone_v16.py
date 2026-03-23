import json
import subprocess
from pathlib import Path


def test_v4_nullcone_v16_results():
    script = Path("toe_session_20260316_v16") / "toe_session_20260316_v16" / "w33_v4_nullcone_v16.py"
    assert script.exists(), f"Expected v16 script at {script}"

    subprocess.run(["py", "-3", str(script)], check=True)

    results_path = Path("toe_session_20260316_v16") / "toe_session_20260316_v16" / "w33_v4_nullcone_results_v16.json"
    data = json.loads(results_path.read_text(encoding="utf-8"))

    checks = data["checks"]
    assert checks["chi_A_equals_minus_chi_B_on_active"]
    assert checks["N_nilpotent"]
    assert checks["H_plus_square"]
    assert checks["H_minus_square"]

    general = data["general_packet"]
    assert "exceptional_line" in general
    assert general["exceptional_line"].startswith("a=0")
