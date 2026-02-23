import subprocess
import sys
import os
import json
import numpy as np


def test_sector_assignment_runs():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    res = subprocess.run([sys.executable, "scripts/yukawa_sector_assignment.py"], env=env)
    assert res.returncode == 0
    assert os.path.exists("data/yukawa_sector_assignment.json")


def test_best_assignment_structure():
    data = json.load(open("data/yukawa_sector_assignment.json"))
    best = data.get("best")
    assert best is not None
    assert "perm" in best and "sectors" in best
    # ensure the permutation is length 3 with unique entries
    perm = tuple(best["perm"])
    assert len(perm) == 3 and set(perm) == {0,1,2}
    # ensure sectors list matches
    sectors = best["sectors"]
    assert len(sectors) == 3
    # current data gives down‑lepton‑up ordering
    assert tuple(best["perm"]) == (1, 2, 0)
    assert sectors == ["down", "lepton", "up"]
    # mass_error should be present and non-negative
    assert "mass_error" in best and best["mass_error"] >= 0
    # predicted masses should be strictly increasing order in each sector
    pm = best.get("predicted_masses", {})
    for sec in ["up", "down", "lepton"]:
        masses = np.array(pm.get(sec, []))
        # we expect at least three generations
        assert masses.size >= 3
        assert masses[0] < masses[1] < masses[2] > 0
    # score should equal the sum of the individual errors, including heavy error
    computed = (
        best["ckm_error"] + best["koide_error"] + best["mass_error"]
        + best.get("heavy_error", 0)
    )
    assert abs(computed - best["score"]) < 1e-6
    # mass and heavy errors should not be astronomically large (sanity checks)
    assert best["mass_error"] < 10
    assert best.get("heavy_error", 0) < 10
    # fit scales and predicted heavy masses exist and are positive
    assert "fit_scales" in best and all(best["fit_scales"][s] > 0 for s in ["up","down","lepton"])
    assert "predicted_heavy_masses" in best and all(best["predicted_heavy_masses"][s] > 0 for s in ["up","down","lepton"])

