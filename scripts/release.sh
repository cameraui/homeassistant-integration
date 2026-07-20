#!/bin/bash
set -euo pipefail

# Bump the integration version in manifest.json, rebuild the Lovelace card bundle,
# commit, tag vX.Y.Z, push and cut a GitHub release. HACS installs from the tag.
#
#   scripts/release.sh patch
#   scripts/release.sh 0.3.0 --yes

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="custom_components/cameraui/manifest.json"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

usage() {
  cat <<EOF
Usage: scripts/release.sh <version|major|minor|patch> [--yes] [--skip-checks]

Examples:
  scripts/release.sh patch
  scripts/release.sh 0.3.0

Options:
  --yes, -y       Push without the confirmation prompt.
  --skip-checks   Skip the lint pre-flight (the card is always rebuilt).
EOF
  exit 1
}

SPEC="${1:-}"
YES=false
SKIP_CHECKS=false
for arg in "${@:2}"; do
  case "$arg" in
    --yes | -y) YES=true ;;
    --skip-checks) SKIP_CHECKS=true ;;
    *)
      echo "Unknown option: $arg"
      usage
      ;;
  esac
done

[ -z "$SPEC" ] && usage

cd "$ROOT"

command -v gh >/dev/null 2>&1 || {
  echo -e "${RED}gh CLI not found - needed to cut the GitHub release HACS installs from.${NC}"
  exit 1
}

# Safety: clean tree, on main, not behind origin.
if [ -n "$(git status --porcelain)" ]; then
  echo -e "${RED}Working tree not clean - commit or stash first.${NC}"
  exit 1
fi
branch="$(git rev-parse --abbrev-ref HEAD)"
if [ "$branch" != "main" ]; then
  echo -e "${RED}Not on main (on '$branch').${NC}"
  exit 1
fi
git fetch -q origin main || true
if [ -n "$(git rev-list HEAD..origin/main 2>/dev/null)" ]; then
  echo -e "${RED}Local main is behind origin/main - pull first.${NC}"
  exit 1
fi

cur="$(node -p "require('./$MANIFEST').version")"

bump() {
  local IFS='.'
  read -r ma mi pa <<<"$1"
  case "$2" in
    major) echo "$((ma + 1)).0.0" ;;
    minor) echo "$ma.$((mi + 1)).0" ;;
    patch) echo "$ma.$mi.$((pa + 1))" ;;
  esac
}

case "$SPEC" in
  major | minor | patch) NEW="$(bump "$cur" "$SPEC")" ;;
  *) NEW="$SPEC" ;;
esac

if ! echo "$NEW" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
  echo -e "${RED}Invalid version '$NEW' (expected X.Y.Z).${NC}"
  exit 1
fi

TAG="v$NEW"
if git rev-parse "$TAG" >/dev/null 2>&1; then
  echo -e "${RED}Tag $TAG already exists.${NC}"
  exit 1
fi

echo -e "${CYAN}Releasing integration: $cur -> $NEW (tag $TAG)${NC}"

if [ "$SKIP_CHECKS" = false ]; then
  echo -e "${YELLOW}Linting...${NC}"
  npm run lint
fi

echo -e "${YELLOW}Building card bundle...${NC}"
npm run build

node -e "const f='./$MANIFEST'; const j=require(f); j.version='$NEW'; require('fs').writeFileSync(f, JSON.stringify(j, null, 2) + '\n')"
npm --prefix card version "$NEW" --no-git-tag-version >/dev/null

git add "$MANIFEST" card/package.json card/package-lock.json custom_components/cameraui/www
git commit -q -m "release: v$NEW"
echo -e "${GREEN}Committed version bump and rebuilt bundle.${NC}"

git tag "$TAG"
echo -e "${GREEN}Created tag $TAG.${NC}"

if [ "$YES" = false ]; then
  printf "Push main + %s and cut the GitHub release? [y/N] " "$TAG"
  read -r ans
  case "$ans" in
    y | Y | yes) ;;
    *)
      git tag -d "$TAG" >/dev/null
      git reset -q --hard HEAD~1
      echo "Aborted - tag and bump commit were undone locally."
      exit 0
      ;;
  esac
fi

git push -q origin main
git push -q origin "$TAG"
gh release create "$TAG" --title "$TAG" --generate-notes
echo -e "${GREEN}Released $TAG. HACS will offer the update once it refreshes.${NC}"
