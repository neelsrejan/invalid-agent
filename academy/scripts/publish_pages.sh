#!/usr/bin/env bash
# Stage the static site plus rendered MP4s and, with --push, publish them
# on an orphan gh-pages branch. main never receives the video bytes.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

python3 academy/scripts/render_all.py
python3 academy/scripts/verify_videos.py
python3 academy/scripts/build_site.py

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
cp -a academy/site/. "$STAGE/"
mkdir -p "$STAGE/videos"
cp -a academy/build/videos/. "$STAGE/videos/"
find "$STAGE" -name '*.json' -path '*/videos/*' -delete
# Authoring keys stay off the published site.
rm -rf "$STAGE/quiz-bank" "$STAGE/content" "$STAGE/narration"

if [[ "${1:-}" != "--push" ]]; then
  trap - EXIT
  rm -rf academy/build/pages
  mkdir -p academy/build/pages
  cp -a "$STAGE"/. academy/build/pages/
  rm -rf "$STAGE"
  echo "local site: academy/build/pages (pass --push to publish gh-pages)"
  exit 0
fi

NAME="$(git config user.name || echo 'invalid-agent academy')"
EMAIL="$(git config user.email || echo 'academy@users.noreply.github.com')"
REMOTE="$(git remote get-url origin)"
git -C "$STAGE" init -q
git -C "$STAGE" checkout -q -b gh-pages
git -C "$STAGE" config user.name "$NAME"
git -C "$STAGE" config user.email "$EMAIL"
git -C "$STAGE" add -A
git -C "$STAGE" commit -q -m "Publish invalid-agent Academy"
git -C "$STAGE" push -f "$REMOTE" HEAD:gh-pages
echo "pushed gh-pages"
