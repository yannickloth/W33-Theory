"""Compare Deligne/Vogel dimensions with Hodge heat entropy on W33.

We evaluate the heat kernel entropy at a set of times and juxtapose those
values with the Deligne-series dimensions for the corresponding t-parameters.
This rudimentary comparison may reveal whether the information-theoretic
behaviour of the geometry correlates with the universal Lie-algebra
parameterization.
"""
import sys
sys.path.append('.')
from e8_embedding_group_theoretic import build_w33
from w33_cellular_automaton import hodge_heat_evolution
from VOGEL_RESEARCH_FEB2026 import deligne_dim

# choose Deligne t-values and compute corresponding heat times (positive)
t_values = [-3, -2, -5/3, -1, 0, 1, 2, 3, 4]
heat_times = [abs(t) for t in t_values]  # heat parameter positive

n, verts, adj, edges = build_w33()
simplices = __import__('w33_homology').build_clique_complex(n, adj)

heat_results, evals = hodge_heat_evolution(simplices, heat_times)

print(f"{'t':>6} {'deligne dim':>12} {'entropy':>10} {'harmonic%':>10}")
for t, hr in zip(t_values, heat_results):
    ddim = deligne_dim(t)
    ent = hr['entropy']
    harm = hr['harmonic_fraction']
    print(f"{t:6} {str(ddim):>12} {ent:10.4f} {harm:10.4f}")
