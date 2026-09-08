# Interview scaffold â€” Angular + Flask + Postgres

A deliberately small full-stack app. Angular calls `GET /api/hello`, Flask reads
the single row from a Postgres table, and the page renders the value.

```
Angular (:3000) â”€â”€/api proxyâ”€â”€> Flask (:5000) â”€â”€SQLAlchemyâ”€â”€> Postgres (:5432)
```

**Everything already works.** Get it running, confirm you see "hello world" on
the page, and build from there.

## Running it

```bash
./scripts/bootstrap.sh   # venv, npm packages, database. Idempotent.
./scripts/dev.sh         # starts Postgres, Flask, and Angular together
```

Then open <http://localhost:3000>. On the interview VM, port 3000 is published
at `https://<host>:8443` â€” open that in a normal browser tab instead.

Ctrl-C stops Flask and Angular. The database container keeps running; stop it
with `docker compose down` (add `-v` to also wipe the data and re-seed).

## Layout

```
backend/         Flask API
  app.py           the whole API: /api/health and /api/hello
  tests/           pytest, runs against the real database
frontend/          Angular 22 app (standalone, signals, zoneless)
  src/app/app.ts   calls /api/hello and renders the result
  proxy.conf.json  routes /api to Flask so the browser stays same-origin
db/init.sql        creates and seeds the greeting table
docker-compose.yml Postgres only
```

## The data

One table, one column, one row â€” nothing more:

```sql
CREATE TABLE greeting (message TEXT NOT NULL);
INSERT INTO greeting (message) VALUES ('hello world');
```

`db/init.sql` seeds this on first boot of a fresh Postgres volume. `app.py` also
re-creates and re-seeds it at startup if it's missing, so a stale volume can't
leave you staring at an empty page.

## Database access

```bash
./scripts/psql.sh                                 # interactive prompt
./scripts/psql.sh -c 'SELECT * FROM greeting;'    # one-off query
```

On the interview VM this runs the installed `psql`. Everywhere else it falls
back to the client inside the Postgres container, so it works without a local
Postgres install either way.

Connection details, if you'd rather point your own tool at it:

| | |
|---|---|
| host / port | `localhost:5432` |
| database | `interview` |
| user / password | `interview` / `interview` |

## Tests

```bash
cd backend && .venv/bin/python -m pytest      # needs the db container up
cd frontend && npx ng test --watch=false      # vitest, no db needed
```

## Things worth knowing

- **The API is reached at `/api`, never `http://localhost:5000`, from browser
  code.** The Angular dev server proxies it. This is what makes the app work
  unchanged behind the VM's HTTPS proxy, where only port 3000 is published.
- **Both servers bind `0.0.0.0`.** On the VM, nothing reaches a process that
  listens on loopback only.
- `angular.json` sets `allowedHosts: true` so the dev server accepts the proxied
  `Host` header. Without it Vite returns "Blocked request".
- The API deliberately has no ORM models, no blueprints, and no service layer.
  Add whatever structure the exercise calls for; nothing here is precious.

## The exercise

<!-- Replace this section with the actual task before the interview. -->

_To be provided at the start of the interview._

If anything about the environment gets in your way â€” a missing package, a port
conflict, a tool you'd rather use â€” just say so. Fighting the setup is not part
of the exercise.
