from fastapi import Depends, FastAPI, HTTPException, status
from psycopg import Error as PsycopgError

from app.database import (
    CanvasRepository,
    PostgresCanvasRepository,
)
from app.domain import Canvas
from app.segments import SegmentGenerator


def get_repository() -> CanvasRepository:
    return PostgresCanvasRepository()


def serialize_canvas(canvas: Canvas) -> dict[str, list[dict[str, object]]]:
    ports_by_node: dict[int, list[dict[str, object]]] = {
        node.id: [] for node in canvas.nodes
    }
    for port in canvas.ports:
        ports_by_node[port.node_id].append(
            {"id": port.id, "name": port.name, "value": port.value}
        )

    ports_by_id = {port.id: port for port in canvas.ports}
    return {
        "nodes": [
            {
                "id": node.id,
                "name": node.name,
                "ports": ports_by_node[node.id],
            }
            for node in canvas.nodes
        ],
        "connections": [
            {
                "id": connection.id,
                "source_port_id": connection.source_port_id,
                "source_port": ports_by_id[connection.source_port_id].name,
                "target_port_id": connection.target_port_id,
                "target_port": ports_by_id[connection.target_port_id].name,
            }
            for connection in canvas.connections
        ],
    }


def create_app() -> FastAPI:
    application = FastAPI(title="Segment Generator")

    @application.get("/health")
    def get_health(
        repository: CanvasRepository = Depends(get_repository),
    ) -> dict[str, str]:
        try:
            repository.health_check()
        except PsycopgError as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="database unavailable",
            ) from error
        return {"status": "ok"}

    @application.get("/api/canvas")
    def get_canvas(
        repository: CanvasRepository = Depends(get_repository),
    ) -> dict[str, list[dict[str, object]]]:
        return serialize_canvas(repository.load_canvas())

    @application.get("/api/segments")
    def get_segments(
        repository: CanvasRepository = Depends(get_repository),
    ) -> dict[str, int | list[str] | list[int]]:
        segments = SegmentGenerator(repository.load_canvas()).generate()
        return {
            "segment_count": len(segments),
            "segment_list": [segment.formula for segment in segments],
            "segment_result": [segment.result for segment in segments],
        }

    return application


app = create_app()
