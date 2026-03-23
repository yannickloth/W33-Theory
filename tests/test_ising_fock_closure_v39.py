import json
import subprocess
from pathlib import Path


def test_ising_fock_closure_v39_free_fermion_spectrum():
    script = Path("toe_session_20260316_v39") / "toe_session_20260316_v39" / "w33_ising_fock_closure_v39.py"
    assert script.exists(), f"Expected v39 solver at {script}"

    subprocess.run(["py", "-3", str(script)], check=True)

    results_path = Path("toe_session_20260316_v39") / "toe_session_20260316_v39" / "w33_ising_fock_results_v39.json"
    data = json.loads(results_path.read_text(encoding="utf-8"))

    # Spectrum is exactly 0..7 and partition collapses to (1+x)(1+x^2)(1+x^4)
    energies = sorted(s["energy"] for s in data["states"])
    assert energies == list(range(8))

    assert abs(data["Z_fock"] - data["Z_from_ising"]) < 1e-12

    # Interaction fit should be free: only linear terms nonzero
    fit = data["interaction_fit"]
    assert abs(fit["const"]) < 1e-12
    assert abs(fit["h1"] - 1) < 1e-12
    assert abs(fit["h2"] - 2) < 1e-12
    assert abs(fit["h3"] - 4) < 1e-12
    assert abs(fit["J12"]) < 1e-12
    assert abs(fit["J13"]) < 1e-12
    assert abs(fit["J23"]) < 1e-12
    assert abs(fit["J123"]) < 1e-12
