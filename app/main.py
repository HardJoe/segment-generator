from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.openapi.utils import get_openapi
from psycopg import Error as PsycopgError

from app.database import (
    CanvasRepository,
    PostgresCanvasRepository,
)
from app.domain import Canvas
from app.schemas import (
    CanvasResponse,
    HealthResponse,
    PortReferenceResponse,
    RootResponse,
    SegmentResponse,
    SegmentsResponse,
)
from app.segments import SegmentGenerator


def get_repository() -> CanvasRepository:
    return PostgresCanvasRepository()


ROOT_RESPONSE_EXAMPLE = {
    "service": "Segment Generator API",
    "docs": "/docs",
    "health": "/health",
}

HEALTH_RESPONSE_EXAMPLE = {"status": "ok"}

CANVAS_RESPONSE_EXAMPLE = {
    "nodes": [
        {"id": 1, "name": "1", "ports": [{"id": 1, "name": "1a", "value": 100}]},
        {
            "id": 2,
            "name": "2",
            "ports": [
                {"id": 2, "name": "2a", "value": 90},
                {"id": 3, "name": "2b", "value": 130},
            ],
        },
        {"id": 3, "name": "3", "ports": [{"id": 4, "name": "3a", "value": 150}]},
        {"id": 4, "name": "4", "ports": [{"id": 5, "name": "4a", "value": 70}]},
        {"id": 5, "name": "5", "ports": [{"id": 6, "name": "5a", "value": 160}]},
        {
            "id": 6,
            "name": "6",
            "ports": [
                {"id": 7, "name": "6a", "value": None},
                {"id": 8, "name": "6b", "value": None},
                {"id": 9, "name": "6c", "value": None},
            ],
        },
        {
            "id": 7,
            "name": "7",
            "ports": [
                {"id": 10, "name": "7a", "value": None},
                {"id": 11, "name": "7b", "value": None},
                {"id": 12, "name": "7c", "value": None},
            ],
        },
        {"id": 8, "name": "8", "ports": [{"id": 13, "name": "8a", "value": 200}]},
        {"id": 9, "name": "9", "ports": [{"id": 14, "name": "9a", "value": 120}]},
        {"id": 10, "name": "10", "ports": [{"id": 15, "name": "10a", "value": 80}]},
        {
            "id": 11,
            "name": "11",
            "ports": [
                {"id": 16, "name": "11a", "value": 150},
                {"id": 17, "name": "11b", "value": 100},
                {"id": 18, "name": "11d", "value": 60},
                {"id": 19, "name": "11c", "value": 300},
            ],
        },
        {
            "id": 12,
            "name": "12",
            "ports": [
                {"id": 20, "name": "12a", "value": 250},
                {"id": 21, "name": "12b", "value": 200},
                {"id": 22, "name": "12c", "value": 400},
            ],
        },
    ],
    "connections": [
        {"id": 1, "source_port_id": 1, "source_port": "1a", "target_port_id": 2, "target_port": "2a"},
        {"id": 2, "source_port_id": 3, "source_port": "2b", "target_port_id": 8, "target_port": "6b"},
        {"id": 3, "source_port_id": 4, "source_port": "3a", "target_port_id": 7, "target_port": "6a"},
        {"id": 4, "source_port_id": 9, "source_port": "6c", "target_port_id": 20, "target_port": "12a"},
        {"id": 5, "source_port_id": 5, "source_port": "4a", "target_port_id": 10, "target_port": "7a"},
        {"id": 6, "source_port_id": 6, "source_port": "5a", "target_port_id": 11, "target_port": "7b"},
        {"id": 7, "source_port_id": 12, "source_port": "7c", "target_port_id": 21, "target_port": "12b"},
        {"id": 8, "source_port_id": 13, "source_port": "8a", "target_port_id": 16, "target_port": "11a"},
        {"id": 9, "source_port_id": 14, "source_port": "9a", "target_port_id": 17, "target_port": "11b"},
        {"id": 10, "source_port_id": 15, "source_port": "10a", "target_port_id": 18, "target_port": "11d"},
        {"id": 11, "source_port_id": 19, "source_port": "11c", "target_port_id": 22, "target_port": "12c"},
    ],
}


