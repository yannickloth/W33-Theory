import json
import subprocess
from pathlib import Path


def test_anchor_socle_v10_algebra_structure():
    script = Path("toe_session_20260316_v10") / "toe_session_20260316_v10" / "w33_anchor_socle_v10.py"
    assert script.exists(), f"Expected v10 script at {script}"

    proc = subprocess.run(["py", "-3", str(script)], capture_output=True, text=True, check=True)
    data = json.loads(proc.stdout)

    anchor = data["anchor_algebra"]
    assert "TU2" in anchor["socle_basis"]
    assert anchor["loewy_dimensions"]["A/m"] == 1
    assert anchor["loewy_dimensions"]["m/m^2"] == 2
    assert anchor["loewy_dimensions"]["m^2/m^3"] == 2
    assert anchor["loewy_dimensions"]["m^3"] == 1

    # Ensure the multiplication table matches the claimed ideal structure
    mult = data["multiplication_table"]
    assert mult["U*U2"] == "0"
    assert mult["T*T"] == "0"
    assert mult["U*T"] == "TU"
    assert mult["TU*U"] == "TU2"
