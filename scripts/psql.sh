#!/usr/bin/env bash
# Opens a psql prompt against the scaffold's database.
#
#   ./scripts/psql.sh                                  interactive prompt
#   ./scripts/psql.sh -c 'SELECT * FROM greeting'      one-off query
#
# Uses the local psql if there is one (the interview VM has it), and otherwise
# borrows the client inside the Postgres container so this works anywhere.
set -euo pipefail
cd "$(dirname "$0")/.."

export PGPASSWORD=interview

if command -v psql >/dev/null 2>&1; then
  exec psql -h localhost -p 5432 -U interview -d interview "$@"
fi

TTY_FLAG=()
[ -t 0 ] || TTY_FLAG=(-T)
exec docker compose exec "${TTY_FLAG[@]}" -e PGPASSWORD=interview db \
  psql -U interview -d interview "$@"
