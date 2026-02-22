import subprocess
import sys
import os
import json

def test_rg_script_runs():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    res = subprocess.run([sys.executable, "RG_PRECISION_MASSES.py"], env=env)
    assert res.returncode == 0
    assert os.path.exists("RG_MASSES.json")


def test_rg_output_structure():
    data = json.load(open("RG_MASSES.json"))
    assert "masses_predicted" in data
    preds = data["masses_predicted"]
    # ensure top mass prediction is nonzero numeric
    assert "m_t" in preds and isinstance(preds["m_t"], float)
    assert preds["m_t"] != 0.0
    # ratios dictionary should exist
    assert "W33_ratios" in data and isinstance(data["W33_ratios"], dict)
