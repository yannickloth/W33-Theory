import csv
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
pairs = set()
with open(BASE / 'pillar77_data' / 'K54_edges_with_coords_voltage.csv') as f:
    r = csv.DictReader(f)
    for row in r:
        pairs.add((int(row['qid_u']), int(row['qid_v']), row['gen']))
print('unique qid_u,qid_v,gen combos =', len(pairs))
print('some examples', list(pairs)[:10])