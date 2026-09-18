from fastapi.testclient import TestClient
from psycopg import OperationalError

from app.main import create_app, get_repository
from tests.canvas_data import supplied_canvas


class FakeRepository:
    def load_canvas(self):  # type annotation omitted to mirror a simple test double
        return supplied_canvas()

    def health_check(self) -> None:
        return None


class UnavailableRepository(FakeRepository):
    def health_check(self) -> None:
        raise OperationalError("database unavailable")


def test_root_endpoint_introduces_the_api() -> None:
    app = create_app()

    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "service": "Segment Generator API",
        "docs": "/docs",
        "health": "/health",
    }


def test_canvas_endpoint_returns_complete_canvas() -> None:
    app = create_app()
    app.dependency_overrides[get_repository] = FakeRepository

    with TestClient(app) as client:
        response = client.get("/api/canvas")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["nodes"]) == 12
    assert sum(len(node["ports"]) for node in payload["nodes"]) == 22
    assert len(payload["connections"]) == 11
    assert payload["nodes"][5]["ports"][0]["value"] is None


def test_segments_endpoint_returns_self_contained_segments() -> None:
    app = create_app()
    app.dependency_overrides[get_repository] = FakeRepository

    with TestClient(app) as client:
        response = client.get("/api/segments")

    assert response.status_code == 200
    assert response.json() == {
        "segment_count": 9,
        "segments": [
            {
                "target_port": {"id": 2, "name": "2a"},
                "source_ports": [{"id": 1, "name": "1a"}],
                "formula": "2a - 1a",
                "result": -10,
            },
            {
                "target_port": {"id": 3, "name": "2b"},
                "source_ports": [{"id": 2, "name": "2a"}],
                "formula": "2b - 2a",
                "result": 40,
            },
            {
                "target_port": {"id": 16, "name": "11a"},
                "source_ports": [{"id": 13, "name": "8a"}],
                "formula": "11a - 8a",
                "result": -50,
            },
            {
                "target_port": {"id": 17, "name": "11b"},
                "source_ports": [{"id": 14, "name": "9a"}],
                "formula": "11b - 9a",
                "result": -20,
            },
            {
                "target_port": {"id": 18, "name": "11d"},
                "source_ports": [{"id": 15, "name": "10a"}],
                "formula": "11d - 10a",
                "result": -20,
            },
            {
                "target_port": {"id": 19, "name": "11c"},
                "source_ports": [
                    {"id": 16, "name": "11a"},
                    {"id": 17, "name": "11b"},
                    {"id": 18, "name": "11d"},
                ],
                "formula": "11c - (11a + 11b + 11d)",
                "result": -10,
            },
            {
                "target_port": {"id": 20, "name": "12a"},
                "source_ports": [
                    {"id": 3, "name": "2b"},
                    {"id": 4, "name": "3a"},
                ],
                "formula": "12a - (2b + 3a)",
                "result": -30,
            },
            {
                "target_port": {"id": 21, "name": "12b"},
                "source_ports": [
                    {"id": 5, "name": "4a"},
                    {"id": 6, "name": "5a"},
                ],
                "formula": "12b - (4a + 5a)",
                "result": -30,
            },
            {
                "target_port": {"id": 22, "name": "12c"},
                "source_ports": [{"id": 19, "name": "11c"}],
                "formula": "12c - 11c",
                "result": 100,
            },
        ],
    }


def test_health_endpoint_reports_database_readiness() -> None:
    app = create_app()
    app.dependency_overrides[get_repository] = FakeRepository

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_endpoint_returns_service_unavailable_for_database_failure() -> None:
    app = create_app()
    app.dependency_overrides[get_repository] = UnavailableRepository

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == {"detail": "database unavailable"}
