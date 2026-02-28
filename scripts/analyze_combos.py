import csv
from collections import Counter
from pathlib import Path

from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
coords = {}
# coords are stored in the sheet bundle extraction
with open(BASE / 'sheet_data' / 'coords_9x6.csv') as f:
    r = csv.DictReader(f)
    for row in r:
        coords[int(row['orbit_idx'])] = int(row['sheet_id'])

combos = Counter()
with open(BASE / 'pillar77_data' / 'K54_edges_with_coords_voltage.csv') as f:
    r = csv.DictReader(f)
    for row in r:
        u = int(row['u']); g = row['gen']
        combos[(g, coords[u])] += 1

print('generator-sheet_id combos:', len(combos))
print(combos)