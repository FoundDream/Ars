#!/usr/bin/env bash
set -euo pipefail

# Validate every skill directory has a corresponding entry in its parent README
# Usage: check-readme-sync.sh

exit_code=0

check_dir() {
  local base_dir="$1"
  local readme="$base_dir/README.md"

  if [ ! -f "$readme" ]; then
    echo "FAIL: $readme does not exist"
    exit_code=1
    return
  fi

  for skill_dir in "$base_dir"/*/; do
    [ -d "$skill_dir" ] || continue

    skill_name=$(basename "$skill_dir")

    # Skip hidden directories
    [[ "$skill_name" == .* ]] && continue

    if ! grep -q "\[$skill_name\]" "$readme"; then
      echo "FAIL: $skill_name is missing from $readme"
      exit_code=1
    else
      echo "  OK: $skill_name found in $readme"
    fi
  done
}

[ -d "skills" ] && check_dir "skills"
[ -d "awesome-skills" ] && check_dir "awesome-skills"

if [ "$exit_code" -eq 0 ]; then
  echo "All skills are documented in their README."
fi

exit "$exit_code"
