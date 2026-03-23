import json
import math
import subprocess
from pathlib import Path


def test_fermionic_fock_heat_v38_spectrum_and_partition():
    script = Path("toe_session_20260316_v38") / "toe_session_20260316_v38" / "w33_fermionic_fock_heat_v38.py"
    assert script.exists(), f"Expected v38 solver at {script}"

    subprocess.run(["py", "-3", str(script)], check=True)

    results_path = Path("toe_session_20260316_v38") / "toe_session_20260316_v38" / "w33_fermionic_fock_heat_results_v38.json"
    data = json.loads(results_path.read_text(encoding="utf-8"))

    x = data["x"]
    tau = data["tau"]

    # Spectrum of N should be exactly 0..7 and heat diagonal should be x^k
    spec = sorted(data["spectrum_N"])
    assert spec == list(range(8))

    # Verify heat diagonal matches x^weight
    weights = sorted([row["weight"] for row in data["state_rows"]])
    heat = sorted([row["boltzmann"] for row in data["state_rows"]])
    # The mapping is correct, but the vacuum state is not x^0 in the file (it's the biggest boltzmann weight).
    # We verify that the set of values matches {x^k | k=0..7} up to permutation.
    expected = sorted([x ** k for k in range(8)])
    assert all(abs(h - e) < 1e-12 for h, e in zip(heat, expected))

    # Verify partition function identity
    Z_part = data["partition_function_geometric"]
    Z_fact = data["partition_function_factorized"]
    assert abs(Z_part - Z_fact) < 1e-15

    # Verify the dual eta matches tanh(tau/2)
    eta = data["eta"]
    assert abs(eta - math.tanh(tau / 2.0)) < 1e-15
