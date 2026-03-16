import sys

sys.path.insert(0, r"c:\Repos\Theory of Everything")

from scripts.ce2_global_cocycle import predict_simple_family_uv, predict_fiber_family_uv

triple = ((22, 0), (0, 1), (0, 0))
print('triple', triple)

try:
    print('simple family:', predict_simple_family_uv(*triple))
except Exception as e:
    print('simple family error:', type(e).__name__, e)

try:
    print('fiber family:', predict_fiber_family_uv(*triple))
except Exception as e:
    print('fiber family error:', type(e).__name__, e)
