import numpy as np, json

def load_cycles():
    d = json.load(open('data/h1_subspaces.json'))
    cycles = np.array(d['subspace_bases']).reshape(3*27, 81).T
    return cycles

# build triple tensor function

cycles = load_cycles()

# compute M(v) = cycles.T @ (cycles * (cycles.T @ v)[:,None])? hmm wrong
# Actually we want Y_{ijk} = sum_e cycles[e,i]*cycles[e,j]*cycles[e,k]
# then for given v_k, M_{ij}(v) = sum_k Y_{ijk} v_k
# = sum_{e,k} cycles[e,i]*cycles[e,j]*cycles[e,k]*v_k
# = sum_e cycles[e,i]*cycles[e,j]*(sum_k cycles[e,k] v_k)
# = sum_e cycles[e,i]*cycles[e,j]*(cycles[e,:] @ v)
# So M = cycles.T @ (cycles * (cycles @ v)[:,None])


def M_of_v(v):
    # v length 81
    rv = cycles @ v  # length 81
    return cycles.T @ (cycles * rv[:,None])

# now search for v maximizing eigenvalue ratio
import math

def ratio_of_v(v):
    M = M_of_v(v)
    vals = np.linalg.eigvalsh(M)
    vals = np.abs(vals)
    vals.sort()
    nonzero = vals[vals>1e-12]
    if len(nonzero)==0:
        return 0
    return math.sqrt(nonzero[-1]/nonzero[0])

# quick random search with tracking near specific targets
best = (None, 0)
targets = [40, 72, 301]
closest = {t: (None, float('inf')) for t in targets}  # (v, abs diff)
for it in range(10000):
    v = np.random.randn(81)
    v /= np.linalg.norm(v)
    r = ratio_of_v(v)
    if r > best[1]:
        best = (v.copy(), r)
    for t in targets:
        diff = abs(r - t)
        if diff < closest[t][1]:
            closest[t] = (v.copy(), diff)

print('random search best ratio', best[1])
for t in targets:
    print(f'closest ratio to {t}: r={ratio_of_v(closest[t][0]):.4f}, diff={closest[t][1]:.4f}')

# done
print('search complete')
