from pathlib import Path
import zipfile
ROOT=Path('c:/Repos/Theory of Everything')

def find_bundle(pattern: str) -> Path:
    p = ROOT / f"{pattern}.zip"
    if p.exists():
        return p
    p2 = ROOT / pattern
    if p2.exists():
        return p2
    cands = list(ROOT.glob(pattern + "*"))
    if cands:
        return cands[0]
    raise FileNotFoundError(pattern)

b = find_bundle('TOE_duad_algebra_v06_20260227_bundle')
print('bundle',b)
print('is_file', b.is_file(), 'is_dir', b.is_dir())
if b.is_file():
    with zipfile.ZipFile(b) as z:
        print('contents sample', z.namelist()[:10])
