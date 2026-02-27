import subprocess
from pathlib import Path
import json

def test_octonion_g2(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    # run the tool in quick mode to avoid heavy computation but still produce outputs
    res = subprocess.run([
        ".venv\\Scripts\\python.exe",
        str(repo / "tools" / "octonion_g2.py"),
        "--quick"
    ], cwd=repo)
    assert res.returncode == 0
    # check output files
    stats_file = repo / 'octonion_rep_stats.json'
    deriv_file = repo / 'octonion_derivations.json'
    assert stats_file.exists()
    assert deriv_file.exists()
    stats = json.loads(stats_file.read_text())
    assert stats.get('orbit_size') == 480
    assert stats.get('null_dim') == 14
    assert stats.get('fix_dim') == 8
    deriv = json.loads(deriv_file.read_text())
    assert deriv.get('null_dim') == 14
    assert deriv.get('fix_dim') == 8
