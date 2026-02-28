#!/usr/bin/env python3
import zipfile, csv, io
from collections import Counter
bundle='TOE_tomotope_triality_weld_v01_20260228_bundle.zip'
with zipfile.ZipFile(bundle) as zf:
    text=zf.read('TOE_tomotope_triality_weld_v01_20260228/K_orbit_pockets_54.csv').decode()
reader=csv.DictReader(io.StringIO(text))
print('fields',reader.fieldnames)
vals=[r['silent_vertex'] for r in reader]
print(Counter(vals))
