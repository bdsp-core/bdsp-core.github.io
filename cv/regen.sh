#!/usr/bin/env bash
# Regenerate cv/pages/*.jpg from cv/1-Westover_CV.pdf and update the page
# count in cv/index.html.
#
# === FOR LOCAL TESTING ONLY ===
# The production CV pipeline (private repo: mb-westover/cv-build) runs every
# Sunday, rebuilds the PDF + DOCX, regenerates the 44 JPEGs in this folder,
# and updates the page count in index.html automatically. You do NOT need to
# run this script after editing the source Google Docs/Sheets — the cloud
# workflow handles it.
#
# Use this script when you want to verify locally how an updated PDF will
# render before pushing, e.g. after testing a pipeline change in build_cv/.
#
# Usage:
#   ./cv/regen.sh
#
# Requires: pdftoppm (brew install poppler).

set -euo pipefail
cd "$(dirname "$0")"

PDF="1-Westover_CV.pdf"
[ -f "$PDF" ] || { echo "Missing $PDF in $(pwd)"; exit 1; }

rm -f pages/*.jpg
mkdir -p pages
pdftoppm -r 90 -jpeg -jpegopt quality=75,optimize=y,progressive=y "$PDF" pages/page

N=$(find pages -name 'page-*.jpg' | wc -l | tr -d ' ')

# Update the Liquid loop range and the "page N / N" suffix in index.html.
sed -i.bak -E "s/\(1\.\.[0-9]+\)/(1..$N)/" index.html
sed -i.bak -E "s|(page \{\{ i \}\} / )[0-9]+|\1$N|" index.html
rm -f index.html.bak

echo "Done: $N pages regenerated."
echo "Total: $(du -sh pages/ | cut -f1)"
