---
name: commit
description: "Invoke when committing code changes. Stages only files the agent created or modified, writes a concise commit message. Not for pushing or creating PRs."
metadata:
  version: "1.0.0"
---

# Commit: Stage Your Own Work and Commit

## Format

`{type}: {description}` — one short sentence, lowercase, no period, explain *why* not *what*

types: `feat`, `fix`, `refactor`, `docs`, `chore`

## Atomic Commits

One commit = one purpose, describable in a single sentence.

- Group related files — a skill's SKILL.md and its references/ belong in one commit
- Split unrelated changes — two independent features = two commits
- If the message needs "and" to connect two different things, split it

## Hard Rules

- Only stage files you created or modified — never `git add .` or `git add -A`
- No `--no-verify` or `--amend` unless explicitly asked
- No push unless explicitly asked
- Do not commit files that may contain secrets (.env, credentials, tokens)