def serialize_canvas(canvas: Canvas) -> CanvasResponse:
    ports_by_node: dict[int, list[dict[str, object]]] = {
        node.id: [] for node in canvas.nodes
    }
    for port in canvas.ports:
        ports_by_node[port.node_id].append(
            {"id": port.id, "name": port.name, "value": port.value}
        )

    ports_by_id = {port.id: port for port in canvas.ports}
    return CanvasResponse(
        nodes=[
            {
                "id": node.id,
                "name": node.name,
                "ports": ports_by_node[node.id],
            }
            for node in canvas.nodes
        ],
        connections=[
            {
                "id": connection.id,
                "source_port_id": connection.source_port_id,
                "source_port": ports_by_id[connection.source_port_id].name,
                "target_port_id": connection.target_port_id,
                "target_port": ports_by_id[connection.target_port_id].name,
            }
            for connection in canvas.connections
        ],
    )


def create_app() -> FastAPI:
    application = FastAPI(title="Segment Generator")

    @application.get(
        "/",
        response_model=RootResponse,
        responses={200: {"content": {"application/json": {"example": ROOT_RESPONSE_EXAMPLE}}}},
    )
    def get_root() -> RootResponse:
        return RootResponse(**ROOT_RESPONSE_EXAMPLE)

    @application.get(
        "/health",
        response_model=HealthResponse,
        responses={
            200: {"content": {"application/json": {"example": HEALTH_RESPONSE_EXAMPLE}}},
            503: {
                "description": "Database unavailable",
                "content": {"application/json": {"example": {"detail": "database unavailable"}}},
            },
        },
    )
    def get_health(
        repository: CanvasRepository = Depends(get_repository),
    ) -> HealthResponse:
        try:
            repository.health_check()
        except PsycopgError as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="database unavailable",
            ) from error
        return HealthResponse(**HEALTH_RESPONSE_EXAMPLE)

    @application.get(
        "/api/canvas",
        response_model=CanvasResponse,
        responses={200: {"content": {"application/json": {"example": CANVAS_RESPONSE_EXAMPLE}}}},
    )
    def get_canvas(
        repository: CanvasRepository = Depends(get_repository),
    ) -> CanvasResponse:
        return serialize_canvas(repository.load_canvas())

    @application.get("/api/segments", response_model=SegmentsResponse)
    def get_segments(
        repository: CanvasRepository = Depends(get_repository),
    ) -> SegmentsResponse:
        segments = SegmentGenerator(repository.load_canvas()).generate()
        return SegmentsResponse(
            segment_count=len(segments),
            segments=[
                SegmentResponse(
                    target_port=PortReferenceResponse(
                        id=segment.target.id,
                        name=segment.target.name,
                    ),
                    source_ports=[
                        PortReferenceResponse(id=source.id, name=source.name)
                        for source in segment.sources
                    ],
                    formula=segment.formula,
                    result=segment.result,
                )
                for segment in segments
            ],
        )

    def custom_openapi() -> dict[str, object]:
        if application.openapi_schema:
            return application.openapi_schema

        openapi_schema = get_openapi(
            title=application.title,
            version=application.version,
            routes=application.routes,
        )
        response_examples = {
            "/": ROOT_RESPONSE_EXAMPLE,
            "/health": HEALTH_RESPONSE_EXAMPLE,
            "/api/canvas": CANVAS_RESPONSE_EXAMPLE,
        }
        for path, example in response_examples.items():
            openapi_schema["paths"][path]["get"]["responses"]["200"]["content"][
                "application/json"
            ]["example"] = example

        application.openapi_schema = openapi_schema
        return application.openapi_schema

    application.openapi = custom_openapi
    return application


app = create_app()
