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
    assert data["chi2"] < 0.01
    assert data["max_error"] < 0.05
