import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts.edge_to_e8_mapping import (
    plot_adj_preservation,
    plot_feature_embeddings,
    run_feature_hungarian_mapping,
)

if __name__ == "__main__":
    mapping, result, score_matrix, meta = run_feature_hungarian_mapping(
        write_artifact=True
    )
    fig1 = plot_feature_embeddings(mapping, score_matrix, meta)
    fig2 = plot_adj_preservation(mapping, meta)
    if fig1:
        print("Wrote", fig1)
    if fig2:
        print("Wrote", fig2)
