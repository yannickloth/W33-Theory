import json
import math
import subprocess
from pathlib import Path

def test_ancilla_self_energy_completion_v53():
    """
    Regression test for v53: the finite nonfree residue is exactly the self-energy of one hidden ancilla mode.
    """
    # Run the v53 solver script
    script = Path("bundles/v53/w33_ancilla_completion_v53.py")
    assert script.exists(), f"Expected v53 solver at {script}"
    subprocess.run(["py", "-3", str(script)], check=True)

    # Load the results JSON
    results_path = Path("bundles/v53/w33_ancilla_completion_results_v53.json")
    data = json.loads(results_path.read_text(encoding="utf-8"))

    # Extract key quantities
    kappa = data["kappa"]
    g = data["g"]
    epsilon_a = data["epsilon_a"]
    h_eff_diag = data["H_eff_diag"]
    h_finite_diag = data["H_finite_diag"]

    # Theorem: kappa = g^2 / epsilon_a
    assert math.isclose(kappa, g**2 / epsilon_a, rel_tol=1e-12), f"kappa != g^2/epsilon_a: {kappa} vs {g**2/epsilon_a}"

    # The effective Hamiltonian matches the finite normal form at machine precision
    for h1, h2 in zip(h_eff_diag, h_finite_diag):
        assert math.isclose(h1, h2, rel_tol=1e-12), f"Mismatch in Hamiltonian diagonal: {h1} vs {h2}"

    # The nonfree residue is exactly the self-energy of the hidden ancilla mode
    assert data["ancilla_completion_verified"], "Ancilla self-energy completion not verified in results."
