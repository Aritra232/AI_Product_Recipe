#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Preparing generated data folder..."
mkdir -p Service/data

if [ ! -s Service/data/search_index.json ]; then
  echo '{"terms":[]}' > Service/data/search_index.json
elif command -v python3 >/dev/null 2>&1; then
  if ! python3 -m json.tool Service/data/search_index.json >/dev/null 2>&1; then
    echo "Existing search_index.json is invalid. Resetting it."
    echo '{"terms":[]}' > Service/data/search_index.json
  fi
fi

echo "Building and starting Docker container..."
docker compose up --build -d

echo "Waiting for API..."
for i in {1..30}; do
  if curl -fsS http://127.0.0.1:7011/health >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

echo "Rebuilding CSV/OpenAI search index..."
curl -fsS -X POST http://127.0.0.1:7011/admin/import-csv
echo

echo "Deployment complete."
curl -fsS http://127.0.0.1:7011/health
echo

