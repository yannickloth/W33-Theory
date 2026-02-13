#!/usr/bin/env python3
"""Download curated diagram images from fgmarcelis.wordpress.com into artifacts/fgmarcelis_images/"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, urlretrieve

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "artifacts" / "fgmarcelis_images"
OUT_DIR.mkdir(parents=True, exist_ok=True)

IMAGES = [
    # Fano plane & Fano cube
    "https://fgmarcelis.wordpress.com/wp-content/uploads/2022/12/fano_cube.png?w=1024",
    "https://fgmarcelis.wordpress.com/wp-content/uploads/2022/12/fano_cube_v2-2.png?w=1024",
    # Rhombicosidodecahedron / Reye
    "https://fgmarcelis.wordpress.com/wp-content/uploads/2022/11/reye_configuration.png?w=1024",
    "https://fgmarcelis.wordpress.com/wp-content/uploads/2022/11/double_6_rhombicosidodecahedron3.png?w=1024",
    "https://fgmarcelis.wordpress.com/wp-content/uploads/2022/11/double_6_rhombicosidodecahedron_15_clebsch.png?w=1024",
    # Klein quartic
    "https://fgmarcelis.wordpress.com/wp-content/uploads/2021/07/klein_quartic_geogebra_dubbel_color_buiten.png",
    # Steiner / PG(2,4)
    "https://fgmarcelis.wordpress.com/wp-content/uploads/2021/07/projplane3_s5612.gif",
    "https://fgmarcelis.wordpress.com/wp-content/uploads/2021/06/doily_pg24_mog_inf_circle_rot.png",
    # Heawood / harmonic cubes
    "https://fgmarcelis.wordpress.com/wp-content/uploads/2021/06/heawood_graph_pe15_pl7.png",
    # MOG / codes
    "https://fgmarcelis.wordpress.com/wp-content/uploads/2019/05/hexacode.png",
    "https://fgmarcelis.wordpress.com/wp-content/uploads/2019/05/mog_labels.png",
    # Witting / Penrose
    "https://fgmarcelis.wordpress.com/wp-content/uploads/2018/02/doily_pg24_empty-zimba_penrose.png",
    "https://fgmarcelis.wordpress.com/wp-content/uploads/2018/02/witting11_flat_241_norm1_circles_9_iiyy_2333.png",
]


def safe_filename(url: str) -> str:
    name = url.split("/")[-1]
    if "?" in name:
        name = name.split("?")[0]
    return name


if __name__ == "__main__":
    print("Downloading curated images to:", OUT_DIR)
    results = []
    for url in IMAGES:
        fname = safe_filename(url)
        outp = OUT_DIR / fname
        try:
            print(f" -> {fname}")
            urlretrieve(url, outp)
            results.append({"url": url, "file": str(outp), "status": "ok"})
        except (HTTPError, URLError) as e:
            print(f"   FAILED: {e}")
            results.append({"url": url, "file": None, "status": str(e)})
        except Exception as e:
            print(f"   FAILED: {e}")
            results.append({"url": url, "file": None, "status": str(e)})

    # summary
    ok = [r for r in results if r["status"] == "ok"]
    fail = [r for r in results if r["status"] != "ok"]
    print(f"\nDone — {len(ok)} downloaded, {len(fail)} failures.")
    sys.exit(0)
