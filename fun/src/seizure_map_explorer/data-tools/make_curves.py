#!/usr/bin/env python3
"""Regenerate src/data/curves.json from the Dynamotypes-for-Dummies .mat files.

curves.json is the curated set of bifurcation curves drawn on the parameter
sphere, each tagged with its dynamotype and onset/offset role. The raw curves
live in the upstream MATLAB tutorial as curves.mat / curves2.mat. This script
reproduces the committed curves.json exactly (coordinates rounded to 4 dp).

Source of the .mat files (clone separately, not vendored here):
  https://github.com/Dynamotypes-for-Dummies   (e.g. Python-scripts/curves*.mat)

Usage:
  python make_curves.py /path/to/dynamotypes-for-dummies-tutorial/Python-scripts \
      -o ../src/data/curves.json
"""
import argparse, json, os
import numpy as np
from scipy.io import loadmat

RADIUS = 0.4

# (label, dynotype, role, source .mat, key in that .mat, target #points)
# Hopf and FLC are decimated to keep the rendered curve light; the rest are
# taken whole. Decimation stride = round(n_raw / n_target); first n_target kept.
SPEC = [
    ("SNIC", "SNIC", "both",   "curves2", "SNIC",            44),
    ("Hopf", "SupH", "both",   "curves2", "Hopf",           122),
    ("subH", "SubH", "onset",  "curves",  "subH",            12),
    ("SN",   "SN",   "onset",  "curves",  "SNl_ActiveRest",  63),
    ("FLC",  "FLC",  "offset", "curves2", "FLC",            150),
    ("SH",   "SH",   "offset", "curves2", "SHl",            112),
]


def get_curve(mat, key):
    a = np.asarray(mat[key])
    if a.ndim != 2:
        raise ValueError(f"{key}: expected 2D array, got {a.shape}")
    return a if a.shape[1] == 3 else a.T  # -> (N, 3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mat_dir", help="directory holding curves.mat and curves2.mat")
    ap.add_argument("-o", "--out", default="curves.json")
    args = ap.parse_args()

    mats = {name: loadmat(os.path.join(args.mat_dir, f"{name}.mat"))
            for name in ("curves", "curves2")}

    curves = []
    for label, dyno, role, src, key, target in SPEC:
        raw = get_curve(mats[src], key)
        n = len(raw)
        stride = max(1, round(n / target))
        idx = np.arange(0, n, stride)[:target]
        pts = np.round(raw[idx], 4).tolist()
        curves.append({"label": label, "dyno": dyno, "role": role, "pts": pts})

    with open(args.out, "w") as f:
        json.dump({"radius": RADIUS, "curves": curves}, f)
    print(f"wrote {args.out}: {len(curves)} curves, "
          f"{sum(len(c['pts']) for c in curves)} points")


if __name__ == "__main__":
    main()
