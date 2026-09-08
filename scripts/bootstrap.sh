#!/usr/bin/env bash
# Idempotent setup: Python venv, npm packages, database up and seeded.
# Safe to re-run. The interview VM runs this automatically at boot.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Python dependencies"
python3 -m venv backend/.venv 2>/dev/null || python -m venv backend/.venv
PY=backend/.venv/bin/python
[ -x "$PY" ] || PY=backend/.venv/Scripts/python.exe
"$PY" -m pip install --quiet --upgrade pip
"$PY" -m pip install --quiet -r backend/requirements.txt

echo "==> Node dependencies"
if [ -f frontend/package-lock.json ]; then
  (cd frontend && npm ci --no-audit --no-fund)
else
  (cd frontend && npm install --no-audit --no-fund)
fi

echo "==> Database"
docker compose up -d db
for _ in $(seq 1 60); do
  if docker compose exec -T db pg_isready -U interview -d interview >/dev/null 2>&1; then
    echo "    postgres is ready"
    break
  fi
  sleep 1
done

echo
echo "Bootstrap complete. Start everything with: ./scripts/dev.sh"
