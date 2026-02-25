import json
from pathlib import Path
import pandas as pd

rp = json.loads(Path('data/rp_index.json').read_text(encoding='utf-8'))
per_prime = rp.get('per_prime', [])
rows=[]
for rec in per_prime:
    p = rec.get('p')
    best_perm = rec.get('best_pair_by_perm_index')
    best_mass = rec.get('best_pair_by_mass')
    rows.append({'p': p, 'best_perm': best_perm, 'best_mass': best_mass})
df=pd.DataFrame(rows)
print(df)
print('\nPrimes where best_perm != best_mass:')
print(df[df['best_perm'] != df['best_mass']])
