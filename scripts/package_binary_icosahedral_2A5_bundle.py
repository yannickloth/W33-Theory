import zipfile, os

bundle_name = 'TOE_binary_icosahedral_2A5_v01_20260227_bundle.zip'
inner_dir = 'TOE_binary_icosahedral_2A5_v01_20260227'

# expected outputs (some may not exist if lift failed)
files = [
    'w33_lines_40_orbits_under_A5.csv',
    'A5_orbit_decompositions.json',
]

# optional files if present
optional = [
    'w33_points_40_orbits_under_A5.csv',
    'w33_directed_edges_480_orbits_under_A5.csv',
    'faces_120_orbits_under_A5.csv',
    'binary_icosahedral_2A5_in_Sp43_summary.json',
]

for f in files:
    if not os.path.exists(f):
        raise FileNotFoundError(f"missing output file {f}; run recompute_binary_icosahedral_2A5.py first")

with zipfile.ZipFile(bundle_name, 'w', zipfile.ZIP_DEFLATED) as zf:
    for f in files:
        zf.write(f, f'{inner_dir}/{f}')
    for f in optional:
        if os.path.exists(f):
            zf.write(f, f'{inner_dir}/{f}')
    readme = """Binary icosahedral subgroup analysis bundle

Contains orbit decompositions for the canonical A5 stabilizer on W33 lines
and any vertex-based data when a lift exists (currently none).
"""
    zf.writestr(f'{inner_dir}/README.md', readme)

print('created bundle', bundle_name)
