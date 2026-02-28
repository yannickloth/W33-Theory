import csv, zipfile, io

with zipfile.ZipFile('TOE_tomotope_triality_weld_v01_20260228_bundle.zip') as zf:
    text = zf.read('TOE_tomotope_triality_weld_v01_20260228/K_orbit_pockets_54.csv').decode()
reader = csv.DictReader(io.StringIO(text))
sv = set()
for r in reader:
    sv.add(int(r['silent_vertex']))
print('silent values', sorted(sv), 'count', len(sv))
