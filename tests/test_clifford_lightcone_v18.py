import json
import subprocess
from pathlib import Path


def test_clifford_lightcone_v18_basic_relations():
    script = Path("toe_session_20260316_v18") / "toe_session_20260316_v18" / "w33_clifford_lightcone_v18.py"
    assert script.exists(), f"Expected v18 script at {script}"

    subprocess.run(["py", "-3", str(script)], check=True)

    results_path = Path("toe_session_20260316_v18") / "toe_session_20260316_v18" / "w33_clifford_lightcone_results_v18.json"
    data = json.loads(results_path.read_text(encoding="utf-8"))

    ferm = data["fermionic_relations"]
    assert ferm["E2"] == "Matrix([[0, 0], [0, 0]])"
    assert ferm["F2"] == "Matrix([[0, 0], [0, 0]])"
    assert ferm["EF_plus_FE"] == "Matrix([[1, 0], [0, 1]])"

    # verify the Dirac supercharge squares correctly and has correct kernel dimension
    supercharge = data["supercharge_packet"]
    assert supercharge["Q2_zero"]
    assert supercharge["Qdag2_zero"]
    assert supercharge["D_rank"] == 2
    assert supercharge["D_nullity"] == 2

    # verify the Clifford signature matches (2,1) embedding
    cliff = data["clifford_2_1_anticommutators"]
    assert cliff["gamma1_H_gamma1_H"] == "Matrix([[2, 0], [0, 2]])"
    assert cliff["gamma0_Qy_gamma0_Qy"] == "Matrix([[-2, 0], [0, -2]])"
