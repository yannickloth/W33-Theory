import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze
from tools import enumerate_minimal_certificates as enum

lines, sign_field = analyze._load_sign_field(Path("artifacts/e6_f3_trilinear_map.json"))
gl = analyze._gl2_3()
sl = [m for m in gl if m[4] == 1]
import inspect
import traceback

try:
    import inspect

    print("function object:", enum.exhaustive_enumeration)
    print("defined in:", enum.exhaustive_enumeration.__code__.co_firstlineno)
    print("source:")
    print(inspect.getsource(enum.exhaustive_enumeration))
    res = enum.exhaustive_enumeration(
        lines, sign_field, sl, 7, workers=1, progress=True
    )
    print("res type", type(res))
    print("res", res if res else "None")
except Exception as e:
    print("Exception:", type(e), e)
    traceback.print_exc()
