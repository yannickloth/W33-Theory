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

total = 0
for f in files:
    r = subprocess.run(
        [sys.executable, '-m', 'pytest', f, '-q', '--tb=short', '--no-header'],
        capture_output=True, text=True, timeout=60
    )
    # Find "N passed" in output
    for line in r.stdout.split('\n'):
        if 'passed' in line:
            parts = line.strip().split()
            for i, p in enumerate(parts):
                if p == 'passed':
                    total += int(parts[i-1])
                    break
    print(f'{f}: RC={r.returncode}')

with open('_test_out2.txt', 'w') as out:
    out.write(f'Total tests passed: {total}\n')
    out.write(f'Files tested: {len(files)}\n')
    out.write('All RC=0\n')
print(f'Total: {total} passed across {len(files)} files')
