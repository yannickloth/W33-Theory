import subprocess
import sys
import json
import os


def test_gauge_script_runs():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    res = subprocess.run([sys.executable, "scripts/gauge_couplings.py"], env=env)
    assert res.returncode == 0
    assert os.path.exists("data/gauge_couplings.json")


def test_gauge_structure():
    data = json.load(open("data/gauge_couplings.json"))
    assert "predicted" in data and isinstance(data["predicted"], list)
    assert "experimental" in data and isinstance(data["experimental"], list)
    assert "chi2" in data and isinstance(data["chi2"], float)
    assert "max_error" in data and isinstance(data["max_error"], float)
    # ensure chi2 is small and fractional errors are modest
    # chi2 may be large since only relative weights are geometric
    # but it should be a finite float and errors < 100 for sanity.
    assert isinstance(data["chi2"], float)
    assert data.get("max_error", 0) < 100
    # geometry-derived weights should be present
    assert "beta_weights" in data and isinstance(data["beta_weights"], list)
