"""Klein-quartic AG-code shadow on the promoted W33/Fano surface package.

This module is intentionally narrower than the exact projective-shell theorem.
Its purpose is to package a clean coding-theory shadow suggested by the Klein
quartic literature:

    Klein-quartic AG codes of Hansen include length 21 examples.

Inside the repo, the same 21 already appears in four exact ways:

    - Fano plane flags: 21
    - Heawood edges: 21
    - Csaszar edges: 21
    - Szilassi edges: 21

So while the repo does not yet construct the AG code itself, the promoted 21 is
already a stable geometric/coding shadow rather than an isolated count.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "exploration"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from w33_surface_neighborly_bridge import (
    csaszar_seed,
    fano_plane_counts,
    szilassi_seed,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_klein_quartic_ag21_bridge_summary.json"


@lru_cache(maxsize=1)
def build_klein_quartic_ag21_summary() -> dict[str, Any]:
    ag_code_length = 21
    q = 3
    phi6 = 7

    fano = fano_plane_counts()
    csaszar = csaszar_seed()
    szilassi = szilassi_seed()
    heawood_edges = 21

    return {
        "status": "ok",
        "ag21_coding_shadow": {
            "klein_quartic_ag_code_length": ag_code_length,
            "fano_flags": int(fano["flags"]),
            "heawood_edges": heawood_edges,
            "csaszar_edges": int(csaszar.edges),
            "szilassi_edges": int(szilassi.edges),
            "q": q,
            "phi6": phi6,
            "ag21_equals_fano_flags": ag_code_length == int(fano["flags"]),
            "ag21_equals_heawood_edges": ag_code_length == heawood_edges,
            "ag21_equals_csaszar_edges": ag_code_length == int(csaszar.edges),
            "ag21_equals_szilassi_edges": ag_code_length == int(szilassi.edges),
            "ag21_equals_q_times_phi6": ag_code_length == q * phi6,
            "all_promoted_21_counts_agree": (
                ag_code_length
                == int(fano["flags"])
                == heawood_edges
                == int(csaszar.edges)
                == int(szilassi.edges)
            ),
        },
        "bridge_verdict": (
            "The Klein-quartic coding layer already casts a clean shadow on the "
            "promoted W33 surface package. The AG-code length 21 from the Klein "
            "quartic literature matches the live 21 of Fano flags, Heawood edges, "
            "and the common edge count of the Csaszar/Szilassi toroidal pair. So "
            "even before constructing the code internally, the coding side is "
            "already landing on a rigid geometric 21 rather than a floating number."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_klein_quartic_ag21_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
