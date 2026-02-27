import subprocess
from pathlib import Path

def test_moonshine_cft_terms():
    repo = Path(__file__).resolve().parents[1]
    res = subprocess.run([".venv\\Scripts\\python.exe", str(repo / "tools" / "moonshine_cft.py"), "--terms", "3"], cwd=repo, capture_output=True, text=True)
    assert res.returncode == 0
    out = res.stdout.strip().splitlines()
    # expect header line plus at least 3 coefficient lines
    assert len(out) >= 4
    # check that the first coefficient is q^{-1} = 1
    assert out[1].startswith("-1 1")
