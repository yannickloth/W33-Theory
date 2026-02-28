import csv
from collections import Counter

combos = Counter()
with open('sheet_data/coords_9x6.csv') as f:
    r = csv.DictReader(f)
    for row in r:
        combos[(int(row['silent_index']), int(row['sheet_id']))] += 1
print('combo counts', combos)
print('unique combos', len(combos))
