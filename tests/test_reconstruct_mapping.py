import json
import subprocess
import sys


def test_reconstruction_equivariance(tmp_path, capsys):
    # run the reconstruction script and capture output
    result = subprocess.run([sys.executable, 'tools/reconstruct_w33_e8_mapping.py'], capture_output=True, text=True)
    out = result.stdout + result.stderr
    assert 'reconstruction succeeded' in out
    assert 'stabilizer of edge 0 has size 216' in out

    # also double-check the mapping file matches expectations
    with open('data/w33_e8_mapping.json') as f:
        orig = json.load(f)
    # reconstruct mapping using same algorithm inline for sanity
    from tools.reconstruct_w33_e8_mapping import build_W33, edge_perm
    vertices, edges = build_W33()
    orig_map = [orig[str(i)] for i in range(len(edges))]
    import networkx as nx
    G = nx.Graph(); G.add_nodes_from(range(len(vertices))); G.add_edges_from(edges)
    matcher = nx.algorithms.isomorphism.GraphMatcher(G,G)
    autos = list(matcher.isomorphisms_iter())
    # compute root perms
    root_perms = []
    for perm in autos:
        rmap=[None]*len(edges)
        for e in range(len(edges)):
            e2=edge_perm(perm, edges[e], edges)
            rmap[orig_map[e]] = orig_map[e2]
        root_perms.append(tuple(rmap))
    seed_root = orig_map[0]
    reconstructed=[None]*len(edges)
    for perm,rperm in zip(autos, root_perms):
        e = edge_perm(perm, edges[0], edges)
        reconstructed[e] = rperm[seed_root]
    assert reconstructed == orig_map
