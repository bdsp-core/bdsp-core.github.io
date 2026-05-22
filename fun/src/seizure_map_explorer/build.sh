#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
./node_modules/.bin/esbuild src/main.jsx --bundle --minify --format=iife --jsx=automatic --loader:.json=json --define:process.env.NODE_ENV='"production"' --outfile=app.js
cat > seizure_map_explorer.html <<'HTML'
<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Seizure dynamotype map explorer</title>
<style>html,body{margin:0;padding:0;height:100%;background:#0e1014}#root{min-height:100%}</style>
</head><body><div id="root"></div><script>
HTML
cat app.js >> seizure_map_explorer.html
echo '</script></body></html>' >> seizure_map_explorer.html
echo "Built seizure_map_explorer.html ($(wc -c < seizure_map_explorer.html) bytes)"
