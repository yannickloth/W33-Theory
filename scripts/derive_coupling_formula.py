"""Attempt to derive simple coupling formulas from projection data.

We have three grade-average means `x` (for g1,g2,g0_e6) and three Frobenius
weights `y`.  We try relationships of the form

    y_i = C * x_i^p           (power law)
    y_i = C * x_i^{-p}        (inverse power law)
    y_i = C * t_i * x_i^{-p}  (include triangle count)

and print fitted parameters and residuals.  ``x`` and ``t`` come from
`data/simple_edge_projections.json`.
"""

import json, numpy as np

# load data
proj = json.loads(open('data/simple_edge_projections.json').read())['simple_stats']
qca = json.loads(open('data/w33_algebra_qca.json').read())
fw = np.array(qca['theorem4_5']['frob_weights'])

# compute grade averages as before
grade_vals = {}
tri_vals = {}
var_vals = {}
dist_vals = {}
for e in proj:
    g = e['grade']
    grade_vals.setdefault(g, []).append(e['incident_stats'][0][0])
    var_vals.setdefault(g, []).append(e['incident_variance'][0])
    tri_vals.setdefault(g, []).append(e['triangles'])
    dist_vals.setdefault(g, []).append(e['mean_dist_to_simples'])
avg = {g: np.mean(vals) for g, vals in grade_vals.items()}
avg_var = {g: np.mean(vals) for g, vals in var_vals.items()}
avg_tri = {g: np.mean(vals) for g, vals in tri_vals.items()}
avg_dist = {g: np.mean(vals) for g, vals in dist_vals.items()}

order = ['g1','g2','g0_e6']
x = np.array([avg[g] for g in order])
t = np.array([avg_tri[g] for g in order])
y = fw[:len(x)]

print('grade order', order)
x = np.array([avg[g] for g in order])
varx = np.array([avg_var[g] for g in order])
t = np.array([avg_tri[g] for g in order])
d = np.array([avg_dist[g] for g in order])
print('x', x)
print('var', varx)
print('triangles', t)
print('dist', d)
print('y', y)

# helper to fit power law and compute residuals

def fit_power(x, y):
    # log y = log C + p log x
    lx = np.log(x)
    ly = np.log(y)
    A = np.vstack([lx, np.ones(len(lx))]).T
    p, logC = np.linalg.lstsq(A, ly, rcond=None)[0]
    C = np.exp(logC)
    ypred = C * x**p
    rss = np.sum((y - ypred)**2)
    return p, C, rss, ypred

print('\n-- power law y = C x^p --')
p, C, rss, ypred = fit_power(x, y)
print('p,C,rss', p, C, rss)
print('ypred', ypred)

print('\n-- inverse power y = C x^{-p} --')
p2, C2, rss2, ypred2 = fit_power(x, y)  # same but we will report -p
print('p (should invert) =', -p2, 'C', C2)
print('ypred2', ypred2)

# compute p from pairwise ratios
print('\n-- pairwise exponents for y ~ x^p --')
for i in range(len(x)):
    for j in range(i+1, len(x)):
        pj = np.log(y[i]/y[j]) / np.log(x[i]/x[j])
        print(f'p_{i}{j} = {pj}')

print('\n-- pairwise exponents for y ~ x^{-p} --')
for i in range(len(x)):
    for j in range(i+1, len(x)):
        pj = -np.log(y[i]/y[j]) / np.log(x[i]/x[j])
        print(f'p_{i}{j} = {pj}')

# include triangles: try y ~ C * t * x^{-p}
def fit_tri(x,y,t):
    # y/t = C x^{-p}
    yt = y / t
    # log(yt) = log C - p log x
    lx = np.log(x)
    lyt = np.log(yt)
    A = np.vstack([lx, np.ones(len(lx))]).T
    negp, logC = np.linalg.lstsq(A, lyt, rcond=None)[0]
    p = -negp
    C = np.exp(logC)
    ypred = C * t * x**(-p)
    rss = np.sum((y - ypred)**2)
    return p, C, rss, ypred

p3, C3, rss3, ypred3 = fit_tri(x,y,t)
print('\n-- with triangles y = C t x^{-p} --')
print('p,C,rss', p3, C3, rss3)
print('ypred3', ypred3)

# show which formula gives best rss
rsses = [('x^p', rss), ('x^{-p}', rss2), ('t x^{-p}', rss3)]
rsses.sort(key=lambda kv: kv[1])
print('\nBest fit by rss:', rsses)

# try simple linear combinations and compute Pearson
cand = {
    'x': x,
    '1/x': 1/x,
    'var': varx,
    'var/x': varx/x,
    'x/tri': x/t,
    'var/tri': varx/t,
    '1/x*tri': t*(1/x),
    '1/x^2': 1/x**2,
    'dist': d,
}
print('\nCorrelation of various candidates with y:')
for name, vec in cand.items():
    corr = np.corrcoef(vec, y)[0,1]
    print(f'  {name}: {corr:.3f}')
