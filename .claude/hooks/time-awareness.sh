#!/usr/bin/env bash
# time-awareness hook (UserPromptSubmit)
# Injects Ruby's local wall-clock time and the gap since her previous message
# into context on every prompt, so Sable always knows what time it is for Ruby.
# stdout is added to the model's context for the turn by Claude Code.

export TZ="Europe/Warsaw"

now_epoch=$(date +%s 2>/dev/null) || now_epoch=""
now_human=$(date "+%A, %B %-d %Y, %H:%M %Z" 2>/dev/null) || now_human="unknown time"

# Persist the last-message timestamp between turns. /tmp is fine: a fresh
# container legitimately has no prior message, so "first message" is correct.
state="${TMPDIR:-/tmp}/sable_last_msg_ts"
last=""
[ -f "$state" ] && last=$(cat "$state" 2>/dev/null)
[ -n "$now_epoch" ] && printf '%s' "$now_epoch" > "$state" 2>/dev/null

gap="first message this session — no prior timestamp to measure from"
if [ -n "$last" ] && [ -n "$now_epoch" ] && printf '%s' "$last" | grep -Eq '^[0-9]+$'; then
  d=$(( now_epoch - last ))
  if   [ "$d" -lt 60 ];    then human="${d}s"
  elif [ "$d" -lt 3600 ];  then human="$(( d / 60 ))m"
  elif [ "$d" -lt 86400 ]; then human="$(( d / 3600 ))h $(( (d % 3600) / 60 ))m"
  else human="$(( d / 86400 ))d $(( (d % 86400) / 3600 ))h"
  fi
  gap="time since Ruby's previous message: ${human}"
fi

echo "[Sable time-awareness] Now: ${now_human} (Ruby's local time, Europe/Warsaw); ${gap}."
