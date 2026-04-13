# Claude Code Status Line

A minimal status line for [Claude Code](https://claude.ai/code) that displays model, context window usage, and rate limits.

```
[Opus] ▓▓▓░░░░░░░░░░░░ 18% | 5h:23% 7d:41%
```

## Features

- Model name
- Context window progress bar with color coding (green → yellow → red)
- Rate limit usage (5-hour and 7-day windows, highlighted when > 80%)

## Requirements

- [jq](https://jqlang.github.io/jq/) — `brew install jq`

## Install

1. Copy the script to `~/.claude/`:

```bash
cp statusline.sh ~/.claude/statusline.sh
chmod +x ~/.claude/statusline.sh
```

2. Add to `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh"
  }
}
```

## Color Thresholds

| Context Usage | Color |
|---------------|-------|
| < 60% | Green |
| 60–84% | Yellow |
| >= 85% | Red |

Rate limits turn red when usage exceeds 80%.
