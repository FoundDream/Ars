#!/bin/bash
# Claude Code Status Line
# Displays: model | context progress bar | rate limits
# Requires: jq (brew install jq)

input=$(cat)

# --- Model ---
MODEL=$(echo "$input" | jq -r '.model.display_name')

# --- Context Window ---
PCT=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)

BAR_WIDTH=15
FILLED=$((PCT * BAR_WIDTH / 100))
EMPTY=$((BAR_WIDTH - FILLED))
BAR=""
[ "$FILLED" -gt 0 ] && printf -v FILL "%${FILLED}s" && BAR="${FILL// /▓}"
[ "$EMPTY" -gt 0 ] && printf -v PAD "%${EMPTY}s" && BAR="${BAR}${PAD// /░}"

# Color: green < 60%, yellow < 85%, red >= 85%
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
DIM='\033[2m'
RESET='\033[0m'

if [ "$PCT" -ge 85 ]; then
  BAR_COLOR="$RED"
elif [ "$PCT" -ge 60 ]; then
  BAR_COLOR="$YELLOW"
else
  BAR_COLOR="$GREEN"
fi

# --- Rate Limits ---
RATE_5H=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
RATE_5H_RESET=$(echo "$input" | jq -r '.rate_limits.five_hour.resets_at // empty')
RATE_7D=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')
RATE_7D_RESET=$(echo "$input" | jq -r '.rate_limits.seven_day.resets_at // empty')

# Format reset time as HH:MM
format_reset() {
  local ts="$1"
  if [ -n "$ts" ]; then
    date -r "$ts" '+%H:%M' 2>/dev/null || date -d "@$ts" '+%H:%M' 2>/dev/null
  fi
}

RATE_INFO=""
if [ -n "$RATE_5H" ]; then
  RATE_5H_INT=$(echo "$RATE_5H" | cut -d. -f1)
  RESET_TIME=$(format_reset "$RATE_5H_RESET")
  RESET_LABEL=""
  [ -n "$RESET_TIME" ] && RESET_LABEL="@${RESET_TIME}"
  if [ "$RATE_5H_INT" -ge 80 ]; then
    RATE_INFO="${RED}5h:${RATE_5H_INT}%${RESET_LABEL}${RESET}"
  else
    RATE_INFO="${DIM}5h:${RATE_5H_INT}%${RESET_LABEL}${RESET}"
  fi
fi

if [ -n "$RATE_7D" ]; then
  RATE_7D_INT=$(echo "$RATE_7D" | cut -d. -f1)
  RESET_TIME=$(format_reset "$RATE_7D_RESET")
  RESET_LABEL=""
  [ -n "$RESET_TIME" ] && RESET_LABEL="@${RESET_TIME}"
  if [ "$RATE_7D_INT" -ge 80 ]; then
    RATE_INFO="${RATE_INFO} ${RED}7d:${RATE_7D_INT}%${RESET_LABEL}${RESET}"
  else
    RATE_INFO="${RATE_INFO} ${DIM}7d:${RATE_7D_INT}%${RESET_LABEL}${RESET}"
  fi
fi

# --- Output ---
LINE="[$MODEL] ${BAR_COLOR}${BAR}${RESET} ${PCT}%"
[ -n "$RATE_INFO" ] && LINE="${LINE} | ${RATE_INFO}"

echo -e "$LINE"
