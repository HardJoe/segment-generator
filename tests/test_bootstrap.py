from pathlib import Path

from app import database


class FakeResult:
    def __init__(self, value: bool) -> None:
        self._value = value

    def fetchone(self) -> tuple[bool]:
        return (self._value,)


class FakeConnection:
    def __init__(self, is_empty: bool) -> None:
        self.is_empty = is_empty
        self.statements: list[str] = []

    def execute(self, statement: str) -> FakeResult:
        self.statements.append(statement)
        if statement == "SELECT NOT EXISTS (SELECT 1 FROM nodes)":
            return FakeResult(self.is_empty)
        return FakeResult(False)

    def __enter__(self) -> "FakeConnection":
        return self

    def __exit__(self, *_: object) -> None:
        return None


def _bootstrap_with_connection(monkeypatch, connection: FakeConnection) -> None:
    monkeypatch.setattr(
        database.psycopg,
        "connect",
        lambda *_args, **_kwargs: connection,
    )
    database.bootstrap_database("postgresql://example")


def test_bootstrap_applies_schema_and_seeds_an_empty_database(monkeypatch) -> None:
    connection = FakeConnection(is_empty=True)

    _bootstrap_with_connection(monkeypatch, connection)

    schema = (database.PROJECT_ROOT / "db/schema.sql").read_text(encoding="utf-8")
    seed = (database.PROJECT_ROOT / "db/seed.sql").read_text(encoding="utf-8")
    assert schema in connection.statements
    assert seed in connection.statements
    assert connection.statements.index(schema) < connection.statements.index(seed)


def test_bootstrap_does_not_reseed_a_populated_database(monkeypatch) -> None:
    connection = FakeConnection(is_empty=False)

    _bootstrap_with_connection(monkeypatch, connection)

    seed = (database.PROJECT_ROOT / "db/seed.sql").read_text(encoding="utf-8")
    assert seed not in connection.statements


def test_schema_file_remains_idempotent() -> None:
    schema_path = Path(database.PROJECT_ROOT / "db/schema.sql")

    assert schema_path.read_text(encoding="utf-8").count("CREATE TABLE IF NOT EXISTS") == 3
