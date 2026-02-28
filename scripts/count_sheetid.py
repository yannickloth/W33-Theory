import csv
from collections import Counter
c=Counter()
with open('edges_270_transport.csv') as f:
    for r in csv.DictReader(f):
        c[int(r['sheet_id'])]+=1
print(c)
