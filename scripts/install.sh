#!/usr/bin/env bash
set -euo pipefail

DESTINATION="${1:-$HOME/.codex/skills}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILL_ROOT="$REPO_ROOT/skills"

if [[ ! -d "$SKILL_ROOT" ]]; then
  echo "Cannot find skills directory: $SKILL_ROOT" >&2
  exit 1
fi

mkdir -p "$DESTINATION"

for skill in "$SKILL_ROOT"/*; do
  [[ -d "$skill" ]] || continue
  name="$(basename "$skill")"
  target="$DESTINATION/$name"
  rm -rf "$target"
  cp -R "$skill" "$target"
  echo "Installed $name -> $target"
done

echo
echo "Done. Restart Codex to pick up the installed skills."
