# Source for the seizure dynamotype map explorer

This is the React source for the deployed `fun/seizure_map_explorer.html` (a
self-contained esbuild bundle). The HTML is a build artifact — **edit the
sources here, then rebuild**, don't hand-edit the HTML.

## Files
- `src/App.jsx` — the explorer UI: the rotatable parameter sphere (shaded by
  dynamical regime, with the real bifurcation curves), onset/offset waypoint
  placement, dynamotype classification, and the trace + spectrogram panels.
- `src/model.js` — the faithful Saggio fast-slow model. Integrates the fast
  subsystem continuously along the great-circle arc between waypoints; a seizure
  emerges only if the path actually crosses into the limit-cycle (seizure)
  region (hysteresis-respecting), otherwise it returns a calm resting baseline.
- `src/synth.jsx` — the validated normal-form ("fast") signal engine plus the
  shared `TraceCanvas` / `SpectroCanvas` / `Slider` components and palette.
- `src/data/curves.json` — the real exported Saggio bifurcation curves
  (radius-0.4 sphere), tagged by dynamotype and onset/offset role.
- `src/data/regions.json` — dynamical-regime label grid (Active rest / Seizure /
  Bistable), downsampled from the MATLAB tutorial's `testmesh.mat`, used to shade
  the sphere. Built in the model frame (mesh y negated to match the curve frame).

## Rebuild the app

Dependencies are pinned in `package.json` / `package-lock.json` (React 18.3.1,
esbuild 0.28). The committed `src/` + `src/data/*.json` are all you need.

```bash
cd fun/src/seizure_map_explorer
npm ci                     # or: npm install
./build.sh                 # emits seizure_map_explorer.html
cp seizure_map_explorer.html ../../seizure_map_explorer.html
```

`build.sh` bundles `src/main.jsx` with esbuild (`--bundle --minify
--format=iife --jsx=automatic --loader:.json=json`) and wraps the result in the
self-contained HTML shell.

## Regenerating the data (optional)

`src/data/curves.json` and `src/data/regions.json` are committed, so you only
need this if you want to re-derive them from the upstream MATLAB tutorial. The
scripts in `data-tools/` reproduce the committed files byte-for-byte.

```bash
# clone the upstream data source (the .mat files are NOT vendored here):
#   https://github.com/Dynamotypes-for-Dummies
pip install -r data-tools/requirements.txt          # numpy, scipy
MAT=/path/to/dynamotypes-for-dummies-tutorial/Python-scripts
python data-tools/make_curves.py  "$MAT"            -o src/data/curves.json
python data-tools/make_regions.py "$MAT/testmesh.mat" -o src/data/regions.json
```

- `make_curves.py` — extracts and tags the bifurcation curves from
  `curves.mat` / `curves2.mat` (which `.mat` key maps to which dynamotype/role,
  and the decimation, are documented in the script's `SPEC`).
- `make_regions.py` — downsamples the dense region meshes in `testmesh.mat`
  into the lat/lon shading grid, flipping the mesh y-axis into our frame.
