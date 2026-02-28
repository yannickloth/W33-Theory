import subprocess
import os
import json
import sys

def test_recompute_icosahedral_spine_outputs(tmp_path, capsys):
    # run the recompute script and capture output
    script = os.path.join("scripts", "recompute_binary_icosahedral_2A5.py")
    result = subprocess.run([sys.executable, script], cwd=".", capture_output=True, text=True)
    # script should finish without crashing (exit code 0)
    assert result.returncode == 0, result.stderr
    out = result.stdout + result.stderr
    # we expect a warning about missing lifts or a success message
    assert "Warning:" in out or "done exports" in out
    # check that line orbit CSV and JSON exist
    assert os.path.isfile("w33_lines_40_orbits_under_A5.csv")
    assert os.path.isfile("A5_orbit_decompositions.json")
    with open("A5_orbit_decompositions.json") as f:
        data = json.load(f)
    assert "line_orbit_sizes" in data
    assert isinstance(data["line_orbit_sizes"], list)
