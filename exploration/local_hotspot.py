# Shim to expose local_hotspot_feasibility as a top-level importable module
# This makes dynamic import/reload in tests robust (importlib.reload can find a normal module spec)
from scripts.local_hotspot_feasibility import (
    build_edge_vectors,
    build_local_model,
    compute_embedding_matrix,
    generate_scaled_e8_roots,
    main,
    slice_pairs,
    test_forced_pairs,
)

__all__ = [
    "main",
    "compute_embedding_matrix",
    "generate_scaled_e8_roots",
    "build_edge_vectors",
    "slice_pairs",
    "test_forced_pairs",
    "build_local_model",
]
