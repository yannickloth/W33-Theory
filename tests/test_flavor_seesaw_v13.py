import json
import subprocess
from pathlib import Path


def test_flavor_seesaw_v13_projector_and_commutant_structure():
    script = Path("toe_session_20260316_v13") / "toe_session_20260316_v13" / "w33_flavor_seesaw_v13.py"
    assert script.exists(), f"Expected v13 script at {script}"

    subprocess.run(["py", "-3", str(script)], check=True)

    results_path = Path("toe_session_20260316_v13") / "toe_session_20260316_v13" / "w33_flavor_seesaw_results_v13.json"
    data = json.loads(results_path.read_text(encoding="utf-8"))

    proj = data["projectors"]
    assert proj["verified_identities"]["N = 3 P0"]
    assert proj["verified_identities"]["Lg = 3 Pperp"]

    # commutant dimension should be 4 (singlet + doublet family)
    assert data["commutant_family"]["dimension"] == 4

    # ranks: reduced bridge should be rank 1, full 162 should be 27
    assert proj["ranks"]["rank(B_red)"] == 1
    assert proj["ranks"]["rank(B_162)"] == 27
