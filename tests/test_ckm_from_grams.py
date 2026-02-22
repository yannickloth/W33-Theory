import subprocess
import sys
import json
import os
import numpy as np


def test_ckm_script_runs_and_outputs():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    res = subprocess.run([sys.executable, "scripts/ckm_from_grams.py"], env=env)
    assert res.returncode == 0, "ckm_from_grams.py failed to run"
    assert os.path.exists("data/ckm_from_grams.json"), "output JSON not created"


def test_ckm_matrix_reasonable():
    data = json.load(open("data/ckm_from_grams.json"))
    mat = np.array(data["overlap_matrix"], dtype=float)
    assert mat.shape == (3, 3)
    # we expect some hierarchy: at least one row should have a dominant entry >0.5
    row_max = np.max(mat, axis=1)
    assert np.any(row_max > 0.5), "no row has a dominant element"
    # ensure the matrix is not completely flat (all entries roughly equal)
    assert mat.std() > 1e-2, "CKM overlap matrix is too uniform"
