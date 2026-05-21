# Source for the dynamotype quiz

`dynamotype_quiz.jsx` is the React source for the deployed
`fun/dynamotype_quiz.html` (a self-contained esbuild bundle). The HTML is a
build artifact — **edit the `.jsx`, then rebuild**, don't hand-edit the HTML.

## Rebuild

```bash
mkdir -p build/src && cd build
cp ../dynamotype_quiz.jsx src/App.jsx
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
# wrap app.js in the HTML shell (see git history of fun/dynamotype_quiz.html
# for the exact <head>/<body> wrapper), then copy over fun/dynamotype_quiz.html
```

## What the phase-portrait triptych adds

After you answer, each feedback card shows three schematic state-space
pictures (rest → bifurcation → oscillating; reversed for offsets). The scene
data + renderer live in the `PHASE`, `PhasePortrait`, and `PhaseSequence`
definitions just above the `Feedback` component in the `.jsx`.
