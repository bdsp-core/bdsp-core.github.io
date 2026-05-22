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

## Rebuild

```bash
cd fun/src/seizure_map_explorer
npm init -y >/dev/null
npm install react@18.3.1 react-dom@18.3.1 esbuild
./build.sh                 # emits seizure_map_explorer.html
cp seizure_map_explorer.html ../../seizure_map_explorer.html
```

`build.sh` bundles `src/main.jsx` with esbuild (`--bundle --minify
--format=iife --jsx=automatic --loader:.json=json`) and wraps the result in the
self-contained HTML shell.
