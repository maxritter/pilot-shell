#!/bin/bash
# Pilot Bot heartbeat context check script
# Outputs current state for Claude to evaluate

BOT_DIR="${PILOT_BOT_DIR:-$HOME/.pilot/bot}"
LOCK="$BOT_DIR/.heartbeat-lock"
NOW=$(date +%s)

# Lock file dedup: skip if last check was within 1350s (75% of 30min interval)
if [ -f "$LOCK" ] && [ $((NOW - $(cat "$LOCK"))) -lt 1350 ]; then
    echo "SKIP: heartbeat ran recently"
    exit 0
fi
echo "$NOW" > "$LOCK"

echo "=== PILOT BOT HEARTBEAT: $(date '+%Y-%m-%d %H:%M') ==="
echo ""

# Check JOBS.yaml for active jobs
echo "--- Active Jobs ---"
if [ -f "$BOT_DIR/JOBS.yaml" ]; then
    grep -c "active: true" "$BOT_DIR/JOBS.yaml" 2>/dev/null || echo "0"
    echo "jobs configured"
else
    echo "(no JOBS.yaml)"
fi
echo ""

# Check bot PID
echo "--- Bot Process ---"
if [ -f "$BOT_DIR/.bot-pid" ]; then
    PID=$(cat "$BOT_DIR/.bot-pid")
    if kill -0 "$PID" 2>/dev/null; then
        echo "Running (PID: $PID)"
    else
        echo "WARNING: PID file exists but process $PID is dead"
    fi
else
    echo "WARNING: No PID file"
fi
echo ""

echo "=== END CHECK ==="
