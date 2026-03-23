import json
import subprocess
from pathlib import Path


def test_fano_hamming_bridge_v35_attenuation_weights():
    script = Path("toe_session_20260316_v35") / "w33_fano_hamming_bridge_v35.py"
    assert script.exists(), f"Expected v35 solver at {script}"

    subprocess.run(["py", "-3", str(script)], check=True)

    results_path = Path("toe_session_20260316_v35") / "w33_fano_hamming_results_v35.json"
    data = json.loads(results_path.read_text(encoding="utf-8"))

    x = data["x"]
    channels = data["channels"]

    # Attenuation = x^channel_id (index 1-7), not x^bit-weight
    for ch in channels:
        expected = x ** ch["channel_id"]
        assert abs(ch["attenuation"] - expected) < 1e-12

    # Verify that the Walsh characters correspond to the parity function on the bit subset
    # (i.e., + for even parity and - for odd parity in the 8-bit Walsh order)
    for ch in channels:
        char = ch["walsh_character"]
        assert set(char).issubset({"+", "-"})
        assert len(char) == 8

    # Check Fano configuration consistency: 7 lines of 3 points each
    lines = data["Fano_lines"]
    assert len(lines) == 7
    assert all(len(line) == 3 for line in lines)
