#!/usr/bin/env bash
set -euo pipefail

# Validate all SKILL.md files have required frontmatter fields: name, description, version
# Usage: check-skill-frontmatter.sh

REQUIRED_FIELDS=("name" "description" "version")

exit_code=0

while IFS= read -r file; do
  # Extract frontmatter between --- delimiters
  frontmatter=$(sed -n '/^---$/,/^---$/p' "$file" | sed '1d;$d')

  if [ -z "$frontmatter" ]; then
    echo "FAIL: $file — missing frontmatter"
    exit_code=1
    continue
  fi

  missing=()
  for field in "${REQUIRED_FIELDS[@]}"; do
    if [ "$field" = "version" ]; then
      # version is nested under metadata
      if ! echo "$frontmatter" | grep -qE '^\s+version:'; then
        missing+=("metadata.version")
      fi
    else
      if ! echo "$frontmatter" | grep -qE "^${field}:"; then
        missing+=("$field")
      fi
    fi
  done

  if [ ${#missing[@]} -gt 0 ]; then
    echo "FAIL: $file — missing fields: ${missing[*]}"
    exit_code=1
  else
    echo "  OK: $file"
  fi
done < <(find skills awesome-skills -name "SKILL.md" 2>/dev/null)

if [ "$exit_code" -eq 0 ]; then
  echo "All SKILL.md files have valid frontmatter."
fi

exit "$exit_code"
