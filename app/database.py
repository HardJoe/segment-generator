import os
from pathlib import Path
from typing import Protocol

import psycopg
from psycopg.rows import dict_row

from app.domain import Canvas, Connection, Node, Port


DEFAULT_DATABASE_URL = (
    "postgresql://segment:segment@localhost:5432/segment_generator"
)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class CanvasRepository(Protocol):
    def load_canvas(self) -> Canvas: ...

    def health_check(self) -> None: ...


class PostgresCanvasRepository:
    def __init__(self, database_url: str | None = None) -> None:
        self._database_url = database_url or os.getenv(
            "DATABASE_URL", DEFAULT_DATABASE_URL
        )

    def load_canvas(self) -> Canvas:
        with psycopg.connect(self._database_url, row_factory=dict_row) as connection:
            nodes = tuple(
                Node(**row)
                for row in connection.execute(
                    "SELECT id, name FROM nodes ORDER BY id"
                ).fetchall()
            )
            ports = tuple(
                Port(**row)
                for row in connection.execute(
                    "SELECT id, node_id, name, value FROM ports ORDER BY id"
                ).fetchall()
            )
            connections = tuple(
                Connection(**row)
                for row in connection.execute(
                    """
                    SELECT id, source_port_id, target_port_id
                    FROM connections
                    ORDER BY id
                    """
                ).fetchall()
            )
        return Canvas(nodes=nodes, ports=ports, connections=connections)

    def health_check(self) -> None:
        with psycopg.connect(self._database_url) as connection:
            connection.execute("SELECT 1")


def bootstrap_database(database_url: str | None = None) -> None:
    """Apply the schema and seed the supplied demo graph only on an empty database."""
    url = database_url or os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
    with psycopg.connect(url, autocommit=True) as connection:
        schema_file = PROJECT_ROOT / "db/schema.sql"
        seed_file = PROJECT_ROOT / "db/seed.sql"
        connection.execute(schema_file.read_text(encoding="utf-8"))

        # The deployed free-tier service uses one instance.  The advisory lock also
        # keeps a manual bootstrap or a future second instance from double-seeding.
        connection.execute("SELECT pg_advisory_lock(8142901)")
        try:
            is_empty = connection.execute(
                "SELECT NOT EXISTS (SELECT 1 FROM nodes)"
            ).fetchone()[0]
            if is_empty:
                connection.execute(seed_file.read_text(encoding="utf-8"))
        finally:
            connection.execute("SELECT pg_advisory_unlock(8142901)")


def initialize_database(database_url: str | None = None) -> None:
    """Backward-compatible alias for the deployment bootstrap command."""
    bootstrap_database(database_url)
