#!/bin/sh
# Preview the site locally at http://localhost:4000
#   ./preview.sh         with the yellow review notes
#   ./preview.sh clean   exactly as visitors would see it
# Uses the gems already installed in the main checkout's vendor/bundle.
cd "$(dirname "$0")" || exit 1
CONFIGS="_config.yml,_config_preview.yml"
if [ "$1" = "clean" ]; then CONFIGS="$CONFIGS,_config_preview_clean.yml"; shift; fi
exec bundle exec jekyll serve --config "$CONFIGS" --port 4000 "$@"
