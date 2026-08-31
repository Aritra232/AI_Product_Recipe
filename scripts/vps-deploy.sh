#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ -n "$(git status --porcelain)" ]; then
  echo "Local VPS changes found. Stashing before pull..."
  git stash push --include-untracked -m "auto-stash before deploy $(date -Iseconds)"
fi

echo "Pulling latest code..."
git pull

./scripts/vps-after-pull.sh
