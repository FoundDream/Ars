#!/usr/bin/env bash
set -euo pipefail

# Validate commit messages match: {type}: {description}
# Usage: check-commit-msg.sh <base-ref> [head-ref]

PATTERN='^(feat|fix|refactor|docs|chore): .+'

base="${1:?Usage: check-commit-msg.sh <base-ref> [head-ref]}"
head="${2:-HEAD}"

commits=$(git log --format='%H %s' "$base".."$head")

if [ -z "$commits" ]; then
  echo "No commits to check."
  exit 0
fi

exit_code=0

while IFS= read -r line; do
  sha="${line%% *}"
  msg="${line#* }"

  if ! echo "$msg" | grep -qE "$PATTERN"; then
    echo "FAIL: ${sha:0:7} — $msg"
    echo "      Expected format: {type}: {description}"
    echo "      Valid types: feat, fix, refactor, docs, chore"
    exit_code=1
  else
    echo "  OK: ${sha:0:7} — $msg"
  fi
done <<< "$commits"

exit "$exit_code"
