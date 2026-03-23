import json
import subprocess
from pathlib import Path


def test_real_dirac_shell_v19_clifford_and_dirac():
    script = Path("toe_session_20260316_v19") / "toe_session_20260316_v19" / "w33_real_dirac_shell_v19.py"
    assert script.exists(), f"Expected v19 script at {script}"

    subprocess.run(["py", "-3", str(script)], check=True)

    results_path = Path("toe_session_20260316_v19") / "toe_session_20260316_v19" / "w33_real_dirac_shell_results_v19.json"
    assert results_path.exists(), "Expected v19 result JSON to exist"

    results = json.loads(results_path.read_text(encoding="utf-8"))

    # Basic checks: Clifford signature and anticommutator verification.
    assert results["clifford_signature_diagonal"] == [1, 1, -1, 1]
    assert results["anticommutator_relations_verified"] is True
    assert "slash_square_formula" in results
    assert results["protected_Q_factorization"].startswith("Q = E")
