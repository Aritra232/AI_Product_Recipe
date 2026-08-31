#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Pulling latest code..."
git pull

./scripts/vps-after-pull.sh
