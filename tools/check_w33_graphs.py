import sys
sys.path.append(str((__import__('pathlib').Path(__file__).resolve().parents[1])))
from tools.compute_w33_duality import generate_w33, build_incidence
import networkx as nx

points, lines = generate_w33()
inc_pt, inc_lin = build_incidence(points, lines)

Gpt = nx.Graph()
Gln = nx.Graph()
for i in range(40):
    Gpt.add_node(i)
    Gln.add_node(i)
for p in range(40):
    for l in inc_pt[p]:
        for q in inc_lin[l]:
            if q != p:
                Gpt.add_edge(p, q)
for l in range(40):
    for p in inc_lin[l]:
        for lp in inc_lin[l]:
            if p != lp:
                Gln.add_edge(l, lp)

print('point graph edges', Gpt.number_of_edges())
print('line graph edges', Gln.number_of_edges())
print('point graph degree histogram', sorted([d for n,d in Gpt.degree()]))
print('line graph degree histogram', sorted([d for n,d in Gln.degree()]))

GM = nx.algorithms.isomorphism.GraphMatcher(Gpt, Gln)
mapping = None
for m in GM.isomorphisms_iter():
    mapping = m
    break
print('mapping found?', mapping is not None)
if mapping:
    print('first mapping sample', list(mapping.items())[:10])
