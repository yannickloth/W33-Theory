"""Run a ternary cellular automaton on the 24-edge subgraph extracted earlier.

This explores whether the 24-plane corresponds to a particularly efficient
information network (low entropy, short periods, etc).  We reuse the CA
function from w33_cellular_automaton but build adjacency of the 24-edge set.
"""
import sys
sys.path.append('.')
from e8_embedding_group_theoretic import build_w33
from scripts.w33_cellular_automaton import ternary_cellular_automaton

# reconstruct the 24-edge set via extract_24_edges logic
from scripts.extract_24_edges import sel

# 'sel' is list of 6 four-cycles; compute union of their edges
n, verts, adj, edges = build_w33()
sub_edges = []
for cyc in sel:
    for idx in cyc:
        sub_edges.append(edges[idx])

# build adjacency for subgraph vertices
subs = sorted({v for e in sub_edges for v in e})
index_map = {v:i for i,v in enumerate(subs)}
adj24 = [[] for _ in subs]
for i,j in sub_edges:
    ai = index_map[i]; aj = index_map[j]
    adj24[ai].append(aj)
    adj24[aj].append(ai)

print('24-edge subgraph has', len(subs), 'vertices and', len(sub_edges), 'edges')

# run CA on this smaller graph
for rule in ['totalistic','majority','life']:
    ca=ternary_cellular_automaton(adj24, len(subs), rule_type=rule, steps=100)
    print(f"rule {rule}: period={ca['period']}, final entropy={ca['final_entropy']:.4f}")
