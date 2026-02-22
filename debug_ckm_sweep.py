import sys

sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
from scripts.w33_ckm_from_vev import (
    _build_hodge_and_generations,
    build_generation_profiles,
    build_h27_index_and_tris,
    compute_ckm_and_jarlskog,
    yukawa_from_vev_with_tris,
)

H, triangles, edges, gens = _build_hodge_and_generations()
n = max(max(u, v) for u, v in edges) + 1
adj = [[] for _ in range(n)]
for u, v in edges:
    adj[u].append(v)
    adj[v].append(u)
H27, local_tris = build_h27_index_and_tris(adj, v0=0)
_, _, X_profiles = build_generation_profiles(H, edges, gens, v0=0)

v_u = X_profiles[0].astype(complex)
print("profile length", len(v_u))
for idx in range(min(20, len(v_u))):
    for phase in (0.3, 0.6, 1.6):
        v_d = v_u.copy()
        v_d[idx] *= 1.0 + phase * 1j
        Y_u = yukawa_from_vev_with_tris(X_profiles, v_u, local_tris)
        Y_d = yukawa_from_vev_with_tris(X_profiles, v_d, local_tris)
        V, J = compute_ckm_and_jarlskog(Y_u, Y_d)
        s12, s23, s13 = abs(V[0, 1]), abs(V[1, 2]), abs(V[0, 2])
        print(
            f"idx={idx:2d} phase={phase:4.1f} -> s12={s12:.6f} s23={s23:.6f} s13={s13:.6f} J={J:.3e}"
        )
