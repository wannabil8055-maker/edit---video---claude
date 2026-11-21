"""Download the CC0 Poly Haven assets used by house3d.py into ./assets3d/.

Usage: python3 fetch_assets.py
All assets are CC0 (public domain) from https://polyhaven.com.
"""
import json
import os
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DST = os.path.join(HERE, "assets3d")
API = "https://api.polyhaven.com/files/"

HDRIS = {"kloofendal_48d_partly_cloudy_puresky": "4k"}
TEXTURES = {
    "grey_roof_tiles_02": "2k",
    "painted_plaster_wall": "2k",
    "stacked_stone_wall": "2k",
    "brushed_concrete": "2k",
    "grass_ground": "2k" if False else "1k",
    "floor_tiles_06": "1k",
    "aerial_grass_rock": "2k",
}
MODELS = {
    "island_tree_01": "1k", "island_tree_02": "1k", "island_tree_03": "1k",
    "tree_small_02": "1k", "shrub_01": "1k", "shrub_02": "1k", "shrub_03": "1k", "shrub_04": "1k",
    "grass_medium_01": "1k", "grass_medium_02": "1k", "grass_bermuda_01": "1k",
    "potted_plant_02": "1k", "fern_02": "1k",
}
TEX_MAPS = ("Diffuse", "nor_gl", "Rough", "Displacement", "AO")


def get(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "video-render-script"})
    with urllib.request.urlopen(req, timeout=120) as r, open(path, "wb") as f:
        f.write(r.read())
    print("got", os.path.relpath(path, HERE))


def info(asset):
    req = urllib.request.Request(API + asset, headers={"User-Agent": "video-render-script"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def main():
    for a, res in HDRIS.items():
        f = info(a)["hdri"][res]["hdr"]
        get(f["url"], os.path.join(DST, "hdri", f"{a}.hdr"))
    for a, res in TEXTURES.items():
        d = info(a)
        for m in TEX_MAPS:
            if m in d and res in d[m]:
                fmt = "jpg" if "jpg" in d[m][res] else "png"
                get(d[m][res][fmt]["url"], os.path.join(DST, "tex", a, f"{m}.{fmt}"))
    for a, res in MODELS.items():
        d = info(a)["blend"][res]["blend"]
        base = os.path.join(DST, "models", a)
        get(d["url"], os.path.join(base, f"{a}.blend"))
        for rel, inc in d.get("include", {}).items():
            get(inc["url"], os.path.join(base, rel))


if __name__ == "__main__":
    main()
