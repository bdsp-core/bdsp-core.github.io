#!/usr/bin/env python3
"""Regenerate src/data/regions.json from the tutorial's testmesh.mat.

The parameter sphere is shaded by dynamical regime (Active rest / Seizure /
Bistable). The upstream MATLAB tutorial stores those regions as dense surface
meshes in testmesh.mat. Rendering tens of thousands of triangles in the browser
is too heavy, so this script downsamples them to a compact lat/lon label grid.

Classification is by RAY-TRIANGLE CONTAINMENT (per region), not nearest vertex:
for each grid direction we test whether the ray from the origin actually passes
through one of a region's triangles. This matters because the meshes are
PATCHES that cover only ~40% of the sphere (the rest is undefined / plain base
sphere in MATLAB), and the seizure mesh is ~10x denser than the bistable ones --
nearest-vertex would let the dense mesh swallow the sparse regions and assign
the empty 60% to whatever mesh happened to be closest. Directions inside no
patch are labelled `rest` (index 0) so they render as the gray base sphere,
exactly as MATLAB shows them.

IMPORTANT - coordinate frame: the mesh is stored with the y-axis negated
relative to our curve/model frame (verified by confirming the model's ictal
point lands on the Seizure mesh only after flipping y). We negate the mesh y
before classifying, so the grid lines up with curves.json and model.js.

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
# Fine grid: the app renders the regions per screen-pixel (sampling this grid),
# so resolution here sets how smooth the region boundaries look. ~1 degree.
N_LAT = 181   # grid resolution (includes both poles)
N_LON = 361   # includes the 0==360 wrap
K_NEAR = 14   # candidate triangles per region to test for containment

# mesh name -> region key. The two bistable meshes share a colour.
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
    tris, trees = [], []
    for name, _ in REGIONS:
        V = d[name]["vertices"][0][0].astype(float).copy()
        V[:, 1] = -V[:, 1]                       # flip y into our frame
        F = d[name]["faces"][0][0].astype(int)
        if F.min() >= 1:
            F = F - 1                            # MATLAB 1-indexed -> 0-indexed
        tri = V[F]                                # (n_faces, 3, 3)
        tris.append(tri)
        trees.append(cKDTree(tri.mean(1)))        # KD-tree of triangle centroids

    def classify(D):
        """region index containing direction D (ray from origin), or 0 if none."""
        best, best_t = 0, np.inf
        for ri in range(len(REGIONS)):
            tri = tris[ri]
            _, idx = trees[ri].query(D, k=K_NEAR)
            for ti in np.atleast_1d(idx):
                v0, v1, v2 = tri[ti]
                e1, e2 = v1 - v0, v2 - v0
                h = np.cross(D, e2); a = e1 @ h
                if abs(a) < 1e-12:
                    continue
                f = 1.0 / a; s = -v0
                u = f * (s @ h)
                if u < -1e-6 or u > 1 + 1e-6:
                    continue
                q = np.cross(s, e1); v = f * (D @ q)
                if v < -1e-6 or u + v > 1 + 1e-6:
                    continue
                t = f * (e2 @ q)
                if 0 < t < best_t:
                    best_t, best = t, ri
        return best

    lats = np.radians(np.linspace(-90, 90, N_LAT))
    lons = np.radians(np.linspace(0, 360, N_LON))
    grid = []
    for lar in lats:
        cla, sla = np.cos(lar), np.sin(lar)
        row = []
        for lor in lons:
            D = np.array([RADIUS * cla * np.cos(lor), RADIUS * sla, RADIUS * cla * np.sin(lor)])
            row.append(str(classify(D)))
        grid.append("".join(row))

    out = {"nLat": N_LAT, "nLon": N_LON,
           "regions": [k for _, k in REGIONS],
           "colors": COLORS, "labels": LABELS, "grid": grid}
    with open(args.out, "w") as f:
        json.dump(out, f)
    from collections import Counter
    print(f"wrote {args.out}  cells:", dict(Counter("".join(grid))))


if __name__ == "__main__":
    main()
