"""Flask API for the interview exercise.

Deliberately small: one module, one endpoint that reads one row. Add structure
(blueprints, an ORM layer, services) as the exercise pushes you to -- there is
nothing here you need to preserve.
"""

from __future__ import annotations

import os

from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError

DEFAULT_DATABASE_URL = "postgresql+psycopg://interview:interview@localhost:5432/interview"


def build_engine(database_url: str) -> Engine:
    # pool_pre_ping keeps the dev server from handing out connections that
    # Postgres dropped while the container was restarting.
    return create_engine(database_url, pool_pre_ping=True, future=True)


def ensure_schema(engine: Engine) -> None:
    """Create and seed the greeting table if it isn't there yet.

    db/init.sql already does this, but only on a fresh Postgres volume. This
    makes the app self-healing if someone reuses an older volume.
    """
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS greeting (message TEXT NOT NULL)"))
        already_seeded = conn.execute(text("SELECT EXISTS (SELECT 1 FROM greeting)")).scalar()
        if not already_seeded:
            conn.execute(text("INSERT INTO greeting (message) VALUES (:message)"), {"message": "hello world"})


def create_app(database_url: str | None = None) -> Flask:
    app = Flask(__name__)
    app.config["DATABASE_URL"] = database_url or os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)

    # The Angular dev server proxies /api, so same-origin covers normal use.
    # CORS is here only so hitting the API directly on :5000 also works.
    CORS(app)

    engine = build_engine(app.config["DATABASE_URL"])
    app.extensions["engine"] = engine

    @app.get("/api/health")
    def health():
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except SQLAlchemyError as exc:
            app.logger.warning("health check failed: %s", exc)
            return jsonify(status="degraded", database="unreachable"), 503
        return jsonify(status="ok", database="ok")

    @app.get("/api/hello")
    def hello():
        try:
            with engine.connect() as conn:
                message = conn.execute(text("SELECT message FROM greeting LIMIT 1")).scalar_one_or_none()
        except SQLAlchemyError as exc:
            app.logger.exception("could not read greeting")
            return jsonify(error="database unavailable", detail=str(exc)), 503

        if message is None:
            return jsonify(error="no greeting has been seeded"), 404

        return jsonify(message=message)

    return app


app = create_app()

if __name__ == "__main__":
    # 0.0.0.0 matters on the interview VM: the Angular dev server proxies to
    # this process, and nothing reaches it if it binds loopback only.
    ensure_schema(app.extensions["engine"])
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
