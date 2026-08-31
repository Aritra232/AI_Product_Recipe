#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p .git/hooks

cat > .git/hooks/post-merge <<'HOOK'
#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

echo "Git pull finished. Running automatic VPS deploy..."
./scripts/vps-after-pull.sh
HOOK

chmod +x .git/hooks/post-merge
chmod +x scripts/vps-after-pull.sh scripts/vps-deploy.sh

echo "Installed .git/hooks/post-merge"
echo "Future 'git pull' commands will rebuild/restart Docker automatically."
