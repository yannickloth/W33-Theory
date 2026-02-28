import csv
coords={}
with open('pillar77_data/K27_heisenberg_coords.csv') as f:
    for r in csv.DictReader(f):
        coords[int(r['qid'])] = (int(r['x']), int(r['y']), int(r['z']))
print('qid 3', coords[3])
print('qid 12', coords[12])
print('qid 15', coords[15])
