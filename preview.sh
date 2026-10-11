#!/bin/sh
# Preview the site locally at http://localhost:4000
#   ./preview.sh         exactly as visitors would see it
#   ./preview.sh notes   with yellow review notes marking what still needs input
# Uses the gems already installed in the main checkout's vendor/bundle.
cd "$(dirname "$0")" || exit 1
CONFIGS="_config.yml,_config_preview.yml,_config_preview_clean.yml"
if [ "$1" = "notes" ]; then CONFIGS="_config.yml,_config_preview.yml"; shift; fi
exec bundle exec jekyll serve --config "$CONFIGS" --port 4000 "$@"
