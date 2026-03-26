"""Root-span identification of the explicit K3 rank-16 complement.

The explicit K3 lattice split ``H^2(K3, Z) = 3U (+) N16`` leaves one remaining
classification question on the negative-definite side: is the rank-16 even
unimodular complement ``N16`` the ``E8(-1) (+) E8(-1)`` lattice or the negative
``D16^+`` lattice?

The decisive exact invariant is the span of the norm-2 roots. In ``D16^+`` the
roots span the index-2 ``D16`` root lattice, while in ``E8 (+) E8`` they span
the full lattice. This module computes the roots of the explicit complement and
their Smith data, showing that the root span has index ``1``. Under the
standard rank-16 even-unimodular classification, the explicit complement is
therefore ``E8(-1) (+) E8(-1)``.
"""

from __future__ import annotations

import ast
from functools import lru_cache
import json
from math import prod
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any

import numpy as np


if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    ROOT = Path(__file__).resolve().parents[1]

from w33_k3_three_u_complement_refinement_bridge import (
    build_k3_three_u_complement_refinement_bridge_summary,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_k3_n16_e8e8_bridge_summary.json"


def _gp_available() -> bool:
    return shutil.which("gp") is not None


def _parse_vectors(path: Path) -> np.ndarray:
    rows: list[list[int]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if text:
                rows.append(list(ast.literal_eval(text)))
    return np.asarray(rows, dtype=int).T


def _parse_diagonal(path: Path) -> list[int]:
    return [int(value) for value in ast.literal_eval(path.read_text(encoding="utf-8").strip())]


@lru_cache(maxsize=1)
def build_k3_n16_e8e8_bridge_summary() -> dict[str, Any]:
    if not _gp_available():
        raise RuntimeError("PARI/GP executable 'gp' is required for the N16 classification theorem")

    complement_form = build_k3_three_u_complement_refinement_bridge_summary()[
        "three_u_complement_seed_form"
    ]
    positive_form = [[-value for value in row] for row in complement_form]

    with tempfile.TemporaryDirectory(prefix="w33_n16_roots_") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        roots_path = temp_dir / "roots_cols.txt"
        smith_path = temp_dir / "smith_diag.txt"
        script_path = temp_dir / "roots.gp"
        q = "[" + ";".join(",".join(str(value) for value in row) for row in positive_form) + "]"

        script_path.write_text(
            "\n".join(
                [
                    f"Q = {q};",
                    "R = qfminim(Q, 2)[3];",
                    f'for (j = 1, matsize(R)[2], write("{roots_path.as_posix()}", Vec(R[,j])));',
                    "d = matsnf(R);",
                    f'write("{smith_path.as_posix()}", Vec(d));',
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        subprocess.run(
            ["gp", "-q", str(script_path)],
            check=True,
            capture_output=True,
            text=True,
            timeout=180,
        )

        root_representatives = _parse_vectors(roots_path)
        smith_diagonal = _parse_diagonal(smith_path)

    smith_index = int(prod(smith_diagonal))
    root_span_rank = len(smith_diagonal)
    root_rep_count = int(root_representatives.shape[1])
    total_roots = 2 * root_rep_count

    return {
        "status": "ok",
        "root_representative_count": root_rep_count,
        "total_root_count": total_roots,
        "root_span_smith_diagonal": smith_diagonal,
        "root_span_rank": root_span_rank,
        "root_span_index": smith_index,
        "sample_root_representatives": root_representatives[:, :8].astype(int).T.tolist(),
        "n16_classification_theorem": {
            "n16_has_480_roots": total_roots == 480,
            "root_span_has_full_rank_16": root_span_rank == 16,
            "root_span_index_is_1": smith_index == 1,
            "root_span_equals_the_full_lattice": root_span_rank == 16 and smith_index == 1,
            "explicit_n16_is_not_d16_plus": smith_index != 2,
            "explicit_n16_is_e8_plus_e8_by_rank16_even_unimodular_classification": (
                total_roots == 480 and root_span_rank == 16 and smith_index == 1
            ),
        },
        "bridge_verdict": (
            "The explicit rank-16 complement is not just an unnamed even "
            "unimodular negative lattice. Its norm-2 roots already span the full "
            "lattice with Smith index 1. Under the standard rank-16 "
            "even-unimodular classification, that rules out D16^+ and identifies "
            "the explicit complement as E8(-1) (+) E8(-1)."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_n16_e8e8_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
