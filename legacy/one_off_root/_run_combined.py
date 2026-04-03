import subprocess, sys

files = [
    'tests/test_qg_phenomenology.py',
    'tests/test_celestial_holography.py',
    'tests/test_quantum_chaos.py',
    'tests/test_generalized_symmetries.py',
    'tests/test_quantum_cosmology.py',
    'tests/test_experimental_signatures.py',
    'tests/test_absolute_final_synthesis.py',
]

try:
    r = subprocess.run(
        [sys.executable, '-m', 'pytest'] + files + ['-q', '--tb=short', '--no-header'],
        capture_output=True, text=True, timeout=120
    )
    with open('_test_out2.txt', 'w') as f:
        f.write(r.stdout[-1500:])
        f.write('\nRC:' + str(r.returncode) + '\n')
    print('DONE RC=' + str(r.returncode))
except Exception as e:
    with open('_test_out2.txt', 'w') as f:
        f.write('ERROR: ' + str(e) + '\n')
    print('ERROR: ' + str(e))
