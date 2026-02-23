import subprocess
import sys

def test_embedding_counts():
    result = subprocess.run([sys.executable, 'tools/embedding_analysis.py'], capture_output=True, text=True)
    out = result.stdout + result.stderr
    # check the key observation: 72 edges map into the r5=r6=r7 subset
    assert 'candidate r5=r6=r7: 72 roots' in out
    assert 'edges mapped into set: 72' in out
