import subprocess
import sys

def test_edge_stabilizer_counts():
    result = subprocess.run([sys.executable, 'tools/edge_stabilizers.py'], capture_output=True, text=True)
    out = result.stdout + result.stderr
    # expect a line showing 216 for all 240 edges
    assert 'expected stabilizer size = 216' in out
    assert '216: 240' in out
