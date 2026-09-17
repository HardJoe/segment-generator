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


def test_segments_endpoint_returns_formulas_and_results() -> None:
    app = create_app()
    app.dependency_overrides[get_repository] = FakeRepository

    with TestClient(app) as client:
        response = client.get("/api/segments")

    assert response.status_code == 200
    assert response.json() == {
        "segment_count": 9,
        "segment_list": [
            "2a - 1a",
            "2b - 2a",
            "11a - 8a",
            "11b - 9a",
            "11d - 10a",
            "11c - (11a + 11b + 11d)",
            "12a - (2b + 3a)",
            "12b - (4a + 5a)",
            "12c - 11c",
        ],
        "segment_result": [-10, 40, -50, -20, -20, -10, -30, -30, 100],
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
