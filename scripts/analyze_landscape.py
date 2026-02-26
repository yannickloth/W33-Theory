import json
from pathlib import Path

p = Path('data/combined_landscape.json')
print('exists', p.exists())
if not p.exists():
    raise SystemExit('missing JSON')
J = json.loads(p.read_text(encoding='utf-8'))
print('rank', J.get('rank'))
print('best_random', J.get('best_random'))
# aggregate error stats
min_ck = min(pt['ck_err'] for pt in J.get('line_results', []) for _ in (0,))
min_mass = min(pt['mass_err'] for pt in J.get('line_results', []) for _ in (0,))
print('min_ck (lines)', min_ck)
print('min_mass (lines)', min_mass)
# also evaluate random points
rnd = J.get('best_random', {})
print('best_random combined', rnd.get('combined'))
print('best_random ck_err', rnd.get('ck_err'))
print('best_random mass_err', rnd.get('mass_err'))
