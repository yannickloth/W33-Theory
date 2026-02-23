import subprocess
import sys
import os
import json

def test_mixing_runs():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    res = subprocess.run([sys.executable, "scripts/mixing_from_grams.py"], env=env)
    assert res.returncode == 0
    assert os.path.exists("data/mixing_from_grams.json")


def test_mixing_structure():
    data = json.load(open("data/mixing_from_grams.json"))
    assert "ratios" in data and isinstance(data["ratios"], list)
    assert "results" in data and isinstance(data["results"], list)
    assert "best_ckm" in data and isinstance(data["best_ckm"], dict)
    assert "best_pmns" in data and isinstance(data["best_pmns"], dict)
    # optional: cross-check with neutrino mass prediction
    if os.path.exists("data/neutrino_mass_predictions.json"):
        nu = json.load(open("data/neutrino_mass_predictions.json"))
        assert nu.get("index") == data["best_pmns"]["pair"][1]
    # each result should have pair and overlap matrix
    for entry in data["results"]:
        assert "pair" in entry and len(entry["pair"]) == 2
        ov = entry.get("overlap")
        assert isinstance(ov, list) and len(ov) == 3
        assert all(len(row) == 3 for row in ov)
        assert "ckm_error" in entry and isinstance(entry["ckm_error"], (float, int))
        assert "pmns_error" in entry and isinstance(entry["pmns_error"], (float, int))
