import json, numpy as np
proj=json.loads(open('data/simple_edge_projections.json').read())['simple_stats']
qca=json.loads(open('data/w33_algebra_qca.json').read())
fw=np.array(qca['theorem4_5']['frob_weights'])
# averages per grade
grade_vals={}
for e in proj:
    g=e['grade']; grade_vals.setdefault(g,[]).append(e['incident_stats'][0][0])
avg={g:np.mean(vals) for g,vals in grade_vals.items()}
print('avg0 per grade',avg)
order=['g1','g2','g0_e6']
x=np.array([avg[g] for g in order])
y=fw[:len(x)]
print('x',x,'y',y)
A=np.vstack([x, np.ones(len(x))]).T
a,b=np.linalg.lstsq(A,y,rcond=None)[0]
print('fit coeff',a,b)
print('pred',a*x+b)
print('corr x vs y',np.corrcoef(x,y)[0,1])
print('corr 1/x vs y',np.corrcoef(1/x,y)[0,1])
print('corr log x vs y',np.corrcoef(np.log(x),y)[0,1])
# also compare ratios
rat_x = x / x[1]
rat_y = y / y[1]
print('ratio x/y', rat_x, rat_y)
print('corr ratios', np.corrcoef(rat_x, rat_y)[0,1])
