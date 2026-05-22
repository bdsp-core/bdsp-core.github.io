#!/usr/bin/env python3
"""Regenerate src/data/regions.json from the tutorial's testmesh.mat.

The parameter sphere is shaded by dynamical regime (Active rest / Seizure /
Bistable). The upstream MATLAB tutorial stores those regions as dense surface
meshes in testmesh.mat. Rendering tens of thousands of triangles in the browser
is too heavy, so this script downsamples them to a compact lat/lon label grid:
for each grid direction we record which region's mesh is nearest.

IMPORTANT - coordinate frame: the mesh is stored with the y-axis negated
relative to our curve/model frame (verified by confirming the model's ictal
point lands on the Seizure mesh only after flipping y). We therefore negate the
mesh y before classifying, so the grid lines up with curves.json and model.js.

Source of testmesh.mat (clone separately, not vendored here):
  https://github.com/Dynamotypes-for-Dummies   (e.g. Python-scripts/testmesh.mat)

Usage:
  python make_regions.py /path/to/.../Python-scripts/testmesh.mat \
      -o ../src/data/regions.json
"""
import argparse, json
import numpy as np
from scipy.io import loadmat
from scipy.spatial import cKDTree

RADIUS = 0.4
N_LAT = 73    # grid resolution (includes both poles)
N_LON = 145   # includes the 0==360 wrap

# mesh name -> (label index, region key). The two bistable meshes share a label.
REGIONS = [
    ("Active_restmesh",   "rest"),
    ("Seizure_mesh",      "seizure"),
    ("BCSmesh",           "bcs"),
    ("Bistable_Lcb_mesh", "lcb"),
]
COLORS = {"rest": "#EBEBEB", "seizure": "#E4B4D3", "bcs": "#F8F6B8", "lcb": "#F8F6B8"}
LABELS = {"rest": "Active rest", "seizure": "Seizure (limit cycle)",
          "bcs": "Bistable", "lcb": "Bistable (with limit cycle)"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("testmesh", help="path to testmesh.mat")
    ap.add_argument("-o", "--out", default="regions.json")
    args = ap.parse_args()

    d = loadmat(args.testmesh)
    trees = []
    for name, _ in REGIONS:
        V = d[name]["vertices"][0][0].astype(float).copy()
        V[:, 1] = -V[:, 1]                       # flip y into our frame
        trees.append(cKDTree(V))

    lats = np.linspace(-90, 90, N_LAT)
    lons = np.linspace(0, 360, N_LON)
    grid = []
    for la in lats:
        lar = np.radians(la)
        row = ""
        for lo in lons:
            lor = np.radians(lo)
            p = np.array([RADIUS * np.cos(lar) * np.cos(lor),
                          RADIUS * np.sin(lar),
                          RADIUS * np.cos(lar) * np.sin(lor)])
            best_i, best_d = 0, 1e9
            for i, t in enumerate(trees):
                dist, _ = t.query(p)
                if dist < best_d:
                    best_d, best_i = dist, i
            row += str(best_i)
        grid.append(row)

    out = {"nLat": N_LAT, "nLon": N_LON,
           "regions": [k for _, k in REGIONS],
           "colors": COLORS, "labels": LABELS, "grid": grid}
    with open(args.out, "w") as f:
        json.dump(out, f)
    from collections import Counter
    print(f"wrote {args.out}  cells:", dict(Counter("".join(grid))))


if __name__ == "__main__":
    main()
