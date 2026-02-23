import subprocess
import sys
import os
import json

def test_neutrino_runs():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    res = subprocess.run([sys.executable, "scripts/neutrino_mass_predictions.py"], env=env)
    assert res.returncode == 0
    assert os.path.exists("data/neutrino_mass_predictions.json")


def test_neutrino_structure():
    data = json.load(open("data/neutrino_mass_predictions.json"))
    assert "index" in data and isinstance(data["index"], int)
    assert "ratios" in data and isinstance(data["ratios"], list)
    assert "predicted" in data and isinstance(data["predicted"], list)
    preds = data["predicted"]
    # ensure first three predicted masses are in ascending order
    assert len(preds) >= 3
    assert preds[0] <= preds[1] <= preds[2]
