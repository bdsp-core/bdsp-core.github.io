#!/usr/bin/env python3
"""Regenerate src/data/curves.json from the Dynamotypes-for-Dummies .mat files.

curves.json is the set of bifurcation curves drawn on the parameter sphere,
each tagged with its dynamotype and onset/offset role. We use the COMPLETE
curves the MATLAB GUI plots, which live in bifurcation_crossing.mat:

  Fold                 -> the closed saddle-node "football" (orange onset curve)
  Hopf                 -> supercritical Hopf loop (green)
  Fold_of_cycles       -> fold of limit cycles (magenta FLC offset)
  Homoclinic_to_saddle -> saddle homoclinic (blue SH offset)

SNIC and the subcritical-Hopf arc aren't in that file, so they come from
curves2.mat / curves.mat. (An earlier version mistakenly used a single
fragment of the Fold from curves.mat, which is why the orange curve was an
open arc instead of the closed football.)

Source of the .mat files (clone separately, not vendored here):
  https://github.com/Dynamotypes-for-Dummies   (e.g. Python-scripts/*.mat)

Usage:
  python make_curves.py /path/to/dynamotypes-for-dummies-tutorial/Python-scripts \
      -o ../src/data/curves.json
"""
import argparse, json, os
import numpy as np
from scipy.io import loadmat

RADIUS = 0.4

# (label, dynotype, role, source .mat, key, target #points | None=all, dashed?, slice)
# The blue saddle-homoclinic offset curve is split across four segments in the
# data; including all of them makes the bifurcation boundary continuous (the
# magenta FLC joins the homoclinic, which chains around to the orange SNIC).
# `dashed` reproduces the MATLAB line styles (subcritical / unstable branches);
# the Hopf curve is split so its subcritical first half is dashed like MATLAB.
SPEC = [
    ("SN",   "SN",   "onset",  "bifurcation_crossing", "Fold",                  None, False, None),
    ("Hopf", "SupH", "both",   "bifurcation_crossing", "Hopf",                  None, True,  (0, 400)),
    ("Hopf", "SupH", "both",   "bifurcation_crossing", "Hopf",                  None, False, (400, None)),
    ("SNIC", "SNIC", "both",   "curves2",              "SNIC",                  None, True,  None),
    ("subH", "SubH", "onset",  "curves",               "subH",                  None, False, None),
    ("FLC",  "FLC",  "offset", "bifurcation_crossing", "Fold_of_cycles",        None, False, None),
    ("SH",   "SH",   "offset", "bifurcation_crossing", "Homoclinic_to_saddle",  None, False, None),
    ("SH",   "SH",   "offset", "bifurcation_crossing", "Homoclinic_to_saddle1", None, True,  None),
    ("SH",   "SH",   "offset", "bifurcation_crossing", "Homoclinic_to_saddle2", None, False, None),
    ("SH",   "SH",   "offset", "bifurcation_crossing", "Homoclinic_to_saddle3", None, True,  None),
]


def get_curve(mat, key):
    a = np.asarray(mat[key])
    if a.ndim != 2:
        raise ValueError(f"{key}: expected 2D array, got {a.shape}")
    a = a if a.shape[1] == 3 else a.T  # -> (N, 3)
    # The .mat data is stored in the plot frame (mu2, -mu1, nu); negate y to get
    # the model frame (mu2, mu1, nu) used by model.js, by the clicked waypoints,
    # and by regions.json. Without this the curves are mirrored relative to the
    # shaded regions and don't sit on the region boundaries.
    a = a.copy(); a[:, 1] = -a[:, 1]
    return a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mat_dir", help="dir with bifurcation_crossing.mat, curves.mat, curves2.mat")
    ap.add_argument("-o", "--out", default="curves.json")
    args = ap.parse_args()

    mats = {name: loadmat(os.path.join(args.mat_dir, f"{name}.mat"))
            for name in ("bifurcation_crossing", "curves", "curves2")}

    curves = []
    for label, dyno, role, src, key, target, dashed, rng in SPEC:
        raw = get_curve(mats[src], key)
        if rng is not None:
            raw = raw[rng[0]:rng[1]]
        if target is None or target >= len(raw):
            idx = np.arange(len(raw))
        else:
            stride = max(1, round(len(raw) / target))
            idx = np.arange(0, len(raw), stride)[:target]
        pts = np.round(raw[idx], 4).tolist()
        c = {"label": label, "dyno": dyno, "role": role, "pts": pts}
        if dashed:
            c["dash"] = True
        curves.append(c)

    with open(args.out, "w") as f:
        json.dump({"radius": RADIUS, "curves": curves}, f)
    print(f"wrote {args.out}: {len(curves)} curves, "
          f"{sum(len(c['pts']) for c in curves)} points")
    for c in curves:
        print(f"  {c['label']:5s} {c['dyno']:5s} {c['role']:6s} {len(c['pts'])} pts")


if __name__ == "__main__":
    main()
