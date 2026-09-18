from pydantic import BaseModel


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
