import subprocess
import sys
import os
import glob


def test_ckm_script_runs():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    res = subprocess.run([sys.executable, "scripts/w33_ckm_matrix.py"], env=env)
    assert res.returncode == 0
    # check that at least one output file was created
    files = glob.glob("checks/PART_CXII_ckm_matrix_*.json")
    assert files, "CKM output file not found"


def test_ckm_output_structure():
    files = glob.glob("checks/PART_CXII_ckm_matrix_*.js")
    if not files:
        return
    # read most recent file
    path = max(files, key=os.path.getmtime)
    content = open(path, encoding="utf-8").read()
    assert "CKM MATRIX FROM W(3,3)" in content
    # basic sanity: includes 'theta_12' and 'theta_13'
    assert "theta_12" in content and "theta_13" in content
