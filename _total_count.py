import os, re

test_dir = 'tests'
files = [f for f in os.listdir(test_dir) if f.startswith('test_') and f.endswith('.py')]
total = 0
for f in files:
    with open(os.path.join(test_dir, f), encoding='utf-8') as fh:
        total += len(re.findall(r'def test_', fh.read()))

print(f'Test files: {len(files)}')
print(f'Total test methods: {total}')

# Also count all .py files in tests/
all_py = [f for f in os.listdir(test_dir) if f.endswith('.py')]
print(f'All .py files in tests/: {len(all_py)}')
