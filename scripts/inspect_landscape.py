import json
from pathlib import Path

p = Path('data/combined_landscape.json')
if not p.exists():
    print('missing file')
    raise SystemExit(1)
J = json.loads(p.read_text(encoding='utf-8'))

points = []
if 'best_random' in J:
    points.append((J['best_random']['ck_err'], J['best_random']['mass_err']))
for line in J.get('line_results', []):
    for pt in line:
        points.append((pt['ck_err'], pt['mass_err']))

print('total points', len(points))
if not points:
    raise SystemExit('no points')

# sort by ck
points.sort()
pareto = []
min_mass = float('inf')
for ck, m in points:
    if m < min_mass:
        pareto.append((ck, m))
        min_mass = m

print('Pareto frontier:')
for ck, m in pareto:
    print(f'  ck={ck:.6f}, mass={m:.6f}')

best_ck = min(ck for ck, m in points)
best_mass = min(m for ck, m in points)
print('best_ck', best_ck)
print('best_mass', best_mass)

ratios = [ck / m if m > 0 else float('inf') for ck, m in points]
print('min ck/mass', min(ratios))
print('max ck/mass', max(ratios))

# quick weight scan using extant points (approximate since weight not stored)
print('\nweight_mass scan (approximate from existing random points):')
for w in [0.01,0.1,1,10,100]:
    # we don't have weight info per point; just report frontier ck/mass ratio
    print(f'  weight {w}: frontier ck/mass ratio ~ {min(ratios):.4f}')
