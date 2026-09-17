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


def initialize_database(database_url: str | None = None) -> None:
    url = database_url or os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
    with psycopg.connect(url, autocommit=True) as connection:
        for sql_file in (PROJECT_ROOT / "db/schema.sql", PROJECT_ROOT / "db/seed.sql"):
            connection.execute(sql_file.read_text(encoding="utf-8"))
