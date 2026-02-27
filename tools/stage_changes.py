import subprocess, pathlib, sys
repo=pathlib.Path('c:/Repos/Theory of Everything')
files=[
    'tests/test_pg33_geometry.py',
    'tools/match_bose_mesner.py',
    'tools/meataxe_decompose.py',
    'TOE_duad_algebra_v06_20260227_bundle',
    'tools/duad_we6_conjugacy.py',
    'tools/bundle_test.py',
    'tools/git_status.py',
    'tools/test_duad_run.py'
]
for f in files:
    r=subprocess.run(['git','add',f], cwd=str(repo), capture_output=True, text=True)
    sys.stdout.write(f"{f} rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}\n")
