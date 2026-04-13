.PHONY: lint check-commit-msg check-skill-frontmatter check-readme-sync

BASE ?= main

lint: check-skill-frontmatter check-readme-sync

lint-all: check-commit-msg check-skill-frontmatter check-readme-sync

check-commit-msg:
	@echo "==> Checking commit messages..."
	@bash scripts/check-commit-msg.sh $(BASE)

check-skill-frontmatter:
	@echo "==> Checking SKILL.md frontmatter..."
	@bash scripts/check-skill-frontmatter.sh

check-readme-sync:
	@echo "==> Checking README sync..."
	@bash scripts/check-readme-sync.sh
