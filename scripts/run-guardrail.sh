#!/bin/sh
# Runs guardrail.py with the first working Python 3.9+. "python3" is tried with a
# real call because on Windows it can be the Microsoft Store placeholder.
# Exit code 2 blocks the tool call when no Python is found.
for py in python3 python py; do
  if "$py" -c 'import sys; sys.exit(sys.version_info < (3, 9))' >/dev/null 2>&1; then
    exec "$py" "$(dirname "$0")/guardrail.py"
  fi
done
echo "guardrail: Python 3.9+ not found, Meta Ads tool calls are blocked" >&2
exit 2
