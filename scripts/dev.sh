#!/usr/bin/env bash
# Runs Postgres, the Flask API, and the Angular dev server together.
# Ctrl-C stops the API and the frontend; the database container keeps running.
set -euo pipefail
cd "$(dirname "$0")/.."

PY=backend/.venv/bin/python
[ -x "$PY" ] || PY=backend/.venv/Scripts/python.exe
if [ ! -x "$PY" ]; then
  echo "No virtualenv found. Run ./scripts/bootstrap.sh first." >&2
  exit 1
fi

docker compose up -d db >/dev/null
for _ in $(seq 1 60); do
  docker compose exec -T db pg_isready -U interview -d interview >/dev/null 2>&1 && break
  sleep 1
done

(cd backend && "../$PY" app.py) &
API_PID=$!
trap 'kill $API_PID 2>/dev/null || true' EXIT INT TERM

# Angular serves on 0.0.0.0:3000 and proxies /api to the Flask app on :5000.
# On the interview VM, 3000 is the port published at https://<host>:8443.
cd frontend && npx ng serve
