# Source for the Fun-page interactive tools

This directory holds the source for the browser tools deployed under `fun/`.
Each deployed `.html` is a **self-contained esbuild bundle** (a build artifact) —
**edit the source here and rebuild; don't hand-edit the HTML.**

All three tools illustrate the Saggio–Jirsa seizure-dynamotype taxonomy and are
based on the same paper:

> Sheckler C, Kish K, Walker Z, Barkelew G, Crisp DN, Szuromi MP, Saggio ML,
> Stacey WC. *Dynamotypes for Dummies: A Toolbox, Atlas, and Tutorial for
> Simulating a Comprehensive Range of Realistic Synthetic Seizures.* eNeuro 2025;
> 12(10):ENEURO.0200-25.2025. doi:10.1523/ENEURO.0200-25.2025.
> Code: https://github.com/Dynamotypes-for-Dummies

## Tools

| Deployed HTML | Source | Notes |
|---|---|---|
| `fun/dynamotype_quiz.html` | `dynamotype_quiz.jsx` | single-file React; recognition quiz + phase-portrait triptych |
| `fun/onset_offset_anim.html` | `onset_offset_anim.jsx` | single-file React; animated onset/offset phase portraits |
| `fun/seizure_map_explorer.html` | `seizure_map_explorer/` | multi-file; parameter-sphere explorer with the real fast-slow model. See its own `README.md`. |

## Rebuilding the single-file tools (quiz, animator)

These are standalone `.jsx` files bundled with esbuild and wrapped in an HTML
shell. React 18.3.1.

```bash
TOOL=dynamotype_quiz          # or: onset_offset_anim
mkdir -p build/src && cd build
cp ../$TOOL.jsx src/App.jsx
cat > src/main.jsx <<'JS'
import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
createRoot(document.getElementById("root")).render(React.createElement(App));
JS
npm init -y >/dev/null
npm install react@18.3.1 react-dom@18.3.1 esbuild
./node_modules/.bin/esbuild src/main.jsx --bundle --minify --format=iife \
  --jsx=automatic --define:process.env.NODE_ENV='"production"' --outfile=app.js
```

Then wrap `app.js` in the HTML shell (a minimal `<head>`/`<body>` with
`<div id="root">` + `<script>app.js</script>`; see the git history of the
deployed `.html` for the exact wrapper) and copy over `fun/$TOOL.html`.

### What the phase-portrait triptych adds (quiz)

After you answer, each feedback card shows three schematic state-space pictures
(rest → bifurcation → oscillating; reversed for offsets). The scene data +
renderer live in the `PHASE`, `PhasePortrait`, and `PhaseSequence` definitions
just above the `Feedback` component in `dynamotype_quiz.jsx`.

## Rebuilding the map explorer

It is multi-file (and ships a small data pipeline). See
`seizure_map_explorer/README.md` for build + data-regeneration instructions.
