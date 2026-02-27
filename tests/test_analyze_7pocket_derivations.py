import subprocess
from pathlib import Path
import shutil
import zipfile

def test_analyze_7pocket_derivations(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    # copy bundle folder to tmp
    src = repo / 'TOE_7pocket_derivations_v01_20260227_bundle' / 'TOE_7pocket_derivations_v01_20260227'
    dst = tmp_path / 'out'
    shutil.copytree(src, dst)
    res = subprocess.run([".venv\\Scripts\\python.exe", str(repo / "tools" / "analyze_7pocket_derivations.py"), str(dst)], cwd=repo, capture_output=True, text=True)
    assert res.returncode == 0
    out = res.stdout
    # expect some keywords
    assert 'rank of derivations' in out
    assert 'center dimension' in out
