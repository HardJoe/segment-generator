from pydantic import BaseModel


class RootResponse(BaseModel):
    service: str
    docs: str
    health: str


class HealthResponse(BaseModel):
    status: str


class CanvasPortResponse(BaseModel):
    id: int
    name: str
    value: int | None


class CanvasNodeResponse(BaseModel):
    id: int
    name: str
    ports: list[CanvasPortResponse]


class CanvasConnectionResponse(BaseModel):
    id: int
    source_port_id: int
    source_port: str
    target_port_id: int
    target_port: str


class CanvasResponse(BaseModel):
    nodes: list[CanvasNodeResponse]
    connections: list[CanvasConnectionResponse]


class PortReferenceResponse(BaseModel):
    id: int
    name: str


class SegmentResponse(BaseModel):
    target_port: PortReferenceResponse
    source_ports: list[PortReferenceResponse]
    formula: str
    result: int


class SegmentsResponse(BaseModel):
    segment_count: int
    segments: list[SegmentResponse]
